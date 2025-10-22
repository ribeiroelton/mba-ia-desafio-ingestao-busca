"""
Critérios de avaliação estruturados para respostas LLM.

Define critérios reutilizáveis específicos para sistemas RAG.
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EvaluationCriterion:
    """Critério de avaliação para respostas LLM."""
    name: str
    weight: float  # 0.0-1.0
    description: str
    examples_good: List[str]
    examples_bad: List[str]


class RagEvaluationCriteria:
    """Critérios de avaliação específicos para sistemas RAG."""
    
    ADHERENCE_TO_CONTEXT = EvaluationCriterion(
        name="adherence_to_context",
        weight=0.30,
        description="Resposta baseada exclusivamente no contexto fornecido",
        examples_good=[
            "Resposta cita trecho exato do contexto",
            "Resposta sintetiza informações presentes no contexto",
            "Resposta admite falta de informação quando contexto insuficiente"
        ],
        examples_bad=[
            "Resposta inclui fatos não presentes no contexto",
            "Resposta usa conhecimento geral externo",
            "Resposta extrapola além do contexto"
        ]
    )
    
    HALLUCINATION_DETECTION = EvaluationCriterion(
        name="hallucination_detection",
        weight=0.30,
        description="Detecção de alucinações e informações inventadas",
        examples_good=[
            "Resposta afirma apenas fatos rastreáveis ao contexto",
            "Resposta não cria números ou estatísticas não mencionadas",
            "Resposta não cria detalhes não mencionados"
        ],
        examples_bad=[
            "Resposta inventa estatísticas não presentes",
            "Resposta adiciona nomes ou datas não mencionados",
            "Resposta infere causas não explícitas"
        ]
    )
    
    RULE_FOLLOWING = EvaluationCriterion(
        name="rule_following",
        weight=0.25,
        description="Seguimento rigoroso do SYSTEM_PROMPT",
        examples_good=[
            "Usa mensagem padrão quando informação não disponível",
            "Não produz opiniões ou interpretações",
            "Não usa conhecimento externo"
        ],
        examples_bad=[
            "Responde com conhecimento geral quando contexto insuficiente",
            "Produz opiniões pessoais",
            "Ignora restrições do SYSTEM_PROMPT"
        ]
    )
    
    CLARITY_OBJECTIVITY = EvaluationCriterion(
        name="clarity_objectivity",
        weight=0.15,
        description="Clareza e objetividade da resposta",
        examples_good=[
            "Resposta é direta e clara",
            "Resposta é objetiva sem enrolação",
            "Resposta responde completamente a pergunta"
        ],
        examples_bad=[
            "Resposta é confusa ou ambígua",
            "Resposta tem enrolação desnecessária",
            "Resposta não responde a pergunta adequadamente"
        ]
    )
    
    @classmethod
    def get_all_criteria(cls) -> List[EvaluationCriterion]:
        """Retorna todos os critérios de avaliação."""
        return [
            cls.ADHERENCE_TO_CONTEXT,
            cls.HALLUCINATION_DETECTION,
            cls.RULE_FOLLOWING,
            cls.CLARITY_OBJECTIVITY,
        ]
    
    @classmethod
    def get_criteria_examples_text(cls, criterion_name: str) -> str:
        """
        Formata exemplos de boas e más respostas para um critério.
        
        Útil para incluir em prompts do LLM e documentação.
        
        Args:
            criterion_name: Nome do critério (ex: "adherence_to_context")
            
        Returns:
            Texto formatado com exemplos bons e ruins
            
        Raises:
            ValueError: Se critério não existe
            
        Example:
            >>> text = RagEvaluationCriteria.get_criteria_examples_text("adherence_to_context")
            >>> assert "BOM:" in text
            >>> assert "RUIM:" in text
        """
        # Encontrar critério
        criteria = cls.get_all_criteria()
        criterion = None
        for c in criteria:
            if c.name == criterion_name:
                criterion = c
                break
        
        if criterion is None:
            raise ValueError(f"Critério '{criterion_name}' não encontrado")
        
        # Formatar exemplos
        lines = []
        lines.append(f"CRITÉRIO: {criterion.name.upper()}")
        lines.append(f"Peso: {int(criterion.weight * 100)}%")
        lines.append(f"Descrição: {criterion.description}")
        lines.append("")
        
        # Exemplos bons
        lines.append("✓ EXEMPLOS DE RESPOSTAS BOM:")
        for example in criterion.examples_good:
            lines.append(f"  • {example}")
        lines.append("")
        
        # Exemplos ruins
        lines.append("✗ EXEMPLOS DE RESPOSTAS RUIM:")
        for example in criterion.examples_bad:
            lines.append(f"  • {example}")
        
        return "\n".join(lines)
    
    @classmethod
    def calculate_weighted_score(cls, scores: Dict[str, int]) -> int:
        """
        Calcula score ponderado baseado nos critérios.
        
        Args:
            scores: Dict com scores por critério (0-100)
            
        Returns:
            Score total ponderado (0-100)
            
        Example:
            >>> scores = {
            ...     "adherence_to_context": 80,
            ...     "hallucination_detection": 90,
            ...     "rule_following": 85,
            ...     "clarity_objectivity": 75,
            ... }
            >>> RagEvaluationCriteria.calculate_weighted_score(scores)
            83
        """
        criteria = cls.get_all_criteria()
        total_score = 0.0
        
        for criterion in criteria:
            score = scores.get(criterion.name, 0)
            total_score += score * criterion.weight
        
        return int(round(total_score))
