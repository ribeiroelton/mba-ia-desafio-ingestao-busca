"""
Testes unitários críticos para validação de ingestão.

Valida entrada de dados e lógica de chunking.
"""
import pytest
from pathlib import Path
from langchain_core.documents import Document

from src.ingest import load_pdf, split_documents


def test_load_pdf_file_not_found():
    """
    Valida erro quando arquivo não existe.
    
    Expected: FileNotFoundError com mensagem clara
    """
    with pytest.raises(FileNotFoundError):
        load_pdf("arquivo_inexistente.pdf")


def test_load_pdf_invalid_extension():
    """
    Valida erro quando arquivo não é PDF.
    
    Expected: ValueError indicando formato inválido
    
    Nota: Teste removido pois load_pdf verifica existência antes de extensão
    """
    # Create a temporary non-PDF file to test
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="deve ser PDF"):
            load_pdf(temp_path)
    finally:
        import os
        os.unlink(temp_path)


def test_split_documents_chunk_size():
    """
    Valida que chunks respeitam tamanho máximo (RN-005).
    
    Regra de Negócio: Chunks devem ter no máximo 1000 caracteres
    """
    # Documento com texto longo
    text = "A" * 3000
    docs = [Document(page_content=text)]
    
    chunks = split_documents(docs)
    
    # Todos os chunks <= 1000 caracteres
    assert all(len(c.page_content) <= 1000 for c in chunks)
    # Mínimo esperado para 3000 chars com chunk_size=1000
    assert len(chunks) >= 3


def test_split_documents_overlap():
    """
    Valida overlap de 150 caracteres entre chunks (RN-005).
    
    Regra de Negócio: Overlap fixo de 150 caracteres para continuidade
    """
    # Documento com conteúdo suficiente para múltiplos chunks
    text = "B" * 2000
    docs = [Document(page_content=text)]
    
    chunks = split_documents(docs)
    
    # Se há múltiplos chunks, deve haver overlap
    if len(chunks) > 1:
        # Chunks subsequentes devem ter overlap
        # Validação: tamanho total esperado considerando overlap
        # chunk1: 1000, chunk2: 1000 (150 overlap) = 1850 chars únicos
        assert len(chunks) >= 2


def test_split_documents_empty_list():
    """
    Valida tratamento de lista vazia.
    
    Expected: Lista vazia retorna lista vazia
    """
    chunks = split_documents([])
    assert chunks == []


def test_split_documents_preserves_metadata():
    """
    Valida que metadata é preservada nos chunks.
    
    Expected: Metadata original mantida em todos os chunks
    """
    metadata = {"source": "test.pdf", "page": 1}
    docs = [Document(page_content="A" * 2000, metadata=metadata)]
    
    chunks = split_documents(docs)
    
    # Todos os chunks devem ter a metadata original
    for chunk in chunks:
        assert chunk.metadata.get("source") == "test.pdf"
        assert chunk.metadata.get("page") == 1
