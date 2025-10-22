"""
Módulo de ingestão de documentos PDF.

Processa documentos PDF, divide em chunks, gera embeddings e armazena no PGVector.
"""

import os
import sys
from pathlib import Path
from typing import List

import typer
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carregar variáveis de ambiente
load_dotenv()

app = typer.Typer()


def load_pdf(file_path: str) -> List[Document]:
    """
    Carrega documento PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Lista de documentos carregados
        
    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se arquivo não for PDF
    """
    pdf_path = Path(file_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Arquivo deve ser PDF: {file_path}")
    
    typer.echo(f"📄 Carregando PDF: {pdf_path.name}")
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()
    
    typer.echo(f"✓ {len(documents)} páginas carregadas")
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Divide documentos em chunks.
    
    Configuração:
    - Tamanho do chunk: 1000 caracteres (RN-005)
    - Overlap: 150 caracteres (RN-005)
    
    Args:
        documents: Lista de documentos a dividir
        
    Returns:
        Lista de chunks
    """
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
    
    typer.echo(f"✂️  Dividindo em chunks (size={chunk_size}, overlap={chunk_overlap})")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    typer.echo(f"✓ {len(chunks)} chunks criados")
    return chunks


def store_in_vectorstore(chunks: List[Document], collection_name: str = "rag_documents") -> None:
    """
    Armazena chunks no PGVector.
    
    Args:
        chunks: Lista de chunks a armazenar
        collection_name: Nome da coleção no banco
        
    Raises:
        ValueError: Se DATABASE_URL não configurada
        Exception: Se houver erro ao armazenar
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL não configurada no .env")
    
    # Verificar se há chunks para armazenar
    if not chunks:
        typer.echo("⚠️  Nenhum chunk para armazenar")
        return
    
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    typer.echo(f"🔢 Gerando embeddings com {embedding_model}")
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    typer.echo(f"💾 Armazenando no PGVector (collection: {collection_name})")
    
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=database_url,
        use_jsonb=True,
    )
    
    # Adicionar chunks ao vectorstore
    vectorstore.add_documents(chunks)
    
    typer.echo(f"✓ {len(chunks)} chunks armazenados com sucesso")


@app.command()
def main(
    pdf_path: str = typer.Argument(..., help="Caminho para o arquivo PDF"),
    collection: str = typer.Option("rag_documents", help="Nome da coleção no banco"),
) -> None:
    """
    Ingere documento PDF no sistema RAG.
    
    Processo:
    1. Carrega PDF
    2. Divide em chunks de 1000 caracteres (overlap 150)
    3. Gera embeddings
    4. Armazena no PGVector
    
    Exemplo:
        python src/ingest.py document.pdf
        python src/ingest.py document.pdf --collection custom_docs
    """
    try:
        typer.echo("🚀 Iniciando ingestão de documento\n")
        
        # 1. Carregar PDF
        documents = load_pdf(pdf_path)
        
        # 2. Dividir em chunks
        chunks = split_documents(documents)
        
        # 3. Armazenar no vectorstore
        store_in_vectorstore(chunks, collection)
        
        typer.echo("\n✅ Ingestão concluída com sucesso!")
        typer.echo(f"📊 Total de chunks: {len(chunks)}")
        typer.echo(f"🗄️  Coleção: {collection}")
        
    except FileNotFoundError as e:
        typer.echo(f"❌ Erro: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        typer.echo(f"❌ Erro de validação: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Erro inesperado: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
