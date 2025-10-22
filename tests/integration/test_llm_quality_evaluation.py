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


def test_factual_accuracy_direct_question(quality_test_collection, llm_evaluator):
    """
    Valida resposta factual para pergunta direta sobre empresa específica.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions fortalecidas com thresholds ajustados para variabilidade do LLM
    assert evaluation.passed, \
        f"Falhou com score {evaluation.score}: {evaluation.feedback}"
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        f"Detecção de alucinação abaixo do esperado: {evaluation.criteria_scores['hallucination_detection']}"
    assert evaluation.criteria_scores["adherence_to_context"] >= 65, \
        f"Aderência ao contexto abaixo do esperado: {evaluation.criteria_scores['adherence_to_context']}"
    assert 70 <= evaluation.score <= 100, \
        f"Score fora do range esperado: {evaluation.score}"


def test_no_context_standard_message(quality_test_collection, llm_evaluator):
    """
    Valida mensagem padrão quando sem contexto.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["rule_following"] >= 70, \
        f"Seguimento de regras abaixo do esperado: {evaluation.criteria_scores['rule_following']}"
    assert evaluation.overall_score >= 65, \
        f"Score geral abaixo do esperado: {evaluation.overall_score}"
    assert 70 <= evaluation.score <= 100, \
        f"Score fora do range esperado: {evaluation.score}"


def test_partial_info_no_hallucination(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não inventa informações ausentes no documento.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # Pergunta sobre campo não presente na tabela
    question = "Quantos funcionários a empresa Alfa Energia S.A. possui?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Crítico: não deve inventar números de funcionários (campo não existe no doc)
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        f"Detecção de alucinação abaixo do esperado: {evaluation.criteria_scores['hallucination_detection']}"
    assert evaluation.overall_score >= 60, \
        f"Score geral abaixo do esperado: {evaluation.overall_score}"
    assert 0 <= evaluation.score <= 100, \
        f"Score fora do range válido: {evaluation.score}"


def test_no_external_knowledge(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não usa conhecimento geral externo.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve usar contexto OU mensagem padrão, nunca conhecimento geral
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        f"Aderência ao contexto abaixo do esperado: {evaluation.criteria_scores['adherence_to_context']}"
    assert evaluation.criteria_scores["rule_following"] >= 70, \
        f"Seguimento de regras abaixo do esperado: {evaluation.criteria_scores['rule_following']}"
    assert 70 <= evaluation.score <= 100, \
        f"Score fora do range esperado: {evaluation.score}"


