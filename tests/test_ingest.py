"""Testes unitários para módulo de ingestão."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from src.ingest import load_pdf, split_documents, store_in_vectorstore


def test_load_pdf_success(sample_pdf_path):
    """Testa carregamento de PDF válido."""
    documents = load_pdf(sample_pdf_path)
    assert len(documents) > 0
    assert all(hasattr(doc, "page_content") for doc in documents)
    assert all(hasattr(doc, "metadata") for doc in documents)


def test_load_pdf_file_not_found():
    """Testa erro quando arquivo não existe."""
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        load_pdf("naoexiste.pdf")


def test_load_pdf_invalid_extension():
    """Testa erro quando arquivo não é PDF."""
    with pytest.raises(ValueError, match="Arquivo deve ser PDF"):
        load_pdf("README.md")


def test_split_documents_basic():
    """Testa divisão básica em chunks."""
    # Criar documento de teste com 3000 caracteres
    text = "A" * 3000
    documents = [Document(page_content=text)]
    
    chunks = split_documents(documents)
    
    # Deve criar múltiplos chunks
    assert len(chunks) > 1
    
    # Chunks devem ter <= 1000 caracteres (tamanho padrão)
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000


def test_split_documents_respects_chunk_size():
    """Testa que split respeita chunk_size configurado."""
    # Criar documento de teste
    text = "B" * 2500
    documents = [Document(page_content=text)]
    
    # Configurar chunk_size via variável de ambiente
    with patch.dict(os.environ, {"CHUNK_SIZE": "500", "CHUNK_OVERLAP": "50"}):
        chunks = split_documents(documents)
    
    # Validar que chunks respeitam o tamanho
    for chunk in chunks:
        assert len(chunk.page_content) <= 500


def test_split_documents_empty_list():
    """Testa split com lista vazia."""
    chunks = split_documents([])
    assert len(chunks) == 0


def test_split_documents_single_small_document():
    """Testa split com documento menor que chunk_size."""
    text = "Texto pequeno"
    documents = [Document(page_content=text)]
    
    chunks = split_documents(documents)
    
    # Deve retornar 1 chunk
    assert len(chunks) == 1
    assert chunks[0].page_content == text


def test_split_documents_preserves_metadata():
    """Testa que metadata é preservada nos chunks."""
    text = "C" * 2000
    metadata = {"source": "test.pdf", "page": 1}
    documents = [Document(page_content=text, metadata=metadata)]
    
    chunks = split_documents(documents)
    
    # Validar metadata preservada
    for chunk in chunks:
        assert chunk.metadata.get("source") == "test.pdf"
        assert chunk.metadata.get("page") == 1


def test_store_in_vectorstore_success(clean_test_collection, sample_text):
    """Testa armazenamento bem-sucedido no vectorstore."""
    # Criar chunks de teste
    chunks = [Document(page_content=sample_text)]
    
    # Armazenar
    store_in_vectorstore(chunks, collection_name=clean_test_collection)
    
    # Validar que documentos foram armazenados
    from langchain_postgres import PGVector
    from langchain_openai import OpenAIEmbeddings
    
    vectorstore = PGVector(
        connection=os.getenv("DATABASE_URL"),
        collection_name=clean_test_collection,
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
    )
    
    # Buscar documentos
    results = vectorstore.similarity_search("empresa", k=1)
    assert len(results) > 0, "Deve ter documentos no vectorstore"


def test_store_in_vectorstore_empty_chunks(clean_test_collection):
    """Testa armazenamento com lista vazia."""
    # Lista vazia deve ser tratada sem erro
    store_in_vectorstore([], collection_name=clean_test_collection)
    # Deve retornar sem tentar inserir nada


def test_ingest_pdf_invalid_path():
    """Testa ingestão com caminho inválido."""
    with pytest.raises(FileNotFoundError):
        load_pdf("arquivo_inexistente.pdf")
