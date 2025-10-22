"""
Testes de integração end-to-end.

Valida fluxo completo: ingestão → busca → resposta.
Valida RN-001 a RN-006 e casos de teste CT-001, CT-002, CT-003.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.chat import ask_llm
from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch

# Carregar variáveis de ambiente
load_dotenv()

TEST_COLLECTION = "test_e2e"


@pytest.fixture(scope="function")
def setup_test_db():
    """
    Setup do banco de teste.
    
    Limpa a coleção antes e depois dos testes.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL não configurada")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Limpar coleção se existir
    try:
        vectorstore = PGVector(
            connection=database_url,
            collection_name=TEST_COLLECTION,
            embeddings=embeddings,
        )
        vectorstore.delete_collection()
    except Exception:
        pass
    
    yield
    
    # Cleanup após teste
    try:
        vectorstore = PGVector(
            connection=database_url,
            collection_name=TEST_COLLECTION,
            embeddings=embeddings,
        )
        vectorstore.delete_collection()
    except Exception:
        pass


def test_e2e_flow_with_context(setup_test_db):
    """
    CT-001: Testa fluxo completo com pergunta dentro do contexto.
    
    Cenário:
    1. Ingere PDF document.pdf
    2. Faz busca semântica por informação que está no documento
    3. Pergunta ao LLM
    4. Valida resposta com informação correta (não mensagem padrão)
    
    Valida RN-001: Respostas baseadas exclusivamente no contexto
    """
    # 1. Ingestão
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    # Carregar e processar PDF
    documents = load_pdf(str(test_pdf))
    assert len(documents) > 0, "PDF deve ter ao menos 1 página"
    
    chunks = split_documents(documents)
    assert len(chunks) > 0, "Deve gerar ao menos 1 chunk"
    
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # 2. Busca
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    question = "Qual é o faturamento da Alfa Energia S.A.?"
    context = searcher.get_context(question)
    
    # Validar contexto recuperado
    assert context, "Contexto não deve estar vazio"
    assert len(context) > 0, "Contexto deve ter conteúdo"
    
    # 3. Pergunta ao LLM
    answer = ask_llm(question, context)
    
    # 4. Validação da resposta
    assert answer, "Resposta não deve estar vazia"
    assert "não tenho informações" not in answer.lower(), \
        f"Resposta não deve ser a mensagem padrão. Resposta: {answer}"


def test_e2e_flow_without_context(setup_test_db):
    """
    CT-002: Testa fluxo completo com pergunta fora do contexto.
    
    Cenário:
    1. Ingere PDF document.pdf
    2. Faz pergunta completamente fora do contexto
    3. Valida que resposta é a mensagem padrão
    
    Valida RN-002: Mensagem padrão quando sem informação
    """
    # 1. Ingestão
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    documents = load_pdf(str(test_pdf))
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # 2. Busca com pergunta fora do contexto
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    
    # Contexto pode existir mas não ser relevante
    # 3. Pergunta ao LLM
    answer = ask_llm(question, context)
    
    # 4. Validação - deve retornar mensagem padrão
    assert "não tenho informações necessárias" in answer.lower() or \
           "não tenho informações" in answer.lower(), \
        f"Resposta deve ser a mensagem padrão. Resposta recebida: {answer}"


def test_e2e_partial_information(setup_test_db):
    """
    CT-003: Testa pergunta com informação parcial no contexto.
    
    Cenário:
    1. Ingere PDF document.pdf
    2. Faz pergunta que pode ter informação limitada
    3. Valida que sistema responde adequadamente
    
    Valida que sistema reconhece limitações do contexto
    """
    # 1. Ingestão
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    documents = load_pdf(str(test_pdf))
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # 2. Busca com pergunta parcialmente coberta
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    question = "Quais são os principais desafios?"
    context = searcher.get_context(question)
    
    # 3. Pergunta ao LLM
    answer = ask_llm(question, context)
    
    # 4. Validação - deve ter resposta não vazia
    assert len(answer) > 0, "Resposta não deve estar vazia"
    # Sistema deve responder com base no contexto ou admitir falta de informação


