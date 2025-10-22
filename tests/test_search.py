"""Testes unitários para módulo de busca."""
import os
import pytest
from unittest.mock import patch, MagicMock

from src.search import SemanticSearch
from src.ingest import store_in_vectorstore
from langchain_core.documents import Document


def test_semantic_search_initialization():
    """Testa inicialização do SemanticSearch."""
    searcher = SemanticSearch()
    assert searcher.k == 10
    assert hasattr(searcher, "vectorstore")
    assert searcher.vectorstore is not None


def test_semantic_search_with_custom_collection():
    """Testa inicialização com coleção customizada."""
    test_collection = "custom_test_collection"
    searcher = SemanticSearch(collection_name=test_collection)
    assert searcher.vectorstore is not None


def test_search_empty_query():
    """Testa erro com query vazia."""
    searcher = SemanticSearch()
    
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("")
    
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("   ")


def test_search_k_fixed():
    """Testa que k=10 é fixo (RN-006)."""
    searcher = SemanticSearch()
    assert searcher.k == 10


def test_search_k_respects_env_variable():
    """Testa que k pode ser configurado via variável de ambiente."""
    with patch.dict(os.environ, {"SEARCH_K": "5"}):
        searcher = SemanticSearch()
        assert searcher.k == 5


def test_similarity_search_returns_max_k10(clean_test_collection, sample_pdf_path):
    """Testa que busca retorna no máximo k=10 resultados."""
    from src.ingest import load_pdf, split_documents
    
    # Ingerir documento
    documents = load_pdf(sample_pdf_path)
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Buscar
    searcher = SemanticSearch(collection_name=clean_test_collection)
    results = searcher.search("empresa")
    
    # Validar
    assert len(results) <= 10, f"Retornou {len(results)}, esperado máximo 10"
    
    # Cada resultado é tupla (Document, float)
    for doc, score in results:
        assert hasattr(doc, "page_content")
        assert isinstance(score, float)
        assert score >= 0


def test_search_results_ordered(clean_test_collection, sample_pdf_path):
    """Testa que resultados são ordenados por score."""
    from src.ingest import load_pdf, split_documents
    
    # Ingerir documento
    documents = load_pdf(sample_pdf_path)
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Buscar
    searcher = SemanticSearch(collection_name=clean_test_collection)
    results = searcher.search("empresa")
    
    if len(results) > 1:
        # Scores devem estar em ordem crescente (menor distância = mais similar)
        scores = [score for _, score in results]
        assert scores == sorted(scores), "Resultados devem estar ordenados por score"


def test_get_context_returns_string(clean_test_collection, sample_pdf_path):
    """Testa que get_context retorna string."""
    from src.ingest import load_pdf, split_documents
    
    # Ingerir documento
    documents = load_pdf(sample_pdf_path)
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Buscar contexto
    searcher = SemanticSearch(collection_name=clean_test_collection)
    context = searcher.get_context("empresa")
    
    # Validar
    assert isinstance(context, str), "Contexto deve ser string"
    assert len(context) > 0, "Contexto não deve estar vazio"
    
    # Deve conter marcador de chunk
    assert "[Chunk 1]" in context


def test_get_context_format(clean_test_collection, sample_text):
    """Testa formato do contexto retornado."""
    # Ingerir texto de teste
    chunks = [
        Document(page_content="Primeiro chunk de teste"),
        Document(page_content="Segundo chunk de teste"),
    ]
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Buscar contexto
    searcher = SemanticSearch(collection_name=clean_test_collection)
    context = searcher.get_context("teste")
    
    # Validar formato
    assert "[Chunk 1]" in context
    assert "Primeiro chunk" in context or "Segundo chunk" in context


def test_search_with_no_results(clean_test_collection):
    """Testa busca em coleção vazia."""
    searcher = SemanticSearch(collection_name=clean_test_collection)
    results = searcher.search("teste")
    
    # Deve retornar lista vazia
    assert len(results) == 0, "Deve retornar lista vazia para coleção vazia"


def test_get_context_with_no_results(clean_test_collection):
    """Testa get_context quando não há resultados."""
    searcher = SemanticSearch(collection_name=clean_test_collection)
    context = searcher.get_context("teste")
    
    # Deve retornar string vazia
    assert context == "", "Deve retornar string vazia quando não há resultados"


def test_search_with_special_characters(clean_test_collection, sample_text):
    """Testa busca com caracteres especiais."""
    # Ingerir texto
    chunks = [Document(page_content=sample_text)]
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Buscar com caracteres especiais
    searcher = SemanticSearch(collection_name=clean_test_collection)
    
    queries = [
        "empresa com R$ 10 milhões",
        "crescimento de 25%",
        "atende 200 clientes",
    ]
    
    for query in queries:
        results = searcher.search(query)
        assert isinstance(results, list)


def test_vectorstore_connection_error():
    """Testa erro de conexão com DATABASE_URL inválida."""
    with patch.dict(os.environ, {"DATABASE_URL": ""}):
        with pytest.raises(ValueError, match="DATABASE_URL não configurada"):
            SemanticSearch()
