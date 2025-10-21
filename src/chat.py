"""
Interface CLI interativa para consultas ao sistema RAG.

Permite fazer perguntas em linguagem natural e receber respostas
baseadas no conteúdo dos documentos ingeridos.
"""

import os
import sys

import typer
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.search import SemanticSearch

load_dotenv()

app = typer.Typer()


SYSTEM_PROMPT = """Você é um assistente que responde perguntas baseado EXCLUSIVAMENTE no contexto fornecido.

REGRAS OBRIGATÓRIAS:
1. Responda SOMENTE com base no CONTEXTO fornecido
2. Se a informação NÃO estiver explicitamente no CONTEXTO, responda:
   "Não tenho informações necessárias para responder sua pergunta."
3. NUNCA invente ou use conhecimento externo
4. NUNCA produza opiniões ou interpretações além do que está escrito
5. Seja direto e objetivo na resposta

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."
"""


def build_prompt(context: str, question: str) -> str:
    """
    Monta prompt completo com contexto e pergunta.
    
    Args:
        context: Contexto recuperado do vectorstore
        question: Pergunta do usuário
        
    Returns:
        Prompt formatado
    """
    return f"""CONTEXTO:
{context}

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO":"""


def ask_llm(question: str, context: str) -> str:
    """
    Envia pergunta ao LLM com contexto.
    
    Args:
        question: Pergunta do usuário
        context: Contexto recuperado
        
    Returns:
        Resposta do LLM
    """
    llm_model = os.getenv("LLM_MODEL", "gpt-5-mini")
    
    llm = ChatOpenAI(
        model=llm_model,
        temperature=0,  # Determinístico
    )
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=build_prompt(context, question))
    ]
    
    response = llm.invoke(messages)
    return response.content


@app.command()
def main(
    collection: str = typer.Option("rag_documents", help="Coleção no banco"),
):
    """
    Inicia chat interativo com o sistema RAG.
    
    Comandos especiais:
    - quit, exit, sair: Encerra o chat
    
    Exemplo:
        python src/chat.py
    """
    typer.echo("🤖 Sistema de Busca Semântica")
    typer.echo("=" * 50)
    typer.echo("Digite 'quit', 'exit' ou 'sair' para encerrar\n")
    
    try:
        # Inicializar busca
        searcher = SemanticSearch(collection_name=collection)
        
        while True:
            # Solicitar pergunta
            question = typer.prompt("\n💬 Faça sua pergunta")
            
            # Comandos de saída
            if question.lower() in ["quit", "exit", "sair"]:
                typer.echo("\n👋 Até logo!")
                break
            
            # Validar pergunta
            if not question.strip():
                typer.echo("⚠️  Pergunta vazia. Tente novamente.")
                continue
            
            try:
                typer.echo("\n🔍 Buscando informações...")
                
                # Buscar contexto
                context = searcher.get_context(question)
                
                if not context:
                    typer.echo("⚠️  Nenhum contexto encontrado no banco de dados.")
                    typer.echo("   Certifique-se de ter ingerido documentos primeiro.")
                    continue
                
                typer.echo("💭 Gerando resposta...")
                
                # Perguntar ao LLM
                answer = ask_llm(question, context)
                
                # Exibir resposta
                typer.echo("\n📝 RESPOSTA:")
                typer.echo("-" * 50)
                typer.echo(answer)
                typer.echo("-" * 50)
                
            except Exception as e:
                typer.echo(f"\n❌ Erro ao processar pergunta: {e}", err=True)
                typer.echo("Tente novamente ou digite 'quit' para sair.")
                
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Interrompido pelo usuário. Até logo!")
        sys.exit(0)
    except Exception as e:
        typer.echo(f"\n❌ Erro fatal: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
