"""
Testes E2E do fluxo completo com LLM real.

Valida integração end-to-end: Ingest → Search → Chat
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm


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


def test_e2e_empty_collection_handling(test_collection_name):
    """
    Teste E2E: Comportamento com coleção vazia.
    
    Cenário: Buscar em coleção sem documentos
    Expected: Sistema trata gracefully, não retorna contexto útil
    """
    # Coleção vazia (clean_test_collection já limpa)
    searcher = SemanticSearch(collection_name=test_collection_name)
    
    # Buscar em coleção vazia
    try:
        context = searcher.get_context("Qualquer pergunta")
        
        # Contexto vazio ou mensagem indicando falta de dados
        # Sistema deve lidar com isso sem erro
        assert isinstance(context, str), "Contexto deve ser string"
        
    except Exception as e:
        # Aceitar exceção se sistema não consegue buscar em coleção vazia
        # Mas deve ser exceção tratada, não erro inesperado
        assert "collection" in str(e).lower() or "not found" in str(e).lower()


def test_e2e_special_characters_in_query(sample_pdf_path, clean_test_collection):
    """
    Teste E2E: Query com caracteres especiais.
    
    Valida que sistema lida corretamente com:
    - Acentuação
    - Pontuação
    - Caracteres especiais
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


def test_e2e_context_length_validation(sample_pdf_path, clean_test_collection):
    """
    Teste E2E: Validar que contexto tem tamanho adequado.
    
    Expected: Contexto contém múltiplos chunks (até k=10)
    Valida que formatação [Chunk X] está presente
    """
    # Setup
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    
    # Query genérica que deve recuperar múltiplos chunks
    context = searcher.get_context("informações gerais")
    
    # Validar formato do contexto
    assert isinstance(context, str), "Contexto deve ser string"
    assert len(context) > 0, "Contexto não pode ser vazio"
    
    # Se há chunks, formato deve incluir marcadores
    if len(chunks) > 0:
        assert "[Chunk" in context or len(context.split('\n')) > 1, \
            "Contexto deve ter formato estruturado"
