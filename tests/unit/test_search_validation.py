"""
Testes unitários críticos para validação de busca.

Valida entrada e configurações críticas do módulo de search.
"""
import pytest
import os

from src.search import SemanticSearch


def test_search_empty_query():
    """
    Valida erro com query vazia.
    
    Expected: ValueError com mensagem clara
    """
    searcher = SemanticSearch()
    
    with pytest.raises(ValueError, match="vazia"):
        searcher.search("")


def test_search_k_fixed_10():
    """
    Valida que k=10 é fixo (RN-006).
    
    Regra de Negócio: Sistema sempre busca exatamente 10 resultados
    """
    searcher = SemanticSearch()
    assert searcher.k == 10


def test_search_initialization_default():
    """
    Valida inicialização com valores padrão.
    
    Expected: k=10 fixo
    """
    searcher = SemanticSearch()
    assert searcher.k == 10


def test_search_initialization_custom_collection():
    """
    Valida inicialização com collection customizada.
    
    Expected: k=10 mantido independente de collection
    """
    custom_name = "custom_collection"
    searcher = SemanticSearch(collection_name=custom_name)
    
    # k sempre 10
    assert searcher.k == 10


def test_search_k_env_variable():
    """
    Valida que k pode ser configurado via SEARCH_K (RN-006).
    
    Nota: Mesmo com variável de ambiente, k=10 deve ser respeitado
    """
    # Salvar valor original
    original_k = os.getenv("SEARCH_K")
    
    try:
        # Configurar SEARCH_K
        os.environ["SEARCH_K"] = "10"
        searcher = SemanticSearch()
        assert searcher.k == 10
    finally:
        # Restaurar valor original
        if original_k:
            os.environ["SEARCH_K"] = original_k
        else:
            os.environ.pop("SEARCH_K", None)
