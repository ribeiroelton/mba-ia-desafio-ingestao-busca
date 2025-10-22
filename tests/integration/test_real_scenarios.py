"""
Testes de cenários reais com gpt-5-nano.

Valida casos de uso práticos e edge cases com avaliação LLM qualitativa.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


@pytest.fixture(scope="module")
def real_scenario_collection(sample_pdf_path, shared_test_collection):
    """
    Setup para cenários reais: ingestão única para todos os testes.
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    
    yield shared_test_collection
    
    # Cleanup
    from langchain_postgres import PGVector
    from langchain_openai import OpenAIEmbeddings
    import os
    
    try:
        vectorstore = PGVector(
            connection=os.getenv("DATABASE_URL"),
            collection_name=shared_test_collection,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        vectorstore.delete_collection()
    except Exception:
        pass


def test_scenario_ambiguous_question(real_scenario_collection, llm_evaluator):
    """
    Cenário: Pergunta ambígua.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Quando isso aconteceu?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        f"Hallucination detection abaixo do esperado: {evaluation.criteria_scores['hallucination_detection']}"


def test_scenario_no_context_messages(real_scenario_collection, llm_evaluator):
    """
    Cenário: Pergunta fora do contexto.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Quem foi o primeiro presidente dos Estados Unidos?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["rule_following"] >= 70, \
        f"Rule following abaixo do esperado: {evaluation.criteria_scores['rule_following']}"
    assert evaluation.overall_score >= 65, \
        f"Overall score abaixo do esperado: {evaluation.overall_score}"


def test_scenario_numeric_data(real_scenario_collection, llm_evaluator):
    """
    Cenário: Extração de valor monetário de empresa específica.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Qual é o faturamento da empresa Aliança Esportes ME?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        f"Hallucination detection abaixo do esperado: {evaluation.criteria_scores['hallucination_detection']}"
    assert evaluation.criteria_scores["adherence_to_context"] >= 65, \
        f"Adherence to context abaixo do esperado: {evaluation.criteria_scores['adherence_to_context']}"


def test_scenario_factual_extraction(real_scenario_collection, llm_evaluator):
    """
    Cenário: Extração de fato específico de uma empresa.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Em que ano foi fundada a empresa Alta Mídia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Thresholds ajustados para considerar variabilidade do LLM
    assert evaluation.criteria_scores["adherence_to_context"] >= 65, \
        f"Adherence to context abaixo do esperado: {evaluation.criteria_scores['adherence_to_context']}"
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        f"Hallucination detection abaixo do esperado: {evaluation.criteria_scores['hallucination_detection']}"

