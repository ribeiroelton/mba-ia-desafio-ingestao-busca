# Sistema RAG - Ingestão e Busca Semântica

![Python](https://img.shields.io/badge/python-3.13.9-blue)
![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-17-blue)
![Coverage](https://img.shields.io/badge/coverage-80%25+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema de Retrieval Augmented Generation (RAG) para ingestão de documentos PDF e consultas semânticas usando LangChain, OpenAI e PostgreSQL com pgVector. Inclui framework avançado de testes com **LLM-as-a-Judge** para garantir qualidade das respostas.

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
  - [Framework LLM-as-a-Judge](#framework-llm-as-a-judge)
  - [Executando Testes](#executando-testes)
  - [Cobertura de Código](#cobertura-de-código)
- [Troubleshooting](#-troubleshooting)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Regras de Negócio](#-regras-de-negócio)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## 🎯 Visão Geral

Este sistema implementa um pipeline completo de RAG com foco em **qualidade e confiabilidade**:

1. **Ingestão**: Processa PDFs, divide em chunks e armazena embeddings no PostgreSQL
2. **Busca Semântica**: Encontra os 10 trechos mais relevantes por similaridade
3. **Chat**: Interface CLI que responde perguntas baseado EXCLUSIVAMENTE no contexto recuperado
4. **Avaliação de Qualidade**: Framework LLM-as-a-Judge para validar respostas automaticamente

### Principais Características

- ✅ Respostas baseadas **exclusivamente** no contexto dos documentos
- ✅ Mensagem padrão quando informação não está disponível
- ✅ Chunking inteligente (1000 chars, overlap 150)
- ✅ Busca por similaridade de cosseno (top k=10)
- ✅ Interface CLI intuitiva
- ✅ **Framework LLM-as-a-Judge** para avaliação automática de qualidade
- ✅ Testes automatizados com cobertura >= 80%
- ✅ Testes de integração com avaliação qualitativa de respostas

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
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │ LLM Judge   │
                                            │ (Avaliação) │
                                            └─────────────┘
```

### Componentes

- **ingest.py**: Carrega PDFs, gera chunks e embeddings, armazena no banco
- **search.py**: Busca semântica com k=10 fixo
- **chat.py**: Interface CLI para perguntas e respostas
- **PostgreSQL + pgVector**: Armazenamento de embeddings
- **OpenAI**: Embeddings (text-embedding-3-small) e LLM (gpt-5-nano)
- **LLM-as-a-Judge**: Framework de avaliação automática de qualidade

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

### UC-004: Avaliação de Qualidade (LLM-as-a-Judge)
- Avaliação automática de respostas usando segundo LLM
- Validação de aderência ao contexto
- Detecção de alucinações
- Verificação de seguimento de regras
- Análise de clareza e objetividade

## 📦 Pré-requisitos

- **Python**: 3.13.9
- **Docker**: Para PostgreSQL
- **OpenAI API Key**: Para embeddings, LLM e avaliações

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
**Validação**: LLM-as-a-Judge com score >= 70

### CT-002: Pergunta sem Contexto ✅

**Cenário**: Documento sobre empresa, pergunta sobre capital de país  
**Pergunta**: "Qual é a capital da França?"  
**Resposta Esperada**: "Não tenho informações necessárias para responder sua pergunta."  
**Validação**: Score de rule_following >= 90

### CT-003: Informação Parcial ✅

**Cenário**: Documento tem informação limitada  
**Pergunta**: Requer informação não disponível  
**Resposta Esperada**: Resposta com informação disponível ou admissão de limitação  
**Validação**: Sem alucinações (hallucination_detection >= 80)

## 🧪 Testes

### Framework LLM-as-a-Judge

Este projeto implementa um **framework avançado de avaliação** usando o padrão **LLM-as-a-Judge**, onde um segundo LLM avalia objetivamente a qualidade das respostas do sistema principal.

#### Critérios de Avaliação

O framework avalia cada resposta em **4 dimensões**:

| Critério | Peso | Descrição |
|----------|------|-----------|
| **Aderência ao Contexto** | 30% | Resposta baseada exclusivamente no contexto fornecido |
| **Detecção de Alucinação** | 30% | Ausência de informações inventadas ou inferidas |
| **Seguimento de Regras** | 25% | Aderência rigorosa ao SYSTEM_PROMPT |
| **Clareza e Objetividade** | 15% | Resposta clara, direta e completa |

#### Estrutura de Avaliação

```python
# Exemplo de uso do framework
from tests.utils.llm_evaluator import LLMEvaluator

evaluator = LLMEvaluator(threshold=70)
result = evaluator.evaluate(
    question="Qual o faturamento?",
    context="Faturamento de R$10M",
    response="O faturamento é de R$10M",
    system_prompt=SYSTEM_PROMPT
)

print(f"Score Geral: {result.overall_score}")
print(f"Passou: {result.passed}")
print(f"Feedback: {result.feedback}")
```

#### Resultado da Avaliação

Cada avaliação retorna um `EvaluationResult` com:

- **score**: Score geral (0-100)
- **criteria_scores**: Scores individuais por critério
- **feedback**: Análise detalhada em português
- **passed**: Boolean indicando se passou no threshold
- **details**: Detalhes adicionais por critério

#### Métricas de Custo

Framework para avaliação automática de qualidade:

- Modelo: gpt-5-nano
- Tokens por avaliação: ~600-900
- Custo por avaliação: ~$0.00006-0.00009

**Detalhamento por arquivo**:
- `test_llm_quality_evaluation.py`: 4 testes
- `test_real_scenarios.py`: 4 testes
- `test_business_rules.py`: 2 testes técnicos (RN-005, RN-006)
- **Total**: 10 testes de integração + 28 testes unitários = **38 testes**

### Executando Testes

```bash
# Suite completa
pytest

# Somente testes unitários
pytest tests/unit/ -v

# Somente testes de integração
pytest tests/integration/ -v

# Testes de avaliação LLM
pytest tests/integration/test_llm_quality_evaluation.py -v

# Testes unitários do framework LLM-as-a-Judge
pytest tests/unit/test_llm_evaluator_unit.py -v

# Com cobertura detalhada
pytest --cov=src --cov-report=html --cov-report=term-missing

# Abrir relatório HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Tipos de Testes

#### 1. Testes Unitários (`tests/unit/`)

Validam componentes isoladamente (28 testes):
- **test_chat_validation.py**: Validação de inputs e outputs do chat (4 testes)
- **test_ingest_validation.py**: Validação do processo de ingestão (6 testes)
- **test_search_validation.py**: Validação da busca semântica (5 testes)
- **test_llm_evaluator_unit.py**: Testes do framework de avaliação (13 testes focados)

#### 2. Testes de Integração (`tests/integration/`)

Validam fluxos completos end-to-end (10 testes):
- **test_business_rules.py**: Regras de negócio técnicas - chunking, k=10 (2 testes)
- **test_real_scenarios.py**: Cenários reais de uso (4 testes)
- **test_llm_quality_evaluation.py**: Avaliação qualitativa com LLM-as-a-Judge (4 testes)

**Nota**: Suite otimizada para remover redundâncias - de 16 para 10 testes de integração (37,5% redução) mantendo 100% de cobertura funcional.

#### 3. Testes de Qualidade LLM (`tests/integration/test_llm_quality_evaluation.py`)

Validam **aspectos qualitativos** das respostas:

```python
def test_factual_accuracy_direct_question(quality_test_collection, llm_evaluator):
    """Valida resposta factual para pergunta direta."""
    searcher = SemanticSearch(collection_name=quality_test_collection)
    question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.passed
    assert evaluation.criteria_scores["adherence_to_context"] >= 75
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
```

### Cobertura de Código

Objetivo: **>= 80% de cobertura**

```bash
# Gerar relatório de cobertura
pytest --cov=src --cov-report=html --cov-report=term-missing

# Visualizar no terminal
pytest --cov=src --cov-report=term

# Abrir relatório HTML detalhado
open htmlcov/index.html
```

#### Métricas de Cobertura

O relatório HTML mostra:
- ✅ Cobertura por arquivo
- ✅ Linhas cobertas vs não cobertas
- ✅ Branches cobertos
- ✅ Linhas específicas não testadas (destaque vermelho)

### Validação Completa

```bash
# Script de validação automática (quando disponível)
chmod +x scripts/validate.sh
./scripts/validate.sh
```

## 🔧 Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'langchain'`

**Solução**:
```bash
# Ativar ambiente virtual primeiro
source .venv/bin/activate

# Reinstalar dependências
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
3. Verifique logs:
   ```bash
   docker logs rag-postgres
   ```

### Problema: `AuthenticationError: Invalid API key`

**Solução**:
1. Verifique se `.env` existe e contém `OPENAI_API_KEY`
2. Valide a key em: https://platform.openai.com/api-keys
3. Certifique-se de que a key tem créditos disponíveis

### Problema: LLM não segue regras (inventa respostas)

**Solução**:
1. Verificar `SYSTEM_PROMPT` em `src/chat.py`
2. Ajustar temperatura para 0 (determinístico)
3. Testar com modelo mais recente (gpt-4o-mini ou gpt-4)
4. Validar com testes LLM-as-a-Judge:
   ```bash
   pytest tests/integration/test_llm_quality_evaluation.py -v
   ```

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

### Problema: Testes LLM-as-a-Judge falhando

**Possíveis causas**:
1. **API Key inválida ou sem créditos**
   ```bash
   # Verificar se API key está configurada
   echo $OPENAI_API_KEY
   ```
2. **Threshold muito alto**
   - Ajustar threshold no `LLMEvaluator` (padrão: 70)
3. **Modelo inadequado**
   - Usar gpt-4 ou gpt-4o-mini para avaliações mais precisas

## 📁 Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── .github/
│   └── prompts/
│       └── dev-python-rag.prompt.md   # Instruções para desenvolvimento
├── src/
│   ├── __init__.py
│   ├── ingest.py                      # Ingestão de PDFs
│   ├── search.py                      # Busca semântica
│   └── chat.py                        # Interface CLI
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Fixtures compartilhadas
│   ├── unit/                          # Testes unitários
│   │   ├── test_chat_validation.py
│   │   ├── test_ingest_validation.py
│   │   ├── test_search_validation.py
│   │   └── test_llm_evaluator_unit.py # Framework LLM-as-a-Judge
│   ├── integration/                   # Testes de integração
│   │   ├── test_e2e_core.py
│   │   ├── test_business_rules.py
│   │   ├── test_real_scenarios.py
│   │   └── test_llm_quality_evaluation.py  # Avaliação LLM
│   ├── utils/                         # Utilitários de teste
│   │   ├── llm_evaluator.py          # LLM-as-a-Judge framework
│   │   └── evaluation_criteria.py    # Critérios de avaliação
│   └── fixtures/                      # Fixtures de teste
├── scripts/
│   └── validate.sh                    # Validação completa
├── htmlcov/                           # Relatório de cobertura
├── docker-compose.yaml                # PostgreSQL + pgVector
├── init.sql                           # Inicialização do banco
├── requirements.txt                   # Dependências Python
├── pytest.ini                         # Configuração pytest
├── .env                               # Variáveis de ambiente
├── LICENSE                            # Licença MIT
└── README.md                          # Este arquivo
```

## 📜 Regras de Negócio

| ID | Regra | Descrição | Teste |
|----|-------|-----------|-------|
| RN-001 | Contexto Exclusivo | Respostas baseadas SOMENTE no contexto recuperado | `test_business_rules.py` |
| RN-002 | Mensagem Padrão | "Não tenho informações necessárias..." quando sem contexto | `test_llm_quality_evaluation.py` |
| RN-003 | Chunk Size | 1000 caracteres, overlap 150 | `test_ingest_validation.py` |
| RN-004 | Similaridade | Cosine distance | `test_search_validation.py` |
| RN-005 | Embeddings | OpenAI text-embedding-3-small | `test_e2e_core.py` |
| RN-006 | Top K | Fixo em 10 resultados | `test_search_validation.py` |
| RN-007 | Avaliação LLM | Score >= 70 para respostas aceitáveis | `test_llm_quality_evaluation.py` |
| RN-008 | Sem Alucinação | Detecção de alucinação >= 80 | `test_llm_quality_evaluation.py` |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes

- ✅ Adicione testes para novas funcionalidades
- ✅ Mantenha cobertura >= 80%
- ✅ Siga PEP 8 para estilo de código
- ✅ Documente funções e módulos (Google style)
- ✅ Use type hints em funções públicas
- ✅ Valide qualidade com LLM-as-a-Judge quando aplicável
- ✅ Execute `pytest` antes de commitar

### Executar Todos os Checks

```bash
# Testes completos
pytest --cov=src --cov-report=html

# Verificar cobertura >= 80%
coverage report --fail-under=80

```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Referências

### Documentação

- [LangChain](https://python.langchain.com/) - Framework RAG
- [OpenAI API](https://platform.openai.com/docs) - Embeddings e LLM
- [pgVector](https://github.com/pgvector/pgvector) - Busca vetorial no PostgreSQL
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Pytest](https://docs.pytest.org/) - Framework de testes
- [LLM-as-a-Judge Pattern](https://arxiv.org/abs/2306.05685) - Padrão de avaliação

### Tutoriais

- [RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - LangChain RAG
- [PostgreSQL + pgVector](https://github.com/langchain-ai/langchain-postgres) - Integração
- [Testing LLM Applications](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation) - Métricas de avaliação
- [LLM-as-a-Judge Best Practices](https://eugeneyan.com/writing/llm-patterns/#llm-as-a-judge) - Boas práticas

### Artigos e Papers

- [Judging LLM-as-a-Judge with MT-Bench](https://arxiv.org/abs/2306.05685)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Vector Database Comparison](https://benchmark.vectorview.ai/)

---

**Desenvolvido como parte do MBA em Inteligência Artificial**

Para dúvidas ou suporte, abra uma issue no repositório.

### 🎯 Highlights do Projeto

- ✨ **Framework LLM-as-a-Judge** proprietário para avaliação automática de qualidade
- ✨ **Cobertura >= 80%** com testes unitários e de integração
- ✨ **4 dimensões de avaliação**: Contexto, Alucinação, Regras, Clareza
- ✨ **Validação automática** de respostas usando segundo LLM
- ✨ **Testes qualitativos** que vão além de validações estruturais
- ✨ **Pipeline CI/CD ready** com pytest e coverage reports
