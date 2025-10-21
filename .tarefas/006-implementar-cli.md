# [006] - Implementar CLI Interativo (chat.py)

## Metadados
- **ID**: 006
- **Grupo**: Fase 2 - Implementação Core RAG
- **Prioridade**: Alta
- **Complexidade**: Média
- **Estimativa**: 1 dia

## Descrição
Implementar interface CLI interativa usando Typer que recebe perguntas do usuário, usa search.py para buscar contexto, monta prompt para LLM e exibe respostas. Loop contínuo até usuário sair.

## Requisitos

### Requisitos Funcionais
- UC-002: Realizar Consulta Semântica
- RF-013: Interface CLI com Typer
- RF-014: Loop de perguntas e respostas
- RF-015: Integrar busca semântica
- RF-016: Chamar LLM (gpt-5-nano ou gpt-4o-mini)

### Requisitos Não-Funcionais
- RN-001: Respostas baseadas exclusivamente no contexto
- RN-002: Mensagem padrão quando sem informação
- RNF-012: CLI intuitivo com prompts claros
- RNF-013: Mensagens de erro descritivas

## Fonte da Informação
- **Seção 2.3**: Processo de Consulta Semântica (completo)
- **Seção 3.2**: Diagrama - chat.py com CLI (Typer)
- **Seção 4.1**: UC-002 - Realizar Consulta Semântica
- **Seção 4.1**: UC-003 - Validar Resposta Baseada em Contexto

## Stack Necessária
- **Python**: 3.13.9
- **Typer**: 0.20.0
- **LangChain**: langchain_openai (ChatOpenAI)
- **Módulos**: src/search.py

## Dependências

### Dependências Técnicas
- Tarefa 004: Ingestão implementada
- Tarefa 005: Busca implementada
- Documentos no banco

### Dependências de Negócio
- OpenAI API Key válida

## Critérios de Aceite

1. [x] `src/chat.py` implementado
2. [x] CLI com Typer funcional
3. [x] Loop de perguntas/respostas
4. [x] Integração com SemanticSearch
5. [x] Chamada ao LLM OpenAI
6. [x] Prompt com regras estritas de contexto
7. [x] Mensagem padrão para perguntas fora do contexto
8. [x] Comando para sair (quit/exit/sair)
9. [x] Mensagens claras para usuário
10. [x] Tratamento de erros robusto

## Implementação Resumida

### Arquivo Principal

**Arquivo**: `src/chat.py`

```python
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
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
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
```

## Testes de Qualidade e Cobertura

### Testes de Integração

**Arquivo**: `tests/test_chat.py`

```python
"""Testes para módulo de chat."""
import pytest
from src.chat import build_prompt, SYSTEM_PROMPT


def test_build_prompt():
    """Testa construção do prompt."""
    context = "Contexto de teste"
    question = "Pergunta de teste"
    
    prompt = build_prompt(context, question)
    
    assert "CONTEXTO:" in prompt
    assert context in prompt
    assert "PERGUNTA DO USUÁRIO:" in prompt
    assert question in prompt


def test_system_prompt_has_rules():
    """Testa que prompt do sistema tem regras."""
    assert "REGRAS OBRIGATÓRIAS" in SYSTEM_PROMPT
    assert "NUNCA invente" in SYSTEM_PROMPT
    assert "Não tenho informações necessárias" in SYSTEM_PROMPT
```

**Cenários de Teste Manual**:

1. **Cenário 1: Pergunta dentro do contexto**
   ```
   💬 Faça sua pergunta: Qual o faturamento da empresa?
   # Expected: Resposta com informação do PDF
   ```

2. **Cenário 2: Pergunta fora do contexto**
   ```
   💬 Faça sua pergunta: Qual a capital da França?
   # Expected: "Não tenho informações necessárias..."
   ```

3. **Cenário 3: Sair do chat**
   ```
   💬 Faça sua pergunta: quit
   # Expected: "👋 Até logo!"
   ```

## Checklist de Finalização

- [x] `src/chat.py` implementado
- [x] CLI com Typer
- [x] Loop interativo
- [x] Integração com SemanticSearch
- [x] Chamada ao LLM
- [x] SYSTEM_PROMPT com regras estritas
- [x] Validação de contexto
- [x] Comandos de saída (quit/exit/sair)
- [x] Tratamento de erros
- [x] Mensagens claras
- [x] Testes manuais executados

## Notas Adicionais

### Uso
```bash
# Iniciar chat
python src/chat.py

# Com coleção customizada
python src/chat.py --collection meus_docs
```

### Exemplo de Interação
```
🤖 Sistema de Busca Semântica
==================================================
Digite 'quit', 'exit' ou 'sair' para encerrar

💬 Faça sua pergunta: Qual o faturamento da empresa SuperTechIABrazil?

🔍 Buscando informações...
💭 Gerando resposta...

📝 RESPOSTA:
--------------------------------------------------
O faturamento foi de 10 milhões de reais.
--------------------------------------------------

💬 Faça sua pergunta: Quantos clientes temos?

🔍 Buscando informações...
💭 Gerando resposta...

📝 RESPOSTA:
--------------------------------------------------
Não tenho informações necessárias para responder sua pergunta.
--------------------------------------------------

💬 Faça sua pergunta: quit

👋 Até logo!
```

## Referências
- **Typer Documentation**: https://typer.tiangolo.com/
- **ChatOpenAI**: https://python.langchain.com/docs/integrations/chat/openai
