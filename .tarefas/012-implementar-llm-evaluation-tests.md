# [012] - Implementar LLM Evaluation Tests para Testes de Integração

## Metadados
- **ID**: 012
- **Grupo**: Fase 3 - Qualidade e Documentação
- **Prioridade**: Alta
- **Complexidade**: Alta
- **Estimativa**: 2-3 dias
- **Dependências**: Tarefa 011 (Otimizar suite de testes)

## Descrição

Implementar framework de avaliação automatizada de qualidade de outputs de LLM nos testes de integração, permitindo aferir objetivamente se as respostas geradas atendem aos requisitos de negócio, seguem o SYSTEM_PROMPT e mantêm qualidade consistente.

Atualmente, os testes de integração validam apenas aspectos estruturais das respostas (tipo, tamanho, presença de strings específicas), mas não avaliam qualitativamente se:
- A resposta está realmente baseada no contexto fornecido
- O conteúdo da resposta é factualmente correto em relação aos chunks recuperados
- A resposta segue rigorosamente o SYSTEM_PROMPT (RN-001 a RN-004)
- A resposta é clara, objetiva e direta
- A resposta não contém alucinações ou informações inventadas

Esta tarefa implementa **LLM-as-a-Judge** pattern, onde um segundo LLM avalia a qualidade das respostas do LLM principal, criando uma camada de validação automatizada e objetiva.

## Requisitos

### Requisitos Funcionais

- **RF-012-001**: Implementar avaliador LLM que analisa resposta vs contexto vs pergunta
- **RF-012-002**: Avaliar aderência ao SYSTEM_PROMPT (RN-001 a RN-004)
- **RF-012-003**: Avaliar factualidade da resposta em relação ao contexto
- **RF-012-004**: Avaliar clareza e objetividade da resposta
- **RF-012-005**: Detectar alucinações (informações não presentes no contexto)
- **RF-012-006**: Gerar score numérico de qualidade (0-100)
- **RF-012-007**: Gerar feedback detalhado sobre pontos fortes e fracos
- **RF-012-008**: Suportar diferentes critérios de avaliação por tipo de teste

### Requisitos Não-Funcionais

- **RNF-012-001**: Avaliações devem ser determinísticas (temperature=0)
- **RNF-012-002**: Custo de avaliação deve ser mínimo (usar modelo econômico)
- **RNF-012-003**: Testes devem falhar com score < 70/100
- **RNF-012-004**: Feedback deve ser acionável para debug
- **RNF-012-005**: Framework deve ser reutilizável para novos testes

## Fonte da Informação

### Referências ao Contexto de Desenvolvimento
- **Seção 2.4**: Regras de Negócio RN-001 a RN-006
- **Seção 4.1**: UC-003 - Validar Resposta Baseada em Contexto
- **Arquivo**: `src/chat.py` - SYSTEM_PROMPT e ask_llm()
- **Arquivo**: `tests/integration/test_real_scenarios.py` - Testes atuais

### Regras de Negócio Relacionadas
- **RN-001**: Respostas exclusivamente baseadas no contexto recuperado
- **RN-002**: Mensagem padrão quando informação não disponível
- **RN-003**: Nunca inventar informações ou usar conhecimento externo
- **RN-004**: Nunca produzir opiniões ou interpretações além do escrito

### Literatura e Padrões
- **LLM-as-a-Judge Pattern**: Usar LLM para avaliar outputs de outro LLM
- **G-Eval Framework**: Framework de avaliação com critérios estruturados
- **RAGAS Framework**: RAG Assessment com métricas específicas (Faithfulness, Answer Relevancy)

## Stack Necessária

- **Linguagem**: Python 3.13.9
- **Framework de Testes**: pytest 8.3.4
- **LLM Provider**: OpenAI (gpt-5-nano para avaliação)
- **Bibliotecas Adicionais**:
  - `langchain-openai`: 0.3.35 (já instalada)
  - `pydantic`: 2.12.3 (já instalada - validação de estruturas)
- **Ferramentas**:
  - pytest fixtures existentes
  - Docker (PostgreSQL + pgVector)

## Dependências

### Dependências Técnicas
- **Tarefa 011**: Suite de testes otimizada deve estar funcional
- **Tarefa 007**: Integração e validação de contexto implementada
- **Tarefa 008**: Testes de integração base implementados
- **Infraestrutura**: Docker Compose rodando (Tarefa 001)
- **Ambiente**: Python configurado com todas as dependências (Tarefa 003)

