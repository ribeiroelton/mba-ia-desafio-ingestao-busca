"""
Framework de avaliação LLM usando LLM-as-a-Judge pattern.

Avalia qualidade de respostas LLM usando um segundo LLM avaliador.
"""
import json
import os
from typing import Dict, Optional
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from tests.utils.evaluation_criteria import RagEvaluationCriteria


@dataclass
class EvaluationResult:
    """Resultado de uma avaliação LLM."""
    score: int  # 0-100
    criteria_scores: Dict[str, int]  # Scores por critério
    feedback: str  # Feedback detalhado
    passed: bool  # Se passou no threshold
    details: Dict[str, str]  # Detalhes por critério
    
    @property
    def overall_score(self) -> int:
        """Alias para score (compatibilidade)."""
        return self.score


class LLMEvaluator:
    """
    Avaliador de qualidade de respostas LLM usando LLM-as-a-Judge pattern.
    
    Usa um segundo LLM para avaliar objetivamente se a resposta:
    - Segue SYSTEM_PROMPT rigorosamente
    - Está baseada exclusivamente no contexto
    - Não contém alucinações
    - É clara, objetiva e direta
    
    Example:
        >>> evaluator = LLMEvaluator(threshold=70)
        >>> result = evaluator.evaluate(
        ...     question="Qual o faturamento?",
        ...     context="Faturamento de R$10M",
        ...     response="O faturamento é de R$10M"
        ... )
        >>> assert result.passed
        >>> print(result.score)
        85
    """
    
    EVALUATOR_SYSTEM_PROMPT = """Você é um avaliador especializado em validar respostas de sistemas RAG.

MISSÃO: Avaliar se a RESPOSTA do assistente segue rigorosamente as regras e está baseada exclusivamente no CONTEXTO fornecido.

CRITÉRIOS DE AVALIAÇÃO (cada um vale 0-100 pontos):

1. ADERÊNCIA AO CONTEXTO (30 pontos)
   - Resposta baseada EXCLUSIVAMENTE no contexto fornecido?
   - Nenhuma informação externa ou conhecimento geral usado?
   - Fatos mencionados podem ser rastreados ao contexto?
   
   ✓ EXEMPLOS DE BOAS RESPOSTAS:
     • Resposta cita trecho exato do contexto
     • Resposta sintetiza informações presentes no contexto
     • Resposta admite falta de informação quando contexto insuficiente
   
   ✗ EXEMPLOS DE MÁS RESPOSTAS:
     • Resposta inclui fatos não presentes no contexto
     • Resposta usa conhecimento geral externo
     • Resposta extrapola além do contexto

2. DETECÇÃO DE ALUCINAÇÃO (30 pontos)
   - Resposta NÃO inventa ou infere informações?
   - Resposta NÃO extrapola além do escrito?
   - Se info não disponível, usa mensagem padrão?
   
   ✓ EXEMPLOS DE BOAS RESPOSTAS:
     • Resposta afirma apenas fatos rastreáveis ao contexto
     • Resposta não cria números ou estatísticas não mencionadas
     • Resposta não cria detalhes não mencionados
   
   ✗ EXEMPLOS DE MÁS RESPOSTAS:
     • Resposta inventa estatísticas não presentes
     • Resposta adiciona nomes ou datas não mencionados
     • Resposta infere causas não explícitas

3. SEGUIMENTO DE REGRAS (25 pontos)
   - Segue regra de responder "Não tenho informações necessárias" quando apropriado?
   - NÃO produz opiniões ou interpretações além do texto?
   - NÃO usa conhecimento externo?
   
   ✓ EXEMPLOS DE BOAS RESPOSTAS:
     • Usa mensagem padrão quando informação não disponível
     • Não produz opiniões ou interpretações
     • Não usa conhecimento externo
   
   ✗ EXEMPLOS DE MÁS RESPOSTAS:
     • Responde com conhecimento geral quando contexto insuficiente
     • Produz opiniões pessoais
     • Ignora restrições do SYSTEM_PROMPT

4. CLAREZA E OBJETIVIDADE (15 pontos)
   - Resposta é clara e direta?
   - Resposta é objetiva sem enrolação?
   - Resposta responde a pergunta de forma completa?
   
   ✓ EXEMPLOS DE BOAS RESPOSTAS:
     • Resposta é direta e clara
     • Resposta é objetiva sem enrolação
     • Resposta responde completamente a pergunta
   
   ✗ EXEMPLOS DE MÁS RESPOSTAS:
     • Resposta é confusa ou ambígua
     • Resposta tem enrolação desnecessária
     • Resposta não responde a pergunta adequadamente

FORMATO DE SAÍDA:
Retorne APENAS um JSON válido com esta estrutura exata:
{
    "adherence_to_context": <0-100>,
    "hallucination_detection": <0-100>,
    "rule_following": <0-100>,
    "clarity_objectivity": <0-100>,
    "overall_score": <média ponderada>,
    "feedback": "<análise detalhada em português>",
    "passed": <true se overall_score >= 70, false caso contrário>
}

IMPORTANTE:
- Seja rigoroso: prefira scores baixos se houver dúvida
- Feedback deve explicar EXATAMENTE o que está bom e o que está ruim
- Se detectar alucinação, score de hallucination_detection deve ser 0
- Se usar conhecimento externo, score de adherence_to_context deve ser 0
"""
    
    def __init__(self, threshold: int = 70, model: str = "gpt-5-nano"):
        """
        Inicializa avaliador LLM.
        
        Args:
            threshold: Score mínimo para passar (0-100)
            model: Modelo OpenAI para avaliação (padrão: gpt-5-nano)
        """
        self.threshold = threshold
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,  # Determinístico
        )
    
    def evaluate(
        self,
        question: str,
        context: str,
        response: str,
        system_prompt: Optional[str] = None
    ) -> EvaluationResult:
        """
        Avalia qualidade de uma resposta LLM.
        
        Args:
            question: Pergunta do usuário
            context: Contexto fornecido ao LLM
            response: Resposta gerada pelo LLM
            system_prompt: SYSTEM_PROMPT usado (opcional)
            
        Returns:
            EvaluationResult com scores e feedback
            
        Raises:
            ValueError: Se avaliação falhar ou JSON inválido
            
        Example:
            >>> evaluator = LLMEvaluator()
            >>> result = evaluator.evaluate(
            ...     question="Quantos funcionários?",
            ...     context="A empresa tem 50 funcionários",
            ...     response="A empresa tem 50 funcionários"
            ... )
            >>> assert result.passed
        """
        # Montar prompt de avaliação
        evaluation_prompt = self.build_evaluation_prompt(
            question=question,
            context=context,
            response=response,
            system_prompt=system_prompt
        )
        
        # Enviar para LLM avaliador
        messages = [
            SystemMessage(content=self.EVALUATOR_SYSTEM_PROMPT),
            HumanMessage(content=evaluation_prompt)
        ]
        
        try:
            llm_response = self.llm.invoke(messages)
            response_text = llm_response.content
            
            # Parsear resposta JSON
            evaluation_data = self._parse_evaluation_response(response_text)
            
            # Criar EvaluationResult
            result = self._build_evaluation_result(evaluation_data)
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Avaliador retornou JSON inválido: {e}\n"
                f"Resposta raw: {llm_response.content}"
            )
        except Exception as e:
            raise ValueError(f"Erro ao avaliar resposta: {e}")
    
    def build_evaluation_prompt(
        self,
        question: str,
        context: str,
        response: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Monta prompt para avaliação.
        
        Args:
            question: Pergunta do usuário
            context: Contexto fornecido
            response: Resposta do LLM
            system_prompt: SYSTEM_PROMPT usado
            
        Returns:
            Prompt formatado para avaliação
        """
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"SYSTEM_PROMPT DO ASSISTENTE:\n{system_prompt}\n")
        
        prompt_parts.extend([
            "CONTEXTO FORNECIDO AO ASSISTENTE:",
            context,
            "",
            "PERGUNTA DO USUÁRIO:",
            question,
            "",
            "RESPOSTA DO ASSISTENTE:",
            response,
            "",
            "AVALIE A RESPOSTA DO ASSISTENTE SEGUINDO OS CRITÉRIOS."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_evaluation_response(self, response_text: str) -> Dict:
        """
        Parseia resposta JSON do avaliador.
        
        Args:
            response_text: Texto da resposta do LLM
            
        Returns:
            Dict com dados de avaliação
            
        Raises:
            json.JSONDecodeError: Se JSON inválido
        """
        # Tentar extrair JSON do texto (pode ter markdown)
        text = response_text.strip()
        
        # Remover markdown code blocks se presentes
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Tentar parsear JSON normalmente primeiro
        try:
            return json.loads(text, strict=False)
        except json.JSONDecodeError:
            # Se falhar, tentar corrigir problemas comuns com feedback
            # Escapar aspas dentro do campo feedback
            import re
            # Encontrar o campo feedback e escapar aspas dentro dele
            pattern = r'"feedback":\s*"([^"]*(?:"[^"]*)*)"'
            
            def escape_feedback(match):
                feedback_content = match.group(1)
                # Escapar apenas aspas que não são de fechamento do JSON
                escaped = feedback_content.replace('\n', ' ').replace('\r', '')
                return f'"feedback": "{escaped}"'
            
            text_fixed = re.sub(pattern, escape_feedback, text, flags=re.DOTALL)
            return json.loads(text_fixed, strict=False)
    
    def _build_evaluation_result(self, data: Dict) -> EvaluationResult:
        """
        Constrói EvaluationResult a partir dos dados.
        
        Args:
            data: Dict com dados de avaliação
            
        Returns:
            EvaluationResult estruturado
        """
        criteria_scores = {
            "adherence_to_context": data.get("adherence_to_context", 0),
            "hallucination_detection": data.get("hallucination_detection", 0),
            "rule_following": data.get("rule_following", 0),
            "clarity_objectivity": data.get("clarity_objectivity", 0),
        }
        
        # Calcular score ponderado se não fornecido
        overall_score = data.get("overall_score")
        if overall_score is None:
            overall_score = RagEvaluationCriteria.calculate_weighted_score(criteria_scores)
        
        # Determinar se passou
        passed = data.get("passed")
        if passed is None:
            passed = overall_score >= self.threshold
        
        return EvaluationResult(
            score=int(overall_score),
            criteria_scores=criteria_scores,
            feedback=data.get("feedback", ""),
            passed=bool(passed),
            details={}  # Pode ser expandido no futuro
        )
    
    @staticmethod
    def get_failing_criterion_guidance(evaluation_result: EvaluationResult, threshold: int = 70) -> str:
        """
        Retorna guia com exemplos dos critérios que falharam.
        
        Útil para debug e correção de respostas que falharam na avaliação.
        
        Args:
            evaluation_result: Resultado de uma avaliação
            threshold: Score mínimo considerado de sucesso (padrão: 70)
            
        Returns:
            Texto formatado com exemplos dos critérios que falharam
            
        Example:
            >>> result = evaluator.evaluate(question, context, response)
            >>> if not result.passed:
            ...     guidance = LLMEvaluator.get_failing_criterion_guidance(result)
            ...     print(guidance)
        """
        failing_criteria = []
        
        # Identificar critérios que falharam
        for criterion_name, score in evaluation_result.criteria_scores.items():
            if score < threshold:
                failing_criteria.append((criterion_name, score))
        
        if not failing_criteria:
            return "✓ Nenhum critério falhou!"
        
        # Ordenar por score (pior primeiro)
        failing_criteria.sort(key=lambda x: x[1])
        
        lines = []
        lines.append(f"⚠️ CRITÉRIOS COM FALHA (score < {threshold}):\n")
        
        for criterion_name, score in failing_criteria:
            lines.append(f"{'='*60}")
            lines.append(f"Score: {score}/100\n")
            
            try:
                examples_text = RagEvaluationCriteria.get_criteria_examples_text(criterion_name)
                lines.append(examples_text)
            except ValueError:
                lines.append(f"Critério '{criterion_name}' não encontrado")
            
            lines.append("")
        
        lines.append(f"{'='*60}")
        lines.append(f"\n📌 Feedback da Avaliação:")
        lines.append(evaluation_result.feedback)
        
        return "\n".join(lines)
