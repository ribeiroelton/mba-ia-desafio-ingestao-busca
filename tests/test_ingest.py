"""Testes de integração para ingestão."""
import pytest
from pathlib import Path
from src.ingest import load_pdf, split_documents


def test_load_pdf_success():
    """Testa carregamento de PDF válido."""
    pdf_path = "document.pdf"
    if not Path(pdf_path).exists():
        pytest.skip("document.pdf não encontrado")
    
    documents = load_pdf(pdf_path)
    assert len(documents) > 0
    assert all(hasattr(doc, "page_content") for doc in documents)


def test_load_pdf_file_not_found():
    """Testa erro quando arquivo não existe."""
    with pytest.raises(FileNotFoundError):
        load_pdf("naoexiste.pdf")


def test_load_pdf_invalid_extension():
    """Testa erro quando arquivo não é PDF."""
    with pytest.raises(ValueError):
        load_pdf("README.md")


def test_split_documents():
    """Testa divisão em chunks."""
    from langchain_core.documents import Document
    
    # Criar documento de teste com 3000 caracteres
    text = "A" * 3000
    documents = [Document(page_content=text)]
    
    chunks = split_documents(documents)
    
    # Deve criar múltiplos chunks
    assert len(chunks) > 1
    
    # Chunks devem ter <= 1000 caracteres
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000