### Dependências de Negócio
- **Aprovação**: Critérios de qualidade mínima aceitos (score >= 70)
- **Budget**: Aprovação de custos adicionais de API (avaliações com gpt-5-nano)

## Critérios de Aceite

1. [ ] Framework de avaliação LLM implementado e funcional
2. [ ] Avaliador analisa aderência a SYSTEM_PROMPT (RN-001 a RN-004)
3. [ ] Avaliador detecta alucinações e informações inventadas
4. [ ] Avaliador verifica factualidade em relação ao contexto
5. [ ] Scores numéricos gerados (0-100) para cada critério
6. [ ] Feedback textual detalhado gerado para debug
7. [ ] Testes falham automaticamente com score < 70
8. [ ] Todos os testes existentes em `test_real_scenarios.py` integrados com avaliação
9. [ ] Pelo menos 3 novos cenários de teste implementados com avaliação
10. [ ] Documentação completa do framework em docstrings
11. [ ] Exemplos de uso no código de testes
12. [ ] Custos de avaliação documentados (chamadas API extras)

## Implementação Resumida

### Estrutura de Arquivos

```
tests/
├── integration/
│   ├── test_real_scenarios.py          # Atualizado com avaliações
│   ├── test_llm_quality_evaluation.py  # Novos testes focados em qualidade
│   └── __init__.py
├── utils/
│   ├── __init__.py
│   ├── llm_evaluator.py                # Framework de avaliação (NOVO)
│   └── evaluation_criteria.py         # Critérios de avaliação (NOVO)
└── conftest.py                         # Fixture para avaliador
```

### Componentes a Implementar

#### 1. Framework de Avaliação LLM
**Arquivo**: `tests/utils/llm_evaluator.py`
**Responsabilidade**: Avaliar qualidade de respostas LLM usando LLM-as-a-Judge

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os


@dataclass
class EvaluationResult:
    """Resultado de uma avaliação LLM."""
    score: int  # 0-100
    criteria_scores: Dict[str, int]  # Scores por critério
    feedback: str  # Feedback detalhado
    passed: bool  # Se passou no threshold
    details: Dict[str, str]  # Detalhes por critério


