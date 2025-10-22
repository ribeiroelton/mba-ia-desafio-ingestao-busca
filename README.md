# Sistema RAG - Ingestão e Busca Semântica# Sistema RAG - Ingestão e Busca Semântica



![Python](https://img.shields.io/badge/python-3.13+-blue)![Python](https://img.shields.io/badge/python-3.13.9-blue)

![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)

![License](https://img.shields.io/badge/license-Apache%202.0-blue)![PostgreSQL](https://img.shields.io/badge/postgresql-17-blue)

![License](https://img.shields.io/badge/license-MIT-green)

Sistema de **Retrieval Augmented Generation (RAG)** para ingestão de documentos PDF e consultas semânticas com respostas baseadas **exclusivamente** no conteúdo dos documentos.

Sistema de Retrieval Augmented Generation (RAG) para ingestão de documentos PDF e consultas semânticas usando LangChain, OpenAI e PostgreSQL com pgVector.

## 🎯 O que faz?

## 📋 Índice

1. **Ingere documentos PDF** → Divide em chunks e armazena embeddings

2. **Busca semântica** → Encontra os trechos mais relevantes- [Visão Geral](#-visão-geral)

3. **Responde perguntas** → Usa LLM baseado **exclusivamente** no contexto encontrado- [Arquitetura](#️-arquitetura)

- [Funcionalidades](#-funcionalidades)

### ✨ Características Principais- [Pré-requisitos](#-pré-requisitos)

- [Instalação](#-instalação)

- ✅ Respostas baseadas **somente** no conteúdo dos documentos- [Uso](#-uso)

- ✅ Mensagem clara quando a informação não está disponível  - [Ingestão de PDFs](#ingestão-de-pdfs)

- ✅ Interface CLI simples e intuitiva  - [Chat Interativo](#chat-interativo)

- ✅ Testes automatizados com avaliação LLM (LLM-as-a-Judge)- [Casos de Teste](#-casos-de-teste)

- [Testes](#-testes)

## 🚀 Início Rápido- [Troubleshooting](#-troubleshooting)

- [Estrutura do Projeto](#-estrutura-do-projeto)

### 1. Pré-requisitos- [Regras de Negócio](#-regras-de-negócio)

- [Contribuindo](#-contribuindo)

- Python 3.13+- [Licença](#-licença)

- Docker (para PostgreSQL)

- Chave de API da OpenAI## 🎯 Visão Geral



### 2. InstalaçãoEste sistema implementa um pipeline completo de RAG:



```bash1. **Ingestão**: Processa PDFs, divide em chunks e armazena embeddings no PostgreSQL

# Clone o repositório2. **Busca Semântica**: Encontra os 10 trechos mais relevantes por similaridade

git clone https://github.com/ribeiroelton/mba-ia-desafio-ingestao-busca.git3. **Chat**: Interface CLI que responde perguntas baseado EXCLUSIVAMENTE no contexto recuperado

cd mba-ia-desafio-ingestao-busca

### Principais Características

# Crie e ative o ambiente virtual

python3 -m venv .venv- ✅ Respostas baseadas **exclusivamente** no contexto dos documentos

source .venv/bin/activate  # Linux/Mac- ✅ Mensagem padrão quando informação não está disponível

# ou .venv\Scripts\activate no Windows- ✅ Chunking inteligente (1000 chars, overlap 150)

- ✅ Busca por similaridade de cosseno (top k=10)

# Instale as dependências- ✅ Interface CLI intuitiva

pip install -r requirements.txt- ✅ Testes automatizados com cobertura >= 80%



# Inicie o PostgreSQL## 🏗️ Arquitetura

docker-compose up -d

``````

┌─────────────┐      ┌──────────────┐      ┌─────────────┐

### 3. Configure as Variáveis de Ambiente│  ingest.py  │─────▶│  PostgreSQL  │◀─────│  search.py  │

│ (PDFs → DB) │      │  + pgVector  │      │ (Busca)     │

Crie um arquivo `.env` na raiz do projeto:└─────────────┘      └──────────────┘      └─────────────┘

                                                    │

```bash                                                    ▼

# PostgreSQL                                            ┌─────────────┐

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag                                            │  chat.py    │

                                            │  (CLI)      │

# OpenAI                                            └─────────────┘

OPENAI_API_KEY=sk-proj-sua-chave-aqui                                                    │

```                                                    ▼

                                            ┌─────────────┐

## 💡 Como Usar                                            │ OpenAI LLM  │

                                            │ (Resposta)  │

### Ingerir Documentos                                            └─────────────┘

```

```bash

# Ingerir um PDF### Componentes

python src/ingest.py documento.pdf

- **ingest.py**: Carrega PDFs, gera chunks e embeddings, armazena no banco

# Com nome de coleção personalizado- **search.py**: Busca semântica com k=10 fixo

python src/ingest.py relatorio.pdf --collection relatorios_2024- **chat.py**: Interface CLI para perguntas e respostas

```- **PostgreSQL + pgVector**: Armazenamento de embeddings

- **OpenAI**: Embeddings (text-embedding-3-small) e LLM (gpt-5-nano)

**Saída:**

```## 🚀 Funcionalidades

📄 Carregando PDF: documento.pdf

✓ 15 páginas carregadas### UC-001: Ingestão de Documentos

✂️  Dividindo em chunks...- Carrega arquivos PDF

✓ 45 chunks criados- Divide em chunks de 1000 caracteres (overlap 150)

💾 Armazenando embeddings...- Gera embeddings com OpenAI

✅ Ingestão concluída!- Armazena no PostgreSQL com pgVector

```

### UC-002: Consulta Semântica

### Fazer Perguntas (Chat)- Busca por similaridade de cosseno

- Retorna top 10 trechos mais relevantes

```bash- Concatena contexto para o LLM

# Iniciar chat

python src/chat.py### UC-003: Validação de Contexto

- Respostas baseadas **exclusivamente** no contexto

# Com coleção específica- Mensagem padrão quando informação não disponível:

python src/chat.py --collection relatorios_2024  > "Não tenho informações necessárias para responder sua pergunta."

```

## 📦 Pré-requisitos

**Exemplo de uso:**

- **Python**: 3.13.9

```- **Docker**: Para PostgreSQL

🤖 Sistema de Busca Semântica- **OpenAI API Key**: Para embeddings e LLM

Digite 'sair' para encerrar

## 🔧 Instalação

💬 Sua pergunta: Qual foi o faturamento em 2024?

### 1. Clone o Repositório

🔍 Buscando...

💭 Gerando resposta...```bash

git clone https://github.com/ribeiroelton/mba-ia-desafio-ingestao-busca.git

📝 Resposta:cd mba-ia-desafio-ingestao-busca

O faturamento da empresa em 2024 foi de 10 milhões de reais.```



💬 Sua pergunta: Qual é a capital da França?### 2. Configure PostgreSQL com Docker



📝 Resposta:```bash

Não tenho informações necessárias para responder sua pergunta.docker-compose up -d

```

💬 Sua pergunta: sair

👋 Até logo!Isso inicia PostgreSQL 17 com pgVector na porta 5432.

```

### 3. Configure Ambiente Python

## 🧪 Testes

```bash

### Executar Todos os Testes# Criar ambiente virtual

python3.13 -m venv .venv

```bash

# Suite completa (unitários + integração)# Ativar ambiente

pytestsource .venv/bin/activate  # Linux/Mac

# ou

# Apenas testes rápidos (unitários).venv\Scripts\activate     # Windows

pytest tests/unit/ -v

# Instalar dependências

# Com relatório de coberturapip install -r requirements.txt

pytest --cov=src --cov-report=html```

open htmlcov/index.html

```### 4. Configure Variáveis de Ambiente



### Validação CompletaCrie arquivo `.env` na raiz:



Use o script de validação para verificar todo o ambiente:```bash

# PostgreSQL

```bashDATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

chmod +x scripts/validate.sh

./scripts/validate.sh# OpenAI

```OPENAI_API_KEY=sk-your-key-here



Este script verifica:# Modelos (opcional)

- ✅ Dependências Python instaladasEMBEDDING_MODEL=text-embedding-3-small

- ✅ Variáveis de ambiente configuradasLLM_MODEL=gpt-5-nano

- ✅ PostgreSQL rodando e acessível```

- ✅ OpenAI API funcionando

- ✅ Todos os testes passando## 🎮 Uso



## 📋 Regras de Negócio### Ingestão de PDFs



| Regra | Descrição |Ingira um ou mais documentos PDF:

|-------|-----------|

| **RN-001** | Respostas baseadas **exclusivamente** no contexto recuperado |```bash

| **RN-002** | Mensagem padrão quando informação não disponível: _"Não tenho informações necessárias para responder sua pergunta."_ |# Ingerir um PDF

| **RN-003** | Sistema nunca usa conhecimento externo ao documento |python src/ingest.py relatorio_financeiro.pdf

| **RN-004** | Respostas objetivas e diretas |

| **RN-005** | Chunks de 1000 caracteres com overlap de 150 |# Com coleção customizada

| **RN-006** | Busca retorna exatamente 10 resultados (k=10) |python src/ingest.py documento.pdf --collection minha_colecao

```

## 🏗️ Arquitetura

**Saída esperada**:

``````

PDF → Ingestão → PostgreSQL + pgVector → Busca → LLM → Resposta📄 Carregando PDF: relatorio_financeiro.pdf

                      ↓✓ 15 páginas carregadas

                  Embeddings✂️  Dividindo em chunks (size=1000, overlap=150)

                  (OpenAI)✓ 45 chunks criados

```💾 Armazenando embeddings no PGVector...

✓ Embeddings armazenados com sucesso

**Componentes:**✅ Ingestão concluída!

- **src/ingest.py**: Processa PDFs e armazena embeddings```

- **src/search.py**: Busca semântica por similaridade

- **src/chat.py**: Interface CLI para perguntas/respostas### Chat Interativo

- **PostgreSQL + pgVector**: Armazenamento de embeddings

- **OpenAI**: Embeddings (text-embedding-3-small) + LLM (gpt-4o-mini)Inicie o chat para fazer perguntas:



## 🔧 Troubleshooting```bash

# Chat padrão

### Erro: "Connection refused" (PostgreSQL)python src/chat.py



```bash# Com coleção específica

# Verificar se está rodandopython src/chat.py --collection minha_colecao

docker ps | grep postgres```



# Iniciar se necessário**Exemplo de interação**:

docker-compose up -d```

```🤖 Sistema de Busca Semântica

==================================================

### Erro: "Invalid API key"Digite 'quit', 'exit' ou 'sair' para encerrar



1. Verifique se o arquivo `.env` existe💬 Faça sua pergunta: Qual foi o faturamento da empresa?

2. Confirme que `OPENAI_API_KEY` está configurada corretamente

3. Teste a chave em: https://platform.openai.com/api-keys🔍 Buscando informações...

💭 Gerando resposta...

### LLM inventa informações

📝 RESPOSTA:

O sistema está configurado para **nunca** usar conhecimento externo. Se isso ocorrer:--------------------------------------------------

1. Verifique o `SYSTEM_PROMPT` em `src/chat.py`O faturamento da empresa foi de 10 milhões de reais em 2024.

2. Execute os testes de integração: `pytest tests/integration/test_business_rules.py -v`--------------------------------------------------



## 📁 Estrutura do Projeto💬 Faça sua pergunta: Qual é a capital da França?



```🔍 Buscando informações...

mba-ia-desafio-ingestao-busca/💭 Gerando resposta...

├── src/

│   ├── ingest.py          # Ingestão de PDFs📝 RESPOSTA:

│   ├── search.py          # Busca semântica--------------------------------------------------

│   └── chat.py            # Interface CLINão tenho informações necessárias para responder sua pergunta.

├── tests/--------------------------------------------------

│   ├── unit/              # Testes unitários

│   ├── integration/       # Testes E2E com LLM real💬 Faça sua pergunta: quit

│   └── utils/             # Framework de avaliação LLM

├── scripts/👋 Até logo!

│   └── validate.sh        # Script de validação completa```

├── docker-compose.yaml    # PostgreSQL + pgVector

├── requirements.txt       # Dependências## 🧪 Casos de Teste

└── .env                   # Configurações (criar)

```### CT-001: Pergunta com Contexto ✅



## 📊 Métricas de Qualidade**Cenário**: Documento contém "Faturamento foi 10 milhões"  

**Pergunta**: "Qual foi o faturamento?"  

Nossa suite de testes inclui **avaliação automatizada com LLM-as-a-Judge**:**Resposta Esperada**: Informação correta do documento  



- **31 testes unitários** (validação rápida)### CT-002: Pergunta sem Contexto ✅

- **24 testes de integração** (18 com avaliação LLM)

- **Cobertura**: 64%+ (focada em código crítico)**Cenário**: Documento sobre empresa, pergunta sobre capital de país  

- **Tempo de execução**: ~50-60s**Pergunta**: "Qual é a capital da França?"  

- **Custo por execução**: ~$0.03-0.05**Resposta Esperada**: "Não tenho informações necessárias para responder sua pergunta."



Para mais detalhes, veja [tests/README.md](tests/README.md).### CT-003: Informação Parcial ✅



## 🤝 Contribuindo**Cenário**: Documento tem informação limitada  

**Pergunta**: Requer informação não disponível  

1. Fork o projeto**Resposta Esperada**: Resposta com informação disponível ou admissão de limitação

2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`

3. Commit: `git commit -m 'Adiciona nova funcionalidade'`## 🧪 Testes

4. Push: `git push origin feature/nova-funcionalidade`

5. Abra um Pull Request### Suite Otimizada



**Requisitos:**Nossa suite de testes foi otimizada para:

- Adicione testes para novas funcionalidades- **Foco em Integração**: 70% testes E2E com LLM real

- Mantenha a cobertura acima de 60%- **Validação Real**: Usa gpt-5-nano para validar comportamento autêntico

- Siga PEP 8- **Performance**: Execução em ~45-55 segundos (redução de 35%)

- **Custo Controlado**: ~$0.02-0.05 por execução completa

## 📝 Licença

### Estrutura

Apache License 2.0 - veja [LICENSE](LICENSE) para detalhes.

```

## 🔗 Links Úteistests/

├── unit/                    # Testes unitários críticos (10 testes)

- [Documentação LangChain](https://python.langchain.com/)│   ├── test_ingest_validation.py

- [OpenAI API](https://platform.openai.com/docs)│   ├── test_search_validation.py

- [pgVector](https://github.com/pgvector/pgvector)│   └── test_chat_validation.py

└── integration/             # Testes E2E (18 testes)

---    ├── test_business_rules.py    # RN-001 a RN-006

    ├── test_e2e_core.py          # Fluxos principais

**Desenvolvido como parte do MBA em Inteligência Artificial**    └── test_real_scenarios.py     # Cenários reais

```

### Executar Testes

```bash
# Todos os testes (unitários + integração)
pytest

# Somente unitários (rápido, sem custo, < 5s)
pytest tests/unit/ -v

# Somente integração (validação completa, ~40-50s)
pytest tests/integration/ -v

# Com cobertura
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Com duração dos testes
pytest --durations=10
```

### Configuração para Testes

```bash
# Variáveis necessárias em .env
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-5-nano  # Modelo otimizado para testes
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
```

### Validação de Regras de Negócio

Os testes de integração validam **todas as regras de negócio** com LLM real:

- ✅ **RN-001**: Respostas baseadas EXCLUSIVAMENTE no contexto
- ✅ **RN-002**: Mensagem padrão quando sem informação
- ✅ **RN-003**: Sistema nunca usa conhecimento externo
- ✅ **RN-005**: Chunks de 1000 chars com overlap 150
- ✅ **RN-006**: Busca retorna exatamente k=10 resultados

### Métricas

| Métrica | Valor | Observação |
|---------|-------|------------|
| **Total de Testes** | 28 | Redução de 42% (48 → 28) |
| **Testes Unitários** | 10 | Apenas validações críticas |
| **Testes Integração** | 18 | 70% da suite (real validation) |
| **Tempo Execução** | ~45-55s | Redução de 35% (77s → 50s) |
| **Cobertura** | >= 95% | Mantida acima de 85% |
| **Custo/Execução** | ~$0.03 | gpt-5-nano otimizado |

Para mais detalhes, consulte [tests/README.md](tests/README.md).

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
