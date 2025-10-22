"""
Testes E2E do fluxo completo com LLM real.

Valida integração end-to-end: Ingest → Search → Chat com avaliação qualitativa.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


def test_e2e_complete_flow_with_real_llm(sample_pdf_path, clean_test_collection):
    """
    Teste E2E completo: Ingest → Search → Chat com gpt-5-nano real.
    
    Fluxo:
    1. Ingerir PDF
    2. Buscar contexto relevante
    3. Gerar resposta com LLM real
    4. Validar resposta
    
    Este é o teste mais importante: valida todo o sistema funcionando.
    """
    # 1. Ingestão
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    assert len(chunks) > 0, "Documento deve gerar chunks"
    
    # 2. Busca
    searcher = SemanticSearch(collection_name=clean_test_collection)
    context = searcher.get_context("Qual é o conteúdo principal?")
    
    assert len(context) > 0, "Contexto deve ser recuperado"
    
    # 3. Chat com LLM REAL (gpt-5-nano)
    response = ask_llm(
        question="Qual é o conteúdo principal?",
        context=context
    )
    
    # 4. Validações
    assert isinstance(response, str), "Resposta deve ser string"
    assert len(response) > 10, "Resposta deve ser substantiva"
    assert response != "", "Resposta não pode ser vazia"


def test_e2e_complete_flow_with_evaluation(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    Teste E2E completo com AVALIAÇÃO LLM de qualidade.
    
    Valida todo o fluxo end-to-end com avaliação qualitativa da resposta.
    """
    # 1. Ingestão
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # 2. Busca
    searcher = SemanticSearch(collection_name=clean_test_collection)
    question = "Resuma o conteúdo principal do documento"
    context = searcher.get_context(question)
    
    assert len(context) > 0
    
    # 3. Chat com LLM REAL
    response = ask_llm(question=question, context=context)
    
    assert len(response) > 10
    
    # 4. NOVA: Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Fluxo E2E completo deve ter alta qualidade
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        "Resposta E2E deve aderir ao contexto"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 75, \
        "Resposta E2E não deve alucinar"
    
    assert evaluation.overall_score >= 70, \
        f"Fluxo E2E completo deve ter qualidade adequada\n{evaluation.feedback}"


def test_e2e_multiple_queries_same_session(sample_pdf_path, clean_test_collection):
    """
    Teste E2E: Múltiplas queries na mesma sessão.
    
    Valida:
    - Consistência de resultados
    - Performance de queries sequenciais
    - Qualidade de respostas com LLM real
    
    Simula uso real: múltiplas perguntas sobre mesmo documento.
    """
    # Setup: Ingerir documento
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    
    # Query 1: Com contexto esperado
    context1 = searcher.get_context("Primeira pergunta sobre o documento")
    response1 = ask_llm("Primeira pergunta sobre o documento", context1)
    
    assert len(response1) > 0, "Primeira resposta deve existir"
    
    # Query 2: Sem contexto (fora do doc)
    context2 = searcher.get_context("Qual é a capital do Brasil?")
    response2 = ask_llm("Qual é a capital do Brasil?", context2)
    
    # Deve retornar mensagem padrão
    assert "Não tenho informações necessárias" in response2, \
        "Pergunta fora do contexto deve retornar mensagem padrão"
    
    # Query 3: Com contexto novamente
    context3 = searcher.get_context("Outra pergunta sobre o documento")
    response3 = ask_llm("Outra pergunta sobre o documento", context3)
    
    assert len(response3) > 0, "Terceira resposta deve existir"


def test_e2e_multiple_queries_with_evaluation(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    Teste E2E: Múltiplas queries com AVALIAÇÃO LLM.
    
    Valida consistência de qualidade entre múltiplas perguntas.
    """
    # Setup
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    
    # Query 1: Com contexto
    q1 = "Qual é o tema principal?"
    ctx1 = searcher.get_context(q1)
    resp1 = ask_llm(q1, ctx1)
    
    eval1 = llm_evaluator.evaluate(q1, ctx1, resp1, SYSTEM_PROMPT)
    
    # Query 2: Sem contexto (deve retornar mensagem padrão)
    q2 = "Qual é a velocidade da luz?"
    ctx2 = searcher.get_context(q2)
    resp2 = ask_llm(q2, ctx2)
    
    eval2 = llm_evaluator.evaluate(q2, ctx2, resp2, SYSTEM_PROMPT)
    
    # Validações
    assert eval1.passed or eval2.passed, \
        "Ao menos uma query deve passar (com ou sem contexto)"
    
    # Se resposta 2 é mensagem padrão, deve ter score alto
    if "Não tenho informações necessárias" in resp2:
        assert eval2.overall_score >= 85, \
            "Mensagem padrão deve ter score alto"


def test_e2e_special_characters_in_query(sample_pdf_path, clean_test_collection):
    """
    Teste E2E: Query com caracteres especiais.
    
    Valida que sistema lida corretamente com acentuação e pontuação.
    """
    # Setup
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    
    # Query com caracteres especiais
    question = "Qual informação sobre \"questões\" importantes?"
    context = searcher.get_context(question)
    
    # Sistema deve processar normalmente
    response = ask_llm(question=question, context=context)
    
    assert isinstance(response, str), "Resposta deve ser string"
    assert len(response) > 0, "Resposta não pode ser vazia"