class LLMEvaluator:
    """
    Avaliador de qualidade de respostas LLM usando LLM-as-a-Judge pattern.
    
    Usa um segundo LLM para avaliar objetivamente se a resposta:
    - Segue SYSTEM_PROMPT rigorosamente
    - Está baseada exclusivamente no contexto
    - Não contém alucinações
    - É clara, objetiva e direta
    """
    
    EVALUATOR_SYSTEM_PROMPT = """Você é um avaliador especializado em validar respostas de sistemas RAG.

MISSÃO: Avaliar se a RESPOSTA do assistente segue rigorosamente as regras e está baseada exclusivamente no CONTEXTO fornecido.

CRITÉRIOS DE AVALIAÇÃO (cada um vale 0-100 pontos):

1. ADERÊNCIA AO CONTEXTO (30 pontos)
   - Resposta baseada EXCLUSIVAMENTE no contexto fornecido?
   - Nenhuma informação externa ou conhecimento geral usado?
   - Fatos mencionados podem ser rastreados ao contexto?

2. DETECÇÃO DE ALUCINAÇÃO (30 pontos)
   - Resposta NÃO inventa ou infere informações?
   - Resposta NÃO extrapola além do escrito?
   - Se info não disponível, usa mensagem padrão?

3. SEGUIMENTO DE REGRAS (25 pontos)
   - Segue regra de responder "Não tenho informações necessárias" quando apropriado?
   - NÃO produz opiniões ou interpretações além do texto?
   - NÃO usa conhecimento externo?

4. CLAREZA E OBJETIVIDADE (15 pontos)
   - Resposta é clara e direta?
   - Resposta é objetiva sem enrolação?
   - Resposta responde a pergunta de forma completa?

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
- Seja rigoroso: prefer scores baixos se houver dúvida
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
            context: Contexto recuperado do vectorstore
            response: Resposta gerada pelo LLM
            system_prompt: SYSTEM_PROMPT usado (opcional)
            
        Returns:
            EvaluationResult com scores e feedback
            
        Raises:
            ValueError: Se avaliação falhar
        """
        # Implementar lógica de avaliação
        # 1. Montar prompt de avaliação com question, context, response
        # 2. Enviar para LLM avaliador
        # 3. Parsear resposta JSON
        # 4. Calcular scores
        # 5. Retornar EvaluationResult
        pass
    
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
            context: Contexto recuperado
            response: Resposta do LLM
            system_prompt: SYSTEM_PROMPT usado
            
        Returns:
            Prompt formatado para avaliação
        """
        prompt_parts = [
            "CONTEXTO FORNECIDO AO ASSISTENTE:",
            f"{context}",
            "",
            "PERGUNTA DO USUÁRIO:",
            f"{question}",
            "",
            "RESPOSTA DO ASSISTENTE:",
            f"{response}",
            "",
        ]
        
        if system_prompt:
            prompt_parts.insert(0, f"SYSTEM_PROMPT DO ASSISTENTE:\n{system_prompt}\n")
        
        prompt_parts.append("AVALIE A RESPOSTA DO ASSISTENTE SEGUINDO OS CRITÉRIOS.")
        
        return "\n".join(prompt_parts)
```

#### 2. Critérios de Avaliação Estruturados
**Arquivo**: `tests/utils/evaluation_criteria.py`
**Responsabilidade**: Definir critérios de avaliação reutilizáveis

```python
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
            "Resposta sintetiza múltiplos trechos do contexto",
            "Resposta admite falta de informação quando contexto insuficiente"
        ],
        examples_bad=[
            "Resposta inclui fatos não presentes no contexto",
            "Resposta usa conhecimento geral não fornecido",
            "Resposta extrapola além do contexto"
        ]
    )
    
    HALLUCINATION_DETECTION = EvaluationCriterion(
        name="hallucination_detection",
        weight=0.30,
        description="Detecção de alucinações e informações inventadas",
        examples_good=[
            "Resposta afirma apenas fatos rastreáveis ao contexto",
            "Resposta não inventa números ou datas",
            "Resposta não cria detalhes não mencionados"
        ],
        examples_bad=[
            "Resposta inventa estatísticas não presentes",
            "Resposta cria detalhes plausíveis mas falsos",
            "Resposta infere causas não explícitas"
        ]
    )
    
    RULE_FOLLOWING = EvaluationCriterion(
        name="rule_following",
        weight=0.25,
        description="Seguimento rigoroso do SYSTEM_PROMPT",
        examples_good=[
            "Usa mensagem padrão quando informação não disponível",
            "Não produz opiniões além do contexto",
            "Não usa conhecimento externo"
        ],
        examples_bad=[
            "Responde mesmo sem contexto suficiente",
            "Oferece opinião além do texto",
            "Complementa com conhecimento geral"
        ]
    )
    
    CLARITY_OBJECTIVITY = EvaluationCriterion(
        name="clarity_objectivity",
        weight=0.15,
        description="Clareza e objetividade da resposta",
        examples_good=[
            "Resposta clara e direta",
            "Resposta completa e estruturada",
            "Resposta objetiva sem enrolação"
        ],
        examples_bad=[
            "Resposta vaga ou ambígua",
            "Resposta incompleta",
            "Resposta prolíxica ou repetitiva"
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
    def calculate_weighted_score(cls, scores: Dict[str, int]) -> int:
        """
        Calcula score total ponderado.
        
        Args:
            scores: Dict com scores por critério {criterion_name: score}
            
        Returns:
            Score total ponderado (0-100)
        """
        total_score = 0.0
        for criterion in cls.get_all_criteria():
            if criterion.name in scores:
                total_score += scores[criterion.name] * criterion.weight
        
        return int(round(total_score))
```

#### 3. Fixture Pytest para Avaliador
**Arquivo**: `tests/conftest.py` (adicionar)
**Responsabilidade**: Fornecer fixture reutilizável

```python
# Adicionar ao arquivo conftest.py existente

import pytest
from tests.utils.llm_evaluator import LLMEvaluator


@pytest.fixture(scope="session")
def llm_evaluator():
    """
    Fixture para avaliador LLM.
    
    Escopo: session - reutilizado em todos os testes.
    """
    return LLMEvaluator(threshold=70, model="gpt-5-nano")
```

#### 4. Integração com Testes Existentes
**Arquivo**: `tests/integration/test_real_scenarios.py` (atualizar)
**Responsabilidade**: Adicionar avaliação LLM aos testes existentes

```python
# Adicionar ao início do arquivo
from tests.utils.llm_evaluator import LLMEvaluator
from src.chat import SYSTEM_PROMPT


def test_scenario_llm_follows_system_prompt_with_evaluation(
    real_scenario_collection, 
    llm_evaluator
):
    """
    Cenário: Validar que LLM segue SYSTEM_PROMPT rigorosamente.
    
    Agora com AVALIAÇÃO LLM de qualidade.
    
    Este teste é crítico para validar RN-002 e RN-003.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Perguntas claramente fora do contexto
    out_of_context_questions = [
        "Quem foi o primeiro presidente dos Estados Unidos?",
        "Como fazer um bolo de chocolate?",
        "Qual é a fórmula da água?",
    ]
    
    for question in out_of_context_questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        
        # Validação estrutural (existente)
        assert "Não tenho informações necessárias" in response, \
            f"LLM não seguiu SYSTEM_PROMPT para: {question}"
        
        # NOVA: Avaliação qualitativa com LLM
        evaluation = llm_evaluator.evaluate(
            question=question,
            context=context,
            response=response,
            system_prompt=SYSTEM_PROMPT
        )
        
        # Assertions baseadas em avaliação
        assert evaluation.passed, \
            f"Avaliação LLM falhou (score: {evaluation.score}/100)\n" \
            f"Feedback: {evaluation.feedback}\n" \
            f"Detalhes: {evaluation.details}"
        
        # Critérios específicos para este cenário
        assert evaluation.criteria_scores["rule_following"] >= 80, \
            f"Score de rule_following muito baixo: {evaluation.criteria_scores['rule_following']}"
        
        assert evaluation.criteria_scores["hallucination_detection"] >= 90, \
            f"Score de hallucination_detection muito baixo: {evaluation.criteria_scores['hallucination_detection']}"


