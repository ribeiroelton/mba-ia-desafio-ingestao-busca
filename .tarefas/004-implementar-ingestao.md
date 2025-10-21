# [004] - Implementar Módulo de Ingestão de PDFs (ingest.py)

## Metadados
- **ID**: 004
- **Grupo**: Fase 2 - Implementação Core RAG
- **Prioridade**: Alta
- **Complexidade**: Alta
- **Estimativa**: 1 dia

## Descrição
Implementar script completo de ingestão de documentos PDF usando PyPDFLoader, RecursiveCharacterTextSplitter para chunking (1000 caracteres, overlap 150), geração de embeddings com OpenAI e armazenamento no PGVector.

## Requisitos

### Requisitos Funcionais
- UC-001: Ingerir Documento PDF
- RF-006: Carregar PDF usando PyPDFLoader
- RF-007: Dividir em chunks de 1000 caracteres com overlap 150
- RF-008: Gerar embeddings com text-embedding-3-small
- RF-009: Armazenar no PGVector

### Requisitos Não-Funcionais
- RN-005: Chunks devem ter exatamente 1000 caracteres com overlap de 150
- RNF-009: Seguir padrões Pythonic e PEP 8
- RNF-010: Tratamento de erros robusto

## Fonte da Informação
- **Seção 2.3**: Processo de Ingestão de Documentos
- **Seção 3.2**: Diagrama de Componentes - ingest.py
- **Seção 4.1**: UC-001 - Ingerir Documento PDF
- **Seção 3.1**: Stack - PyPDFLoader, RecursiveCharacterTextSplitter, OpenAIEmbeddings
- **Seção 3.4**: Connection string PostgreSQL

## Stack Necessária
- **Python**: 3.13.9
- **LangChain**: 
  - PyPDFLoader (langchain-community)
  - RecursiveCharacterTextSplitter (langchain_text_splitters)
  - OpenAIEmbeddings (langchain_openai)
  - PGVector (langchain_postgres)
- **Database**: PostgreSQL com pgVector
- **APIs**: OpenAI API

## Dependências

### Dependências Técnicas
- Tarefa 001: PostgreSQL rodando
- Tarefa 002: Estrutura criada
- Tarefa 003: Dependências instaladas
- Arquivo PDF de exemplo (`document.pdf`)

### Dependências de Negócio
- OpenAI API Key válida

## Critérios de Aceite

1. [x] Script `src/ingest.py` implementado
2. [x] PyPDFLoader carrega PDF corretamente
3. [x] RecursiveCharacterTextSplitter divide em chunks de 1000 caracteres
4. [x] Overlap de 150 caracteres configurado
5. [x] OpenAIEmbeddings gera embeddings
6. [x] PGVector armazena chunks e embeddings
7. [x] Script aceita caminho do PDF como argumento CLI
8. [x] Logging de progresso implementado
9. [x] Tratamento de erros robusto
10. [x] Mensagem de sucesso ao final
11. [x] Validação: chunks no banco de dados

## Implementação Resumida

### Arquivo Principal

**Arquivo**: `src/ingest.py`
**Responsabilidade**: Ingerir PDFs e armazenar embeddings

```python
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


def store_in_vectorstore(chunks: List[Document], collection_name: str = "rag_documents"):
    """
    Armazena chunks no PGVector.
    
    Args:
        chunks: Lista de chunks a armazenar
        collection_name: Nome da coleção no banco
        
    Raises:
        Exception: Se houver erro ao armazenar
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL não configurada no .env")
    
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
):
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
```

## Testes de Qualidade e Cobertura

### Testes de Integração

**Arquivo**: `tests/test_ingest.py`
```python
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
```

**Cenários de Teste Manual**:

1. **Cenário 1: Ingestão bem-sucedida**
   ```bash
   python src/ingest.py document.pdf
   # Expected: Mensagem de sucesso
   ```

2. **Cenário 2: Verificar chunks no banco**
   ```bash
   docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
   # Expected: Número > 0
   ```

3. **Cenário 3: PDF inexistente**
   ```bash
   python src/ingest.py naoexiste.pdf
   # Expected: Erro FileNotFoundError
   ```

## Checklist de Finalização

- [x] `src/ingest.py` implementado
- [x] PyPDFLoader integrado
- [x] RecursiveCharacterTextSplitter configurado (1000/150)
- [x] OpenAIEmbeddings integrado
- [x] PGVector storage implementado
- [x] CLI com Typer implementado
- [x] Logging de progresso adicionado
- [x] Tratamento de erros implementado
- [x] Docstrings completas
- [x] Testes de integração criados
- [x] Validação manual executada
- [x] Chunks verificados no banco de dados

## Notas Adicionais

### Uso do Script
```bash
# Ingestão básica
python src/ingest.py document.pdf

# Com coleção customizada
python src/ingest.py document.pdf --collection meus_docs

# Ver ajuda
python src/ingest.py --help
```

### Troubleshooting

**Erro: OpenAI API Key inválida**
```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# Testar key manualmente
python -c "from openai import OpenAI; client = OpenAI(); print('OK')"
```

**Erro: Conexão PostgreSQL**
```bash
# Verificar container
docker ps | grep rag-postgres

# Testar conexão
psql "postgresql://postgres:postgres@localhost:5432/rag"
```

**Chunks muito grandes/pequenos**
- Ajustar `CHUNK_SIZE` e `CHUNK_OVERLAP` no `.env`
- RN-005 exige 1000/150, mas pode testar outros valores

## Referências
- **PyPDFLoader**: https://python.langchain.com/docs/integrations/document_loaders/pypdf
- **RecursiveCharacterTextSplitter**: https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter
- **OpenAIEmbeddings**: https://python.langchain.com/docs/integrations/text_embedding/openai
- **PGVector**: https://python.langchain.com/docs/integrations/vectorstores/pgvector
