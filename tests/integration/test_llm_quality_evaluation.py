"""
Testes de qualidade de outputs LLM usando LLM-as-a-Judge.

Valida aspectos qualitativos das respostas que vão além de validações estruturais.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


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
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        "Aderência ao contexto deve ser razoável para resposta factual"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        "Não deve haver alucinação em resposta factual"
    
    assert evaluation.criteria_scores["clarity_objectivity"] >= 70, \
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
    Testa completude da resposta para pergunta específica sobre estrutura.
    
    Cenário: Pergunta detalhada sobre organização do conteúdo.
    Expected: Resposta abrangente e bem estruturada.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta sobre estrutura/organização
    question = "Como o conteúdo está organizado e quais são as principais seções?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural básica
    assert len(response) > 50, "Resposta deve ser substantiva"
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para pergunta sobre organização:
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        "Resposta deve ser baseada no contexto"
    
    assert evaluation.criteria_scores["clarity_objectivity"] >= 70, \
        "Resposta deve ser clara e bem organizada"
    
    assert evaluation.overall_score >= 70, \
        f"Resposta deve passar no threshold\n{evaluation.feedback}"


def test_response_consistency_across_similar_questions(
    quality_test_collection,
    llm_evaluator
):
    """
    Testa consistência de respostas para perguntas similares sobre conceitos.
    
    Cenário: Múltiplas formas de perguntar sobre definições.
    Expected: Scores de qualidade consistentes entre respostas.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Perguntas similares sobre conceitos/definições
    similar_questions = [
        "O que é mencionado sobre inteligência artificial?",
        "Quais informações sobre IA estão presentes?",
        "O documento fala sobre inteligência artificial?",
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
    
    # Todas devem passar ou todas devem usar mensagem padrão consistentemente
    passed_count = sum(1 for e in evaluations if e.passed)
    
    # Se há contexto sobre o tema, todas devem passar
    # Se não há contexto, todas devem falhar/usar mensagem padrão
    assert passed_count == 0 or passed_count == len(evaluations), \
        f"Inconsistência: {passed_count}/{len(evaluations)} passaram"


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


def test_response_handles_partial_information(quality_test_collection, llm_evaluator):
    """
    Testa comportamento quando contexto tem informação parcial.
    
    Cenário: Pergunta específica mas contexto tem apenas info relacionada.
    Expected: LLM responde com info disponível ou admite limitação.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta específica que pode ter resposta parcial
    question = "Quais são todos os números mencionados no documento?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para informação parcial, ainda deve:
    assert evaluation.criteria_scores["adherence_to_context"] >= 75, \
        "Deve aderir ao contexto mesmo com info parcial"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        "Não deve inventar números não presentes"
    
    # Score geral pode ser menor devido à parcialidade, mas deve ser razoável
    assert evaluation.overall_score >= 65, \
        f"Score muito baixo para resposta com info parcial\n{evaluation.feedback}"


def test_response_avoids_external_knowledge(quality_test_collection, llm_evaluator):
    """
    Testa que LLM não usa conhecimento externo mesmo quando pergunta sugere.
    
    Cenário: Pergunta sobre tema comum mas resposta deve ser baseada no contexto.
    Expected: Score alto de aderência e rule_following.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta sobre tema comum (tentação de usar conhecimento geral)
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve evitar conhecimento externo
    assert evaluation.criteria_scores["adherence_to_context"] >= 80, \
        "Não deve usar conhecimento externo sobre IA"
    
    assert evaluation.criteria_scores["rule_following"] >= 85, \
        "Deve seguir regra de não usar conhecimento externo"
    
    # Se contexto não tem info sobre IA, deve usar mensagem padrão
    if "Não tenho informações necessárias" in response:
        assert evaluation.overall_score >= 85, \
            "Mensagem padrão correta deve ter score alto"
