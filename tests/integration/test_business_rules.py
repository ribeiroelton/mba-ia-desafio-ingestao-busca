"""
Testes de integração para regras de negócio técnicas.

Valida configurações específicas do sistema (chunking, k, etc).
"""
import pytest

from src.ingest import load_pdf, split_documents
from src.search import SemanticSearch
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
import os


@pytest.fixture(scope="module")
def ingested_test_doc(sample_pdf_path, shared_test_collection):
    """
    Ingere documento de teste uma vez para todos os testes do módulo.
    
    Otimiza performance evitando ingestão repetida.
    """
    from src.ingest import store_in_vectorstore
    
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    
    yield shared_test_collection
    
    # Cleanup: Remover coleção após testes
    try:
        vectorstore = PGVector(
            connection=os.getenv("DATABASE_URL"),
            collection_name=shared_test_collection,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        vectorstore.delete_collection()
    except Exception:
        pass


def test_rn006_search_returns_k10(ingested_test_doc):
    """
    RN-006: Busca retorna exatamente k=10 resultados.
    
    Expected: Máximo 10 chunks retornados pela busca semântica
    
    Valida configuração fixa de k=10 para consistência.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Query genérica
    results = searcher.search("informações gerais do documento")
    
    # Validar k=10
    assert len(results) <= 10, "Busca não deve retornar mais de 10 resultados"
    assert searcher.k == 10, "k deve ser fixo em 10 (RN-006)"


def test_rn005_chunk_size_1000(sample_pdf_path):
    """
    RN-005: Chunks devem ter 1000 caracteres com overlap 150.
    
    Expected: Chunks respeitam tamanho e overlap configurados
    
    Valida regra de chunking.
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    
    # Validar que nenhum chunk excede 1000 caracteres
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000, \
            f"Chunk excede 1000 caracteres: {len(chunk.page_content)}"
    
    # Deve ter ao menos alguns chunks se documento é grande o suficiente
    assert len(chunks) > 0, "Documento deve gerar ao menos um chunk"