def test_scenario_ambiguous_question_with_evaluation(
    real_scenario_collection,
    llm_evaluator
):
    """
    Cenário: Pergunta ambígua com AVALIAÇÃO LLM.
    
    Valida que LLM interpreta adequadamente ou admite necessidade de clareza.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Me fale sobre isso"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural
    assert len(response) > 0
    assert isinstance(response, str)
    
    # NOVA: Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para pergunta ambígua, esperamos:
    # - Alta aderência ao contexto
    # - Clareza pode ser menor (pergunta é ambígua)
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        f"Mesmo com pergunta ambígua, deve aderir ao contexto"
    
    # Score geral pode ser mais baixo (clareza prejudicada)
    # mas não deve alucinar
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        f"Não deve alucinar mesmo com pergunta ambígua"
```

#### 5. Novos Testes Focados em Qualidade
**Arquivo**: `tests/integration/test_llm_quality_evaluation.py` (NOVO)
**Responsabilidade**: Testes específicos de qualidade LLM

```python
"""
Testes de qualidade de outputs LLM usando LLM-as-a-Judge.

Valida aspectos qualitativos das respostas que vão além de validações estruturais.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT
from tests.utils.llm_evaluator import LLMEvaluator


@pytest.fixture(scope="module")
def quality_test_collection(sample_pdf_path, shared_test_collection):
    """Setup para testes de qualidade."""
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    yield shared_test_collection


def test_response_factual_accuracy(quality_test_collection, llm_evaluator):
    """
    Testa precisão factual da resposta em relação ao contexto.
    
    Cenário: Pergunta específica sobre fato presente no documento.
    Expected: Resposta factualmente correta com score alto de aderência.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta específica que deve ter resposta factual
    question = "Quais são os principais tópicos mencionados no documento?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions de qualidade
    assert evaluation.passed, \
        f"Resposta não passou em avaliação de qualidade\n{evaluation.feedback}"
    
    # Para resposta factual, esperamos:
    assert evaluation.criteria_scores["adherence_to_context"] >= 80, \
        "Aderência ao contexto deve ser alta para resposta factual"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 85, \
        "Não deve haver alucinação em resposta factual"
    
    assert evaluation.criteria_scores["clarity_objectivity"] >= 75, \
        "Resposta factual deve ser clara e objetiva"


def test_response_with_no_context_match(quality_test_collection, llm_evaluator):
    """
    Testa comportamento quando pergunta não tem contexto relevante.
    
    Cenário: Pergunta fora do domínio do documento.
    Expected: Mensagem padrão com score alto de rule_following.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta claramente fora do contexto
    question = "Qual é a receita para fazer um bolo de cenoura?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Deve usar mensagem padrão
    assert "Não tenho informações necessárias" in response
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para mensagem padrão correta, esperamos:
    assert evaluation.criteria_scores["rule_following"] >= 90, \
        "Deve seguir regra de mensagem padrão perfeitamente"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 95, \
        "Não deve alucinar quando não há contexto"
    
    # Score geral deve ser alto (comportamento correto)
    assert evaluation.overall_score >= 85, \
        "Mensagem padrão correta deve ter score alto"


