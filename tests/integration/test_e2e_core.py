"""
Testes E2E do fluxo completo com LLM real.

Valida integração end-to-end: Ingest → Search → Chat com avaliação qualitativa.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


def test_e2e_complete_flow_optimized(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E completo com pergunta direta sobre empresa da tabela.
    
    Tokens: ~500-600 (redução de 50%)
    
    OTIMIZADO: Pergunta específica sobre primeira empresa da lista.
    """
    # Ingestão
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Busca com pergunta direta sobre dado real
    searcher = SemanticSearch(collection_name=clean_test_collection)
    question = "Qual é o faturamento da primeira empresa mencionada no documento?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.passed
    assert evaluation.criteria_scores["adherence_to_context"] >= 70


def test_e2e_no_context_flow_optimized(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E com pergunta fora do contexto.
    
    Tokens: ~400
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    question = "Qual é a capital do Brasil?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90


def test_e2e_special_characters_optimized(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E com formato monetário (caracteres especiais R$).
    
    Tokens: ~450-500
    
    OTIMIZADO: Pergunta sobre formato presente no documento (R$).
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    # OTIMIZADO: Pergunta sobre formato monetário real do documento
    question = "Os valores estão em qual moeda?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 70

