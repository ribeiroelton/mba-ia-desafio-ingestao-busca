"""
Módulo de busca semântica.

Implementa busca vetorial no PGVector para recuperar chunks relevantes.
"""

import os
from typing import List, Tuple

import typer
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

app = typer.Typer()


class SemanticSearch:
    """
    Classe para busca semântica em documentos.
    
    Attributes:
        vectorstore: Instância do PGVector
        k: Número de resultados a retornar (fixo em 10 conforme RN-006)
    """
    
    def __init__(self, collection_name: str = "rag_documents"):
        """
        Inicializa busca semântica.
        
        Args:
            collection_name: Nome da coleção no PGVector
        """
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL não configurada no .env")
        
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        embeddings = OpenAIEmbeddings(model=embedding_model)
        
        self.vectorstore = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=database_url,
            use_jsonb=True,
        )
        
        # k=10 fixo conforme RN-006
        self.k = int(os.getenv("SEARCH_K", "10"))
    
    def search(self, query: str) -> List[Tuple[Document, float]]:
        """
        Busca chunks mais similares à query.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            Lista de tuplas (documento, score) ordenada por relevância
            
        Raises:
            ValueError: Se query vazia
            Exception: Se erro na busca
        """
        if not query or not query.strip():
            raise ValueError("Query não pode ser vazia")
        
        try:
            # Busca com scores
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=self.k
            )
            
            # pgvector retorna distância (menor é melhor)
            # Ordenar por distância crescente (menor distância = mais similar)
            results_sorted = sorted(results, key=lambda x: x[1])
            
            return results_sorted
            
        except Exception as e:
            raise Exception(f"Erro na busca semântica: {e}")
    
    def get_context(self, query: str) -> str:
        """
        Busca e retorna contexto concatenado.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            String com contexto dos chunks encontrados
        """
        results = self.search(query)
        
        if not results:
            return ""
        
        # Concatenar conteúdo dos chunks
        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            context_parts.append(f"[Chunk {i}] {doc.page_content}")
        
        return "\n\n".join(context_parts)


@app.command()
def search_cmd(
    query: str = typer.Argument(..., help="Query de busca"),
    collection: str = typer.Option("rag_documents", help="Coleção no banco"),
) -> None:
    """
    Busca semântica por query.
    
    Exemplo:
        python src/search.py "Qual o faturamento da empresa?"
    """
    try:
        typer.echo(f"🔍 Buscando: {query}\n")
        
        searcher = SemanticSearch(collection_name=collection)
        results = searcher.search(query)
        
        if not results:
            typer.echo("❌ Nenhum resultado encontrado")
            return
        
        typer.echo(f"✓ {len(results)} resultados encontrados\n")
        
        for i, (doc, score) in enumerate(results, 1):
            typer.echo(f"--- Resultado {i} (score: {score:.4f}) ---")
            typer.echo(doc.page_content[:200] + "...")
            typer.echo()
            
    except Exception as e:
        typer.echo(f"❌ Erro: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