def test_response_completeness(quality_test_collection, llm_evaluator):
    """
    Testa completude da resposta para pergunta ampla.
    
    Cenário: Pergunta que requer sintetizar múltiplos chunks.
    Expected: Resposta completa com score alto de clareza.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta ampla que deve usar múltiplos chunks
    question = "Faça um resumo completo do documento"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural básica
    assert len(response) > 100, "Resumo deve ser substantivo"
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para resumo completo, esperamos:
    assert evaluation.criteria_scores["adherence_to_context"] >= 75, \
        "Resumo deve ser baseado no contexto"
    
    assert evaluation.criteria_scores["clarity_objectivity"] >= 80, \
        "Resumo deve ser claro e bem estruturado"
    
    assert evaluation.overall_score >= 70, \
        f"Resumo deve passar no threshold\n{evaluation.feedback}"


def test_response_consistency_across_similar_questions(
    quality_test_collection,
    llm_evaluator
):
    """
    Testa consistência de respostas para perguntas similares.
    
    Cenário: Múltiplas perguntas similares sobre mesmo tópico.
    Expected: Scores de qualidade consistentes entre respostas.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Perguntas similares
    similar_questions = [
        "Qual é o tema principal do documento?",
        "Sobre o que trata o documento?",
        "Qual é o assunto central discutido?",
    ]
    
    evaluations = []
    
    for question in similar_questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        
        evaluation = llm_evaluator.evaluate(
            question=question,
            context=context,
            response=response,
            system_prompt=SYSTEM_PROMPT
        )
        
        evaluations.append(evaluation)
    
    # Todas devem passar
    for i, evaluation in enumerate(evaluations):
        assert evaluation.passed, \
            f"Pergunta {i+1} falhou: {similar_questions[i]}\n{evaluation.feedback}"
    
    # Scores devem ser consistentes (variação < 20 pontos)
    scores = [e.overall_score for e in evaluations]
    score_variance = max(scores) - min(scores)
    
    assert score_variance < 20, \
        f"Scores muito inconsistentes entre perguntas similares: {scores}"


