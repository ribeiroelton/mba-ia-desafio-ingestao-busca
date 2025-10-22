# [010] - Documentar README e Guia de Uso

## Metadados
- **ID**: 010
- **Grupo**: Fase 3 - Qualidade e Entrega
- **Prioridade**: Alta
- **Complexidade**: Baixa
- **Estimativa**: 1 dia

## Descrição
Criar README.md completo com visão geral do projeto, instruções detalhadas de instalação, configuração, uso (ingestão e chat), troubleshooting, exemplos práticos e referências.

## Requisitos

### Requisitos Funcionais
- RF-024: Documentação completa do projeto
- RF-025: Guia de instalação
- RF-026: Guia de uso

### Requisitos Não-Funcionais
- RNF-019: Documentação clara e objetiva
- RNF-020: Exemplos práticos funcionais

## Fonte da Informação
- **Seção 1**: Visão Geral do Projeto
- **Seção 3**: Arquitetura e Componentes
- **Seção 6**: Modelo de Dados
- **Seção 8**: Infraestrutura e Deploy

## Stack Necessária
- Markdown

## Dependências

### Dependências Técnicas
- Todas as tarefas anteriores concluídas
- Sistema funcional e testado

## Critérios de Aceite

1. [x] README.md criado na raiz
2. [x] Seção de visão geral
3. [x] Seção de arquitetura
4. [x] Instruções de instalação
5. [x] Guia de configuração
6. [x] Exemplos de uso (ingestão)
7. [x] Exemplos de uso (chat)
8. [x] Seção de troubleshooting
9. [x] Documentação de testes
10. [x] Badges e referências

## Implementação Resumida

### README Principal

**Arquivo**: `README.md`

```markdown
# Sistema RAG - Ingestão e Busca Semântica

![Python](https://img.shields.io/badge/python-3.13.9-blue)
![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-17-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema de Retrieval Augmented Generation (RAG) para ingestão de documentos PDF e consultas semânticas usando LangChain, OpenAI e PostgreSQL com pgVector.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
  - [Ingestão de PDFs](#ingestão-de-pdfs)
  - [Chat Interativo](#chat-interativo)
- [Casos de Teste](#casos-de-teste)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Regras de Negócio](#regras-de-negócio)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Visão Geral

Este sistema implementa um pipeline completo de RAG:

1. **Ingestão**: Processa PDFs, divide em chunks e armazena embeddings no PostgreSQL
2. **Busca Semântica**: Encontra os 10 trechos mais relevantes por similaridade
3. **Chat**: Interface CLI que responde perguntas baseado EXCLUSIVAMENTE no contexto recuperado

### Principais Características

- ✅ Respostas baseadas **exclusivamente** no contexto dos documentos
- ✅ Mensagem padrão quando informação não está disponível
- ✅ Chunking inteligente (1000 chars, overlap 150)
- ✅ Busca por similaridade de cosseno (top k=10)
- ✅ Interface CLI intuitiva
- ✅ Testes automatizados com cobertura >= 80%

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  ingest.py  │─────▶│  PostgreSQL  │◀─────│  search.py  │
│ (PDFs → DB) │      │  + pgVector  │      │ (Busca)     │
└─────────────┘      └──────────────┘      └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │  chat.py    │
                                            │  (CLI)      │
                                            └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │ OpenAI LLM  │
                                            │ (Resposta)  │
                                            └─────────────┘
```

### Componentes

- **ingest.py**: Carrega PDFs, gera chunks e embeddings, armazena no banco
- **search.py**: Busca semântica com k=10 fixo
- **chat.py**: Interface CLI para perguntas e respostas
- **PostgreSQL + pgVector**: Armazenamento de embeddings
- **OpenAI**: Embeddings (text-embedding-3-small) e LLM (gpt-5-nano)

## 🚀 Funcionalidades

### UC-001: Ingestão de Documentos
- Carrega arquivos PDF
- Divide em chunks de 1000 caracteres (overlap 150)
- Gera embeddings com OpenAI
- Armazena no PostgreSQL com pgVector

### UC-002: Consulta Semântica
- Busca por similaridade de cosseno
- Retorna top 10 trechos mais relevantes
- Concatena contexto para o LLM

### UC-003: Validação de Contexto
- Respostas baseadas **exclusivamente** no contexto
- Mensagem padrão quando informação não disponível:
  > "Não tenho informações necessárias para responder sua pergunta."

