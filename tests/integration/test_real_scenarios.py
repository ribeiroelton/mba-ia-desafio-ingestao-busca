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


def test_scenario_ambiguous_question_optimized(real_scenario_collection, llm_evaluator):
    """
    Cenário: Pergunta ambígua mas específica.
    
    OTIMIZADO: Pergunta menos genérica.
    Tokens: ~550 (redução de 30%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Ambígua mas não genérica
    question = "Quando isso aconteceu?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Ambiguidade aceita, mas sem alucinação
    assert evaluation.criteria_scores["hallucination_detection"] >= 80


def test_scenario_no_context_messages_optimized(real_scenario_collection, llm_evaluator):
    """
    Cenário: Múltiplas perguntas fora do contexto.
    
    OTIMIZADO: 1 pergunta ao invés de loop com 3.
    Tokens: ~400 (redução de 67%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Uma pergunta representativa
    question = "Quem foi o primeiro presidente dos Estados Unidos?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85


def test_scenario_numeric_data_optimized(real_scenario_collection, llm_evaluator):
    """
    Cenário: Extração de valor monetário específico de empresa real.
    
    OTIMIZADO: Pergunta sobre faturamento específico.
    Tokens: ~450-500 (redução de 50%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Pergunta sobre valor monetário real da tabela
    question = "Qual é o faturamento da empresa Aliança Esportes ME?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Crítico: não deve inventar valores
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 75


def test_scenario_factual_extraction_optimized(real_scenario_collection, llm_evaluator):
    """
    Cenário: Extração de fato específico de uma empresa.
    
    Tokens: ~450-500
    
    OTIMIZADO: Pergunta direta sobre ano de fundação.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Pergunta direta sobre empresa específica
    question = "Em que ano foi fundada a empresa Alta Mídia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["adherence_to_context"] >= 70
    assert evaluation.criteria_scores["hallucination_detection"] >= 80