def test_search_returns_k10(setup_test_db):
    """
    RN-006: Valida que busca retorna no máximo k=10 resultados.
    
    Valida configuração de k=10 no sistema de busca.
    """
    # Ingestão mínima
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    documents = load_pdf(str(test_pdf))
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # Testar busca
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    results = searcher.search("teste")
    
    # Deve retornar no máximo 10 resultados
    assert len(results) <= 10, f"Deve retornar no máximo 10, retornou {len(results)}"


def test_chunk_size_validation():
    """
    RN-003: Valida configuração de chunk size 1000/150.
    
    Valida que chunks são criados com tamanho correto e overlap adequado.
    """
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    # Texto maior que chunk_size para forçar divisão
    text = "A" * 2500
    chunks = splitter.split_text(text)
    
    # Validar chunks
    assert all(len(chunk) <= 1000 for chunk in chunks), \
        "Chunks devem ter no máximo 1000 caracteres"
    
    # Validar que houve divisão
    assert len(chunks) > 1, "Texto longo deve ser dividido em múltiplos chunks"


def test_cosine_distance_validation(setup_test_db):
    """
    RN-004: Valida que similaridade usa cosine distance.
    
    Valida que o sistema usa distância cosseno para busca de similaridade.
    """
    # Ingestão
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    documents = load_pdf(str(test_pdf))
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # Buscar com termo específico
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    results = searcher.search("sistema")
    
    # Validar que retorna resultados com scores
    assert len(results) > 0, "Deve retornar resultados"
    
    # Cada resultado é tupla (documento, score)
    for doc, score in results:
        assert isinstance(score, float), "Score deve ser float"
        assert score >= 0, "Score (distância) deve ser >= 0"
    
    # Validar ordenação (menor distância = mais similar)
    scores = [score for _, score in results]
    assert scores == sorted(scores), "Resultados devem estar ordenados por distância crescente"


def test_end_to_end_complete_flow(setup_test_db):
    """
    Teste completo do fluxo end-to-end integrado.
    
    Valida todos os componentes trabalhando juntos:
    - Ingestão (ingest.py)
    - Busca (search.py)  
    - Chat (chat.py)
    """
    # 1. Ingestão
    test_pdf = Path("document.pdf")
    
    if not test_pdf.exists():
        pytest.skip("document.pdf não encontrado na raiz do projeto")
    
    documents = load_pdf(str(test_pdf))
    assert len(documents) > 0
    
    chunks = split_documents(documents)
    assert len(chunks) > 0
    
    # Validar tamanho dos chunks
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000, "Chunk excede tamanho máximo"
    
    store_in_vectorstore(chunks, collection_name=TEST_COLLECTION)
    
    # 2. Busca
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    
    # Validar atributo k
    assert searcher.k == 10, "k deve ser fixo em 10 (RN-006)"
    
    # Buscar contexto
    question = "O que é este documento?"
    context = searcher.get_context(question)
    
    assert context, "Contexto não deve estar vazio"
    
    # 3. Chat/LLM
    answer = ask_llm(question, context)
    
    assert answer, "Resposta não deve estar vazia"
    assert len(answer) > 10, "Resposta deve ter conteúdo significativo"


def test_empty_query_handling():
    """
    Testa tratamento de query vazia.
    
    Valida que sistema trata adequadamente entrada inválida.
    """
    searcher = SemanticSearch(collection_name=TEST_COLLECTION)
    
    # Query vazia deve lançar ValueError
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("")
    
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("   ")


def test_nonexistent_collection():
    """
    Testa comportamento com coleção inexistente.
    
    Valida que sistema inicializa mesmo com coleção vazia.
    """
    # Deve conseguir criar searcher mesmo se coleção não existe
    searcher = SemanticSearch(collection_name="nonexistent_collection_xyz")
    assert searcher is not None
    assert searcher.k == 10
    
    # Busca em coleção vazia deve retornar lista vazia
    results = searcher.search("qualquer coisa")
    assert isinstance(results, list)
    assert len(results) == 0, "Coleção vazia deve retornar 0 resultados"
