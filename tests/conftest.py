"""
Fixtures globais para testes.

Provê setup/teardown compartilhado entre testes.
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

load_dotenv()


@pytest.fixture(scope="session")
def connection_string():
    """Connection string do banco de dados."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL não configurada no .env")
    return database_url


@pytest.fixture(scope="session")
def embeddings_model():
    """Modelo de embeddings."""
    return OpenAIEmbeddings(model="text-embedding-3-small")


@pytest.fixture
def test_collection_name():
    """Nome da coleção de teste."""
    return "pytest_test_collection"


@pytest.fixture
def clean_test_collection(connection_string, embeddings_model, test_collection_name):
    """
    Limpa coleção de teste antes e depois de cada teste.
    """
    # Setup: Limpar antes
    try:
        vectorstore = PGVector(
            connection=connection_string,
            collection_name=test_collection_name,
            embeddings=embeddings_model,
        )
        vectorstore.delete_collection()
    except Exception:
        pass
    
    yield test_collection_name
    
    # Teardown: Limpar depois
    try:
        vectorstore = PGVector(
            connection=connection_string,
            collection_name=test_collection_name,
            embeddings=embeddings_model,
        )
        vectorstore.delete_collection()
    except Exception:
        pass


@pytest.fixture
def sample_pdf_path():
    """Caminho para PDF de teste."""
    # Tentar fixtures primeiro, depois document.pdf na raiz
    paths = [
        Path("tests/fixtures/test_document.pdf"),
        Path("document.pdf"),
    ]
    
    for path in paths:
        if path.exists():
            return str(path)
    
    pytest.skip("PDF de teste não encontrado")


@pytest.fixture
def sample_text():
    """Texto de exemplo para testes."""
    return """
    A empresa SuperTechIABrazil apresentou faturamento de 10 milhões de reais em 2024.
    A empresa possui 50 funcionários e atende 200 clientes no Brasil.
    O crescimento anual foi de 25% comparado ao ano anterior.
    """