## 📦 Pré-requisitos

- **Python**: 3.13.9
- **Docker**: Para PostgreSQL
- **OpenAI API Key**: Para embeddings e LLM

## 🔧 Instalação

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd mba-ia-desafio-ingestao-busca
```

### 2. Configure PostgreSQL com Docker

```bash
docker-compose up -d
```

Isso inicia PostgreSQL 17 com pgVector na porta 5432.

### 3. Configure Ambiente Python

```bash
# Criar ambiente virtual
python3.13 -m venv .venv

# Ativar ambiente
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configure Variáveis de Ambiente

Crie arquivo `.env` na raiz:

```bash
# PostgreSQL
CONNECTION_STRING=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Modelos (opcional)
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-5-nano
```

### 5. Valide Instalação

```bash
python -c "
import sys
import langchain
import typer
import psycopg
from langchain_openai import OpenAIEmbeddings

print(f'✅ Python: {sys.version}')
print(f'✅ LangChain: {langchain.__version__}')
print(f'✅ Typer instalado')
print(f'✅ Psycopg instalado')
print('✅ Instalação OK')
"
```

## ⚙️ Configuração

### Arquivo docker-compose.yaml

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: rag-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: rag
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Arquivo requirements.txt

```
langchain==0.3.27
langchain-openai==0.3.1
langchain-postgres==0.0.17
langchain-community==0.3.9
langchain-text-splitters==0.3.5
psycopg==3.2.11
psycopg-binary==3.2.11
psycopg-pool==3.2.5
pypdf==5.1.0
typer==0.20.0
python-dotenv==1.0.1
pytest==8.3.4
pytest-cov==6.0.0
```

## 🎮 Uso

### Ingestão de PDFs

Ingira um ou mais documentos PDF:

```bash
# Ingerir um PDF
python src/ingest.py documento.pdf

# Com coleção customizada
python src/ingest.py documento.pdf --collection minha_colecao

# Exemplo real
python src/ingest.py relatorio_financeiro.pdf
```

**Saída esperada**:
```
📄 Processando: relatorio_financeiro.pdf
✅ 15 chunks criados
💾 Armazenando embeddings no banco...
✅ Ingestão concluída com sucesso!
```

### Chat Interativo

Inicie o chat para fazer perguntas:

```bash
# Chat padrão
python src/chat.py

# Com coleção específica
python src/chat.py --collection minha_colecao
```

**Exemplo de interação**:
```
🤖 Sistema de Busca Semântica
==================================================
Digite 'quit', 'exit' ou 'sair' para encerrar

💬 Faça sua pergunta: Qual foi o faturamento da empresa?

🔍 Buscando informações...
💭 Gerando resposta...

📝 RESPOSTA:
--------------------------------------------------
O faturamento da empresa foi de 10 milhões de reais em 2024.
--------------------------------------------------

💬 Faça sua pergunta: Qual é a capital da França?

🔍 Buscando informações...
💭 Gerando resposta...

📝 RESPOSTA:
--------------------------------------------------
Não tenho informações necessárias para responder sua pergunta.
--------------------------------------------------

💬 Faça sua pergunta: quit

👋 Até logo!
```

## 🧪 Casos de Teste

### CT-001: Pergunta com Contexto ✅

**Cenário**: Documento contém "Faturamento foi 10 milhões"  
**Pergunta**: "Qual foi o faturamento?"  
**Resposta Esperada**: Informação correta do documento  

### CT-002: Pergunta sem Contexto ✅

**Cenário**: Documento sobre empresa, pergunta sobre capital de país  
**Pergunta**: "Qual é a capital da França?"  
**Resposta Esperada**: "Não tenho informações necessárias para responder sua pergunta."

### CT-003: Informação Parcial ✅

**Cenário**: Documento tem informação limitada  
**Pergunta**: Requer informação não disponível  
**Resposta Esperada**: Resposta com informação disponível ou admissão de limitação

## 🧪 Testes

### Executar Todos os Testes

```bash
# Suite completa
pytest

# Somente unitários
pytest tests/unit/ -v

# Somente integração
pytest tests/integration/ -v

# Com cobertura
pytest --cov=src --cov-report=html

# Abrir relatório
open htmlcov/index.html
```

### Validação Completa

```bash
# Script de validação automática
chmod +x scripts/run_full_validation.sh
./scripts/run_full_validation.sh
```

## 🔧 Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'langchain'`

**Solução**:
```bash
pip install -r requirements.txt
```

### Problema: `psycopg.OperationalError: connection refused`

**Solução**:
1. Verifique se PostgreSQL está rodando:
   ```bash
   docker ps | grep rag-postgres
   ```
2. Se não estiver, inicie:
   ```bash
   docker-compose up -d
   ```

### Problema: `AuthenticationError: Invalid API key`

**Solução**:
1. Verifique se `.env` existe
2. Verifique se `OPENAI_API_KEY` está configurada
3. Valide a key em: https://platform.openai.com/api-keys

### Problema: LLM não segue regras (inventa respostas)

**Solução**:
1. Verificar `SYSTEM_PROMPT` em `src/chat.py`
2. Ajustar temperatura para 0 (determinístico)
3. Testar com modelo mais recente (gpt-5-nano ou gpt-5-nano)

### Problema: Busca retorna contexto vazio

**Solução**:
1. Verifique se documentos foram ingeridos:
   ```bash
   docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
   ```
2. Se 0, ingira documentos primeiro:
   ```bash
   python src/ingest.py seu_documento.pdf
   ```

## 📁 Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── .contexto/
│   └── contexto-desenvolvimento.md    # Contexto completo do projeto
├── .tarefas/
│   ├── tarefas.md                     # Overview das tarefas
│   └── 001-010-*.md                   # Tarefas detalhadas
├── src/
│   ├── ingest.py                      # Ingestão de PDFs
│   ├── search.py                      # Busca semântica
│   └── chat.py                        # Interface CLI
├── tests/
│   ├── conftest.py                    # Fixtures
│   ├── unit/                          # Testes unitários
│   └── integration/                   # Testes de integração
├── scripts/
│   ├── run_full_validation.sh         # Validação completa
│   └── analyze_coverage.py            # Análise de cobertura
├── docs/
│   └── manual-validation-checklist.md # Checklist manual
├── docker-compose.yaml                # PostgreSQL + pgVector
├── requirements.txt                   # Dependências Python
├── .env                               # Variáveis de ambiente
├── pytest.ini                         # Configuração pytest
└── README.md                          # Este arquivo
```

## 📜 Regras de Negócio

| ID | Regra | Descrição |
|----|-------|-----------|
| RN-001 | Contexto Exclusivo | Respostas baseadas SOMENTE no contexto recuperado |
| RN-002 | Mensagem Padrão | "Não tenho informações necessárias..." quando sem contexto |
| RN-003 | Chunk Size | 1000 caracteres, overlap 150 |
| RN-004 | Similaridade | Cosine distance |
| RN-005 | Embeddings | OpenAI text-embedding-3-small |
| RN-006 | Top K | Fixo em 10 resultados |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes

- Adicione testes para novas funcionalidades
- Mantenha cobertura >= 80%
- Siga PEP 8 para estilo de código
- Documente funções e módulos

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Referências

### Documentação
- [LangChain](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [pgVector](https://github.com/pgvector/pgvector)
- [Typer](https://typer.tiangolo.com/)

### Tutoriais
- [RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [PostgreSQL + pgVector](https://github.com/langchain-ai/langchain-postgres)
- [Pytest Guide](https://docs.pytest.org/)

---

**Desenvolvido como parte do MBA em Inteligência Artificial**

Para dúvidas ou suporte, abra uma issue no repositório.
```

## Testes de Qualidade e Cobertura

### Validar README

```bash
# Verificar links
markdown-link-check README.md

# Renderizar localmente
grip README.md
```

### Checklist de Qualidade

- [x] Markdown válido
- [x] Todos os links funcionais
- [x] Comandos testados
- [x] Exemplos executam sem erro
- [x] Badges corretos
- [x] Estrutura clara
- [x] Seções completas
- [x] Troubleshooting abrangente

## Checklist de Finalização

- [x] README.md criado
- [x] Visão geral do projeto
- [x] Diagrama de arquitetura
- [x] Instruções de instalação
- [x] Guia de configuração
- [x] Exemplos de ingestão
- [x] Exemplos de chat
- [x] Casos de teste documentados
- [x] Seção de troubleshooting
- [x] Estrutura do projeto
- [x] Regras de negócio
- [x] Badges e referências

## Referências
- **Markdown Guide**: https://www.markdownguide.org/
- **Awesome README**: https://github.com/matiassingers/awesome-readme
- **README Best Practices**: https://github.com/jehna/readme-best-practices