def test_evaluation_cost_tracking(quality_test_collection, llm_evaluator):
    """
    Testa e documenta custos de avaliação.
    
    Cenário: Executar múltiplas avaliações e estimar custo.
    Expected: Custos documentados para planejamento.
    
    Nota: Este teste não falha, apenas reporta informações.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "Teste de custo"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Executar avaliação
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Documentar informações de custo
    print("\n" + "="*60)
    print("INFORMAÇÕES DE CUSTO DE AVALIAÇÃO")
    print("="*60)
    print(f"Modelo de avaliação: gpt-5-nano")
    print(f"Tokens estimados por avaliação: ~1500-2000")
    print(f"Custo estimado por avaliação: ~$0.0001-0.0002")
    print(f"Custo estimado para 50 avaliações: ~$0.005-0.010")
    print("="*60)
    
    # Teste sempre passa (apenas informativo)
    assert True
```

### Regras de Negócio a Implementar

- **RN-001**: Validar aderência exclusiva ao contexto via critério `adherence_to_context`
- **RN-002**: Validar mensagem padrão via critério `rule_following`
- **RN-003**: Validar ausência de conhecimento externo via `adherence_to_context` e `hallucination_detection`
- **RN-004**: Validar objetividade via critério `clarity_objectivity`

### Validações Necessárias

1. **Validação de Score Threshold**:
   - Score < 70: Teste deve falhar
   - Score >= 70: Teste deve passar
   - Feedback deve ser claro sobre motivo do score

2. **Validação de Formato de Resposta do Avaliador**:
   - Resposta deve ser JSON válido
   - Todos os campos obrigatórios presentes
   - Scores devem estar no range 0-100

3. **Validação de Determinismo**:
   - Temperature=0 para avaliações
   - Mesma pergunta/contexto/resposta deve gerar score similar

4. **Validação de Custo**:
   - Documentar número de chamadas API
   - Estimar custo total de execução da suite

### Tratamento de Erros

1. **Erro na Chamada API do Avaliador**:
   - Capturar exceção
   - Registrar erro detalhado
   - Falhar teste com mensagem clara

2. **Erro no Parse de JSON do Avaliador**:
   - Capturar exceção
   - Mostrar resposta raw do avaliador
   - Falhar teste indicando formato inválido

3. **Timeout na Avaliação**:
   - Definir timeout razoável (30s)
   - Falhar teste com mensagem de timeout

4. **API Key Inválida**:
   - Validar API key antes de executar testes
   - Mensagem clara sobre configuração

## Testes de Qualidade e Cobertura (Obrigatório)

### Testes Unitários
**Arquivo**: `tests/unit/test_llm_evaluator_unit.py` (NOVO)
**Cobertura Mínima**: 80%

**Cenários a Testar**:

1. **Teste de Inicialização**:
   - Input: LLMEvaluator(threshold=70)
   - Expected: Instância configurada corretamente

2. **Teste de Build Prompt**:
   - Input: question, context, response
   - Expected: Prompt formatado corretamente

3. **Teste de Parse de Resposta JSON Válida**:
   - Input: JSON válido do avaliador
   - Expected: EvaluationResult correto

4. **Teste de Parse de Resposta JSON Inválida**:
   - Input: JSON malformado
   - Expected: ValueError com mensagem clara

5. **Teste de Cálculo de Score Ponderado**:
   - Input: {criterion: score} dict
   - Expected: Score total correto

### Testes de Integração
**Arquivo**: `tests/integration/test_llm_quality_evaluation.py` (já documentado acima)

**Cenários Principais**:
1. Resposta factualmente correta
2. Resposta com mensagem padrão correta
3. Resumo completo de documento
4. Consistência entre perguntas similares
5. Tracking de custos

### Testes de Performance
**Opcional - Documentar apenas**

**Métrica**: Tempo de execução de avaliação < 5s por avaliação
**Cenário**: Executar 10 avaliações e medir tempo médio

### Testes de Segurança
**Verificação**: API Key não exposta em logs ou outputs
**Ferramenta**: Inspeção manual de outputs de testes

## Documentação Necessária (Obrigatório)

### Código
- [x] Docstrings completas em todas as funções/classes
- [x] Comentários explicando lógica de avaliação
- [x] Exemplos de uso inline

### README Técnico
**Arquivo**: `tests/README.md` (atualizar)

Adicionar seção:

```markdown
## LLM Evaluation Tests

### Visão Geral
Framework de avaliação automatizada de qualidade de outputs de LLM usando **LLM-as-a-Judge** pattern.

### Como Funciona
1. LLM principal gera resposta baseada em contexto
2. LLM avaliador analisa qualidade da resposta
3. Scores numéricos (0-100) gerados por critério
4. Teste passa se score >= 70

### Critérios de Avaliação
- **Aderência ao Contexto** (30%): Resposta baseada exclusivamente no contexto
- **Detecção de Alucinação** (30%): Ausência de informações inventadas
- **Seguimento de Regras** (25%): Aderência ao SYSTEM_PROMPT
- **Clareza e Objetividade** (15%): Qualidade da comunicação

### Uso
```python
from tests.utils.llm_evaluator import LLMEvaluator

evaluator = LLMEvaluator(threshold=70)
evaluation = evaluator.evaluate(
    question="Pergunta do usuário",
    context="Contexto recuperado",
    response="Resposta do LLM"
)

assert evaluation.passed, f"Score: {evaluation.score}\n{evaluation.feedback}"
```

### Custos
- Modelo: gpt-5-nano
- Custo por avaliação: ~$0.0001-0.0002
- Custo para suite completa: ~$0.01

### Configuração
- Threshold padrão: 70/100
- Pode ser ajustado por teste específico
```

### Documentação de API
- [x] Docstrings seguindo formato Google/NumPy
- [x] Type hints em todas as assinaturas
- [x] Exemplos de uso em docstrings

## Checklist de Finalização

- [ ] Framework `LLMEvaluator` implementado em `tests/utils/llm_evaluator.py`
- [ ] Critérios de avaliação em `tests/utils/evaluation_criteria.py`
- [ ] Fixture `llm_evaluator` adicionada em `tests/conftest.py`
- [ ] Todos os testes em `test_real_scenarios.py` integrados com avaliação
- [ ] Arquivo `test_llm_quality_evaluation.py` criado com novos testes
- [ ] Pelo menos 3 novos cenários de teste implementados
- [ ] Testes unitários do avaliador em `test_llm_evaluator_unit.py`
- [ ] Todos os testes passando (score >= 70)
- [ ] Cobertura de código >= 80% nos novos módulos
- [ ] Documentação em `tests/README.md` atualizada
- [ ] Docstrings completas em todos os novos módulos
- [ ] Custos de API documentados
- [ ] Code review realizado
- [ ] Build passa sem erros
- [ ] Linting passa sem warnings

## Notas Adicionais

### Considerações de Implementação

1. **Modelo para Avaliação**:
   - Usar `gpt-5-nano` para manter consistência e reduzir custos
   - Temperature=0 para determinismo
   - Pode ser substituído por modelo mais barato se necessário

2. **Parsing de JSON**:
   - LLM pode não retornar JSON perfeito sempre
   - Implementar parsing robusto com fallbacks
   - Usar `json.loads()` com tratamento de exceção

3. **Feedback Acionável**:
   - Feedback do avaliador deve ser detalhado
   - Deve apontar exatamente onde está o problema
   - Deve sugerir o que melhorar

4. **Threshold Configurável**:
   - 70 é padrão razoável
   - Alguns testes podem precisar threshold maior (ex: 80 para mensagem padrão)
   - Alguns testes podem aceitar menor (ex: 60 para perguntas ambíguas)

5. **Performance**:
   - Avaliação adiciona ~2-3s por teste
   - Suite completa pode levar +2-3 minutos
   - Considerar executar avaliações apenas em CI/CD

### Armadilhas Conhecidas

1. **Custo Acumulado**:
   - Cada avaliação = 1 chamada API extra
   - Suite com 50 testes = 50 chamadas extras
   - Monitorar custos em uso contínuo

2. **Variabilidade do LLM Avaliador**:
   - Mesmo com temperature=0, LLM pode variar levemente
   - Implementar margem de tolerância em comparações
   - Não confiar 100% em scores absolutos

3. **Contexto Muito Longo**:
   - Contexto + resposta + prompt de avaliação pode exceder limites
   - Implementar truncagem se necessário
   - Documentar limitação

4. **Falsos Positivos/Negativos**:
   - LLM avaliador pode errar
   - Sempre revisar manualmente testes que falharam
   - Ajustar critérios se necessário

### Melhorias Futuras

1. **Cache de Avaliações**:
   - Implementar cache de avaliações para economizar
   - Usar hash de (question, context, response) como chave

2. **Benchmark Dataset**:
   - Criar dataset de referência com avaliações manuais
   - Validar qualidade do avaliador LLM

3. **Múltiplos Avaliadores**:
   - Usar múltiplos LLMs avaliadores e fazer ensemble
   - Aumentar confiabilidade das avaliações

4. **Fine-tuning de Avaliador**:
   - Fine-tune modelo específico para avaliação RAG
   - Reduzir custos e aumentar precisão

## Referências

### Documentação Externa
- **LangChain Evaluation**: https://python.langchain.com/docs/guides/evaluation/
- **OpenAI Evals**: https://github.com/openai/evals
- **RAGAS Framework**: https://docs.ragas.io/en/stable/
- **G-Eval Paper**: https://arxiv.org/abs/2303.16634
- **LLM-as-a-Judge**: https://arxiv.org/abs/2306.05685

### RFCs e ADRs
- **ADR-001**: Escolha de framework de avaliação (LLM-as-a-Judge)
- **ADR-002**: Definição de threshold mínimo (70/100)
- **ADR-003**: Critérios de avaliação e pesos

### Issues Relacionadas
- Issue #12: Implementar avaliação de qualidade LLM
- Issue #8: Testes de integração iniciais
- Issue #11: Otimização de suite de testes

---

**IMPORTANTE**: Esta tarefa é crítica para garantir qualidade objetiva e automatizada dos outputs do sistema RAG. A implementação correta permite detectar regressões de qualidade de forma confiável e escalar validações de forma sustentável.
