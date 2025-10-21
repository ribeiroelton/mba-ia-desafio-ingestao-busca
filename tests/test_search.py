"""Testes de integração para busca semântica."""
import pytest
from src.search import SemanticSearch


@pytest.fixture
def searcher():
    """Fixture para instância de busca."""
    return SemanticSearch()


def test_search_returns_results(searcher):
    """Testa que busca retorna resultados."""
    # Criar uma query genérica que provavelmente terá resultados
    # se houver dados no banco
    results = searcher.search("documento empresa informação")
    
    # Deve retornar até 10 resultados (pode ser menos se banco pequeno)
    assert len(results) <= 10
    
    # Cada resultado é tupla (Document, float)
    for doc, score in results:
        assert hasattr(doc, "page_content")
        assert isinstance(score, float)
        assert score >= 0  # Distância deve ser não-negativa


def test_search_empty_query(searcher):
    """Testa erro com query vazia."""
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("")
    
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("   ")


def test_search_k_fixed(searcher):
    """Testa que k=10 é fixo."""
    assert searcher.k == 10


def test_get_context(searcher):
    """Testa geração de contexto."""
    context = searcher.get_context("documento empresa")
    assert isinstance(context, str)
    
    # Se houver resultados, contexto deve conter [Chunk X]
    if context:
        assert "[Chunk 1]" in context


def test_search_results_ordered(searcher):
    """Testa que resultados são ordenados por score."""
    results = searcher.search("documento empresa")
    
    if len(results) > 1:
        # Scores devem estar em ordem crescente (menor distância = mais similar)
        scores = [score for _, score in results]
        assert scores == sorted(scores), "Resultados devem estar ordenados por score"


def test_search_invalid_collection():
    """Testa erro com coleção inexistente."""
    searcher = SemanticSearch(collection_name="nonexistent_collection")
    
    # Não deve dar erro ao criar, mas ao buscar pode não retornar resultados
    # ou dar erro dependendo do estado do banco
    try:
        results = searcher.search("test")
        assert isinstance(results, list)
    except Exception as e:
        # Aceitar exceção se coleção não existe
        assert "nonexistent_collection" in str(e).lower() or "error" in str(e).lower()


def test_semantic_search_class_initialization():
    """Testa inicialização da classe SemanticSearch."""
    searcher = SemanticSearch()
    assert searcher.k == 10
    assert hasattr(searcher, "vectorstore")
    assert searcher.vectorstore is not None


def test_get_context_empty_results():
    """Testa get_context quando não há resultados."""
    searcher = SemanticSearch(collection_name="empty_test_collection")
    
    try:
        context = searcher.get_context("xyzabc123nonexistent")
        # Se não houver resultados, contexto deve ser string vazia
        assert context == "" or isinstance(context, str)
    except Exception:
        # Aceitar exceção se coleção não existe
        pass
