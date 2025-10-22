# Sistema RAG - Ingestão e Busca Semântica

![Python](https://img.shields.io/badge/python-3.13.9-blue)
![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-17-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema de Retrieval Augmented Generation (RAG) para ingestão de documentos PDF e consultas semânticas usando LangChain, OpenAI e PostgreSQL com pgVector.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#️-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
  - [Ingestão de PDFs](#ingestão-de-pdfs)
  - [Chat Interativo](#chat-interativo)
- [Casos de Teste](#-casos-de-teste)
- [Testes](#-testes)
- [Troubleshooting](#-troubleshooting)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Regras de Negócio](#-regras-de-negócio)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

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
git clone https://github.com/ribeiroelton/mba-ia-desafio-ingestao-busca.git
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
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Modelos (opcional)
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-5-nano
```

## 🎮 Uso

### Ingestão de PDFs

Ingira um ou mais documentos PDF:

```bash
# Ingerir um PDF
python src/ingest.py relatorio_financeiro.pdf

```

**Saída esperada**:
```
📄 Carregando PDF: relatorio_financeiro.pdf
✓ 15 páginas carregadas
✂️  Dividindo em chunks (size=1000, overlap=150)
✓ 45 chunks criados
💾 Armazenando embeddings no PGVector...
✓ Embeddings armazenados com sucesso
✅ Ingestão concluída!
```

### Chat Interativo

Inicie o chat para fazer perguntas:

```bash
# Chat padrão
python src/chat.py
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
pytest tests/ -v -k "not integration"

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
3. Testar com modelo mais recente (gpt-5-nano)

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
│   ├── __init__.py
│   ├── ingest.py                      # Ingestão de PDFs
│   ├── search.py                      # Busca semântica
│   └── chat.py                        # Interface CLI
├── tests/
│   ├── conftest.py                    # Fixtures
│   ├── test_ingest.py                 # Testes unitários
│   ├── test_search.py                 # Testes unitários
│   ├── test_chat.py                   # Testes unitários
│   └── integration/                   # Testes de integração
│       └── test_scenarios.py
├── scripts/
│   ├── run_full_validation.sh         # Validação completa
│   └── analyze_coverage.py            # Análise de cobertura
├── docker-compose.yaml                # PostgreSQL + pgVector
├── requirements.txt                   # Dependências Python
├── .env                               # Variáveis de ambiente
├── .env.example                       # Template de variáveis
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
