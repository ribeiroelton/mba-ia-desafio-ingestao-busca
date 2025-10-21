# Stack Tecnologica

## Armazenamento
Utilizar imagem docker: pgvector/pgvector:pg17

## Linguagem
Utilizar Python 3.13.9

## Framework
Utilizar Langchain com os módulos a seguir:

langchain_text_splitters=0.3.11
langchain_openai=0.3.35
langchain_google_genai=2.1.12
langchain_postgres=0.0.16
langchain=0.3.27
langchain_core=0.3.79
langchain-community=0.4
pydantic=2.12.3

Para CLI, utilizar Typer na versão 0.20.0


Para conexão DB, utilizar psycopg

psycopg=3.2.11
psycopg-binary=3.2.11
psycopg-pool=3.2.6

## Gerenciador de pacotes
Utilizar pip

## Runtime
Docker Compose utilizando Docker Compose Specification

## LLMs
Modelo de embeddings: text-embedding-3-small
Modelo de LLM para responder: gpt-5-nano


## Padrões de Desenvolvimento
Utilizar *pythonic* como conveções utilizadas na comunidade Python
Seguir convenções de estilo do PEP 8 

## Testes
Implementar testes de cobertura para os cenários definidos no projeto.


## Estrutura
src/*.py
requirements
docker-compose.yaml
.env
.env.example
README.md
document.pdf