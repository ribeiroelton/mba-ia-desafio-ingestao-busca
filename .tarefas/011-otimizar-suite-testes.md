# [011] - Otimizar Suite de Testes: Reduzir Custo e Tempo de Execução

## Metadados
- **ID**: 011
- **Grupo**: Fase 3 - Qualidade e Entrega
- **Prioridade**: Alta
- **Complexidade**: Média
- **Estimativa**: 2 dias

## Descrição

Otimizar a suite de testes do projeto reduzindo o número de testes unitários redundantes e focando em testes de integração end-to-end que validem o comportamento real do sistema. O objetivo é reduzir tempo de execução e custo com APIs (OpenAI) mantendo cobertura de qualidade.

**Situação Atual**:
- 48 testes totais (38 unitários + 10 integração)
- Muitos testes unitários com mocks que não validam comportamento real
- Testes de chat com mocks do LLM não validam respostas reais
- Tempo de execução: ~84 segundos
- Custo de APIs não otimizado

**Situação Desejada**:
- ~20-25 testes totais (máximo 30)
- Foco em testes de integração E2E
- Validação com gpt-5-nano real (custo otimizado)
- Tempo de execução: ~40-50 segundos
- Cobertura >= 85%
- Menor custo total com APIs

## Requisitos

### Requisitos Funcionais
- RF-027: Suite de testes otimizada com foco em integração
- RF-028: Validação com LLM real (gpt-5-nano)
- RF-029: Cobertura de código >= 85%

### Requisitos Não-Funcionais
- RNF-021: Tempo de execução reduzido em ~40%
- RNF-022: Custo com APIs reduzido
- RNF-023: Testes mais confiáveis (menos mocks)
- RNF-024: Facilidade de manutenção

## Fonte da Informação

### Contexto Atual
- **Suite Atual**: 48 testes (38 unitários + 10 integração)
- **Testes com Mocks**: 7 testes de chat com ChatOpenAI mockado
- **Testes Redundantes**: Múltiplos testes validando mesma funcionalidade
- **Modelo LLM**: Deve usar gpt-5-nano (custo otimizado)

### Regras de Negócio Críticas
- **RN-001**: Respostas baseadas EXCLUSIVAMENTE no contexto
- **RN-002**: Mensagem padrão quando sem contexto
- **RN-006**: Busca retorna k=10 resultados

## Stack Necessária

- **Python**: 3.13.9+
- **Pytest**: 8.3.4
- **pytest-cov**: Para cobertura
- **LangChain**: 0.3.27
- **OpenAI**: gpt-5-nano (modelo de teste otimizado)
- **PostgreSQL**: 17 com pgVector (TestContainers ou Docker)

## Dependências

### Dependências Técnicas
- Tarefa 009: Validação de testes concluída
- Tarefa 010: README atualizado
- Docker/Docker Compose funcionando
- OpenAI API Key configurada
- gpt-5-nano disponível

### Dependências de Ambiente
- `.env` com `LLM_MODEL=gpt-5-nano`
- `OPENAI_API_KEY` configurada
- PostgreSQL rodando (docker-compose up)

## Critérios de Aceite

1. [ ] Reduzir de 48 para máximo 30 testes
2. [ ] Mínimo 70% dos testes devem ser de integração E2E
3. [ ] Eliminar todos os mocks de ChatOpenAI
4. [ ] Usar gpt-5-nano em todos os testes que requerem LLM
5. [ ] Cobertura de código >= 85%
6. [ ] Tempo de execução <= 50 segundos
7. [ ] Todos os testes passando
8. [ ] Validar RN-001 e RN-002 com LLM real
9. [ ] Reduzir testes unitários de formatação/validação simples
10. [ ] Manter testes críticos de regras de negócio

## Implementação Resumida

### Análise da Suite Atual

#### Testes a REMOVER (Redundantes ou de Baixo Valor)

**test_chat.py** (remover 4-5 testes):
- `test_build_prompt_format`: Validação trivial de string
- `test_build_prompt_with_special_characters`: Coberto por integração
- `test_build_prompt_with_multiline_context`: Coberto por integração
- `test_build_prompt_empty_context`: Validação trivial
- `test_system_prompt_has_required_rules`: Validação de constante

**test_ingest.py** (remover 3-4 testes):
- `test_load_pdf_invalid_extension`: Validação trivial
- `test_split_documents_single_small_document`: Redundante
- `test_split_documents_preserves_metadata`: Coberto por integração
- `test_store_in_vectorstore_empty_chunks`: Caso de erro raro

**test_search.py** (remover 4-5 testes):
- `test_semantic_search_with_custom_collection`: Redundante
- `test_search_k_respects_env_variable`: Configuração simples
- `test_get_context_format`: Validação trivial de string
- `test_search_with_special_characters`: Coberto por integração
- `test_vectorstore_connection_error`: Mock de erro de conexão

**Total a remover**: 11-14 testes unitários

#### Testes a MANTER e MELHORAR

**Testes Unitários Críticos** (8-10 testes):
- Validação de entrada (query vazia, arquivo inexistente)
- Lógica de chunking (tamanho, overlap)
- Configurações críticas (k=10 fixo)
- Tratamento de erros de negócio

**Testes de Integração E2E** (15-20 testes):
- Fluxo completo: Ingest → Search → Chat com LLM real
- Validação RN-001: Pergunta com contexto (LLM real)
- Validação RN-002: Pergunta sem contexto (LLM real)
- Validação RN-006: k=10 resultados
- Cenários críticos com dados reais

### Estrutura de Arquivos Otimizada

```
tests/
├── conftest.py                      # Fixtures compartilhadas
├── unit/                            # Testes unitários críticos (8-10)
│   ├── test_ingest_validation.py    # Validações de entrada
│   ├── test_search_validation.py    # Validações de busca
│   └── test_chat_validation.py      # Validações básicas
└── integration/                     # Testes E2E (15-20)
    ├── test_e2e_core.py            # Fluxos principais
    ├── test_business_rules.py      # RN-001, RN-002, RN-006
    └── test_real_scenarios.py      # Cenários reais com gpt-5-nano
```

### Componentes a Implementar

#### 1. Configuração para gpt-5-nano

**Arquivo**: `tests/conftest.py`

```python
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_llm_model():
    """Garante que gpt-5-nano é usado em todos os testes."""
    os.environ["LLM_MODEL"] = "gpt-5-nano"
    yield
    
@pytest.fixture
def gpt5_nano_model():
    """Retorna nome do modelo para testes."""
    return "gpt-5-nano"
```

#### 2. Testes Unitários Críticos

**Arquivo**: `tests/unit/test_ingest_validation.py`

```python
"""Testes unitários críticos para validação de ingestão."""
import pytest
from src.ingest import load_pdf, split_documents

def test_load_pdf_file_not_found():
    """Valida erro quando arquivo não existe."""
    with pytest.raises(FileNotFoundError):
        load_pdf("naoexiste.pdf")

def test_split_documents_chunk_size():
    """Valida que chunks respeitam tamanho máximo (RN-005)."""
    from langchain_core.documents import Document
    
    text = "A" * 3000
    docs = [Document(page_content=text)]
    chunks = split_documents(docs)
    
    # Chunks <= 1000 caracteres
    assert all(len(c.page_content) <= 1000 for c in chunks)
    assert len(chunks) >= 3  # Mínimo esperado para 3000 chars

def test_split_documents_overlap():
    """Valida overlap de 150 caracteres (RN-005)."""
    # Implementar validação de overlap
    pass
```

**Arquivo**: `tests/unit/test_search_validation.py`

```python
"""Testes unitários críticos para validação de busca."""
import pytest
from src.search import SemanticSearch

def test_search_empty_query():
    """Valida erro com query vazia."""
    searcher = SemanticSearch()
    
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.search("")

def test_search_k_fixed_10():
    """Valida que k=10 é fixo (RN-006)."""
    searcher = SemanticSearch()
    assert searcher.k == 10
```

**Arquivo**: `tests/unit/test_chat_validation.py`

```python
"""Testes unitários críticos para validação de chat."""
from src.chat import build_prompt, SYSTEM_PROMPT

def test_system_prompt_contains_rules():
    """Valida que SYSTEM_PROMPT contém regras críticas."""
    assert "EXCLUSIVAMENTE" in SYSTEM_PROMPT
    assert "Não tenho informações necessárias" in SYSTEM_PROMPT

def test_build_prompt_structure():
    """Valida estrutura do prompt."""
    context = "Contexto de teste"
    question = "Pergunta teste"
    
    prompt = build_prompt(context, question)
    
    assert "CONTEXTO:" in prompt
    assert context in prompt
    assert question in prompt
```

#### 3. Testes de Integração E2E com LLM Real

**Arquivo**: `tests/integration/test_business_rules.py`

```python
"""Testes de integração para regras de negócio com LLM real."""
import pytest
from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm

@pytest.fixture(scope="module")
def ingested_test_doc(sample_pdf_path, clean_test_collection):
    """Ingere documento de teste uma vez para todos os testes."""
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, "test_business_rules")
    yield
    # Cleanup após todos os testes do módulo

def test_rn001_answer_with_context(ingested_test_doc):
    """
    RN-001: Respostas baseadas EXCLUSIVAMENTE no contexto.
    
    Cenário: Documento contém informação específica
    Query: Pergunta sobre informação presente
    Expected: Resposta correta baseada no documento (LLM real)
    """
    searcher = SemanticSearch(collection_name="test_business_rules")
    context = searcher.get_context("Qual informação está no documento?")
    
    # Usar gpt-5-nano REAL
    response = ask_llm(
        question="Qual informação está no documento?",
        context=context
    )
    
    # Validações
    assert isinstance(response, str)
    assert len(response) > 0
    # Resposta não deve ser mensagem padrão
    assert "Não tenho informações necessárias" not in response

def test_rn002_no_context_standard_message(ingested_test_doc):
    """
    RN-002: Mensagem padrão quando informação não disponível.
    
    Cenário: Pergunta completamente fora do contexto
    Query: "Qual é a capital da França?" (não está no doc)
    Expected: "Não tenho informações necessárias..." (LLM real)
    """
    searcher = SemanticSearch(collection_name="test_business_rules")
    context = searcher.get_context("Qual é a capital da França?")
    
    # Usar gpt-5-nano REAL
    response = ask_llm(
        question="Qual é a capital da França?",
        context=context
    )
    
    # Validar mensagem padrão
    assert "Não tenho informações necessárias" in response

def test_rn006_search_returns_k10(ingested_test_doc):
    """
    RN-006: Busca retorna exatamente 10 resultados (k=10).
    
    Expected: Máximo 10 chunks retornados
    """
    searcher = SemanticSearch(collection_name="test_business_rules")
    results = searcher.search("teste query genérica")
    
    assert len(results) <= 10
    assert searcher.k == 10
```

**Arquivo**: `tests/integration/test_e2e_core.py`

```python
"""Testes E2E do fluxo completo com LLM real."""
import pytest
from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm

def test_e2e_complete_flow_with_real_llm(sample_pdf_path, clean_test_collection):
    """
    Teste E2E completo: Ingest → Search → Chat com gpt-5-nano real.
    
    Fluxo:
    1. Ingerir PDF
    2. Buscar contexto relevante
    3. Gerar resposta com LLM real
    4. Validar resposta
    """
    # 1. Ingestão
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, "test_e2e_core")
    
    assert len(chunks) > 0
    
    # 2. Busca
    searcher = SemanticSearch(collection_name="test_e2e_core")
    context = searcher.get_context("Qual é o conteúdo principal?")
    
    assert len(context) > 0
    
    # 3. Chat com LLM REAL (gpt-5-nano)
    response = ask_llm(
        question="Qual é o conteúdo principal?",
        context=context
    )
    
    # 4. Validações
    assert isinstance(response, str)
    assert len(response) > 10  # Resposta substantiva
    assert response != ""

def test_e2e_multiple_queries_same_session(sample_pdf_path, clean_test_collection):
    """
    Teste E2E: Múltiplas queries na mesma sessão.
    
    Valida:
    - Consistência de resultados
    - Performance de queries sequenciais
    - Qualidade de respostas com LLM real
    """
    # Setup
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, "test_multiple_queries")
    
    searcher = SemanticSearch(collection_name="test_multiple_queries")
    
    # Query 1: Com contexto
    context1 = searcher.get_context("Primeira pergunta sobre o documento")
    response1 = ask_llm("Primeira pergunta sobre o documento", context1)
    
    assert len(response1) > 0
    
    # Query 2: Sem contexto (fora do doc)
    context2 = searcher.get_context("Qual é a capital do Brasil?")
    response2 = ask_llm("Qual é a capital do Brasil?", context2)
    
    assert "Não tenho informações necessárias" in response2
    
    # Query 3: Com contexto novamente
    context3 = searcher.get_context("Terceira pergunta sobre o documento")
    response3 = ask_llm("Terceira pergunta sobre o documento", context3)
    
    assert len(response3) > 0
```

**Arquivo**: `tests/integration/test_real_scenarios.py`

```python
"""Testes de cenários reais com gpt-5-nano."""
import pytest
from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm

@pytest.fixture(scope="module")
def real_scenario_collection(sample_pdf_path):
    """Setup para cenários reais."""
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, "real_scenarios")
    yield "real_scenarios"

def test_scenario_ambiguous_question(real_scenario_collection):
    """
    Cenário: Pergunta ambígua que requer interpretação.
    
    Expected: LLM real interpreta contexto e responde adequadamente
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    context = searcher.get_context("Me fale sobre isso")
    
    response = ask_llm("Me fale sobre isso", context)
    
    # LLM deve responder baseado no contexto ou informar falta de clareza
    assert len(response) > 0
    assert isinstance(response, str)

def test_scenario_llm_follows_system_prompt(real_scenario_collection):
    """
    Cenário: Validar que LLM segue SYSTEM_PROMPT.
    
    Query sobre algo fora do contexto deve retornar mensagem padrão.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Perguntas claramente fora do contexto
    out_of_context_questions = [
        "Quem foi o primeiro presidente dos Estados Unidos?",
        "Como fazer um bolo de chocolate?",
        "Qual é a fórmula da água?"
    ]
    
    for question in out_of_context_questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        
        # LLM DEVE seguir SYSTEM_PROMPT
        assert "Não tenho informações necessárias" in response, \
            f"LLM não seguiu SYSTEM_PROMPT para: {question}"

def test_scenario_context_length_handling(real_scenario_collection):
    """
    Cenário: Query que retorna muito contexto (k=10 chunks).
    
    Expected: LLM processa contexto completo e responde adequadamente
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Query genérica que deve retornar múltiplos chunks
    context = searcher.get_context("resumo completo")
    
    # Contexto deve conter múltiplos chunks
    assert "[Chunk" in context  # Formato esperado
    
    response = ask_llm("Faça um resumo do conteúdo", context)
    
    # LLM deve processar e resumir
    assert len(response) > 50
    assert isinstance(response, str)
```

### Otimizações de Performance

#### 1. Fixtures com Escopo de Módulo

```python
# tests/conftest.py

@pytest.fixture(scope="module")
def shared_test_collection():
    """
    Cria coleção de teste uma vez por módulo.
    
    Reduz tempo de setup repetido.
    """
    collection_name = f"test_{uuid.uuid4().hex[:8]}"
    # Setup
    yield collection_name
    # Cleanup
```

#### 2. Paralelização de Testes

```bash
# pytest.ini
[pytest]
addopts = -n auto  # pytest-xdist para paralelização
```

#### 3. Cache de Embeddings (Futuro)

```python
# Considerar cache de embeddings para queries repetidas
# em ambiente de teste (não implementar agora)
```

### Regras de Negócio a Implementar

- **RN-001**: Validar com LLM REAL que respostas são baseadas no contexto
- **RN-002**: Validar com LLM REAL mensagem padrão quando sem contexto
- **RN-006**: Validar k=10 em testes de integração

### Validações Necessárias

1. **Validação de Custo**:
   - Contar chamadas de API por teste
   - Estimar custo total da suite
   - Validar uso de gpt-5-nano (mais barato)

2. **Validação de Tempo**:
   - Tempo total <= 50 segundos
   - Testes unitários: < 5 segundos total
   - Testes integração: < 45 segundos total

3. **Validação de Cobertura**:
   - Cobertura >= 85%
   - Todas as funções críticas cobertas
   - Regras de negócio cobertas

### Tratamento de Erros

1. **Erro de API OpenAI**:
   - Skip test se API indisponível (usar `pytest.mark.skipif`)
   - Retry automático (1 tentativa)
   - Mensagem clara de erro

2. **Timeout de LLM**:
   - Timeout de 30 segundos por chamada
   - Falhar gracefully com mensagem clara

3. **Erro de Conexão com Banco**:
   - Verificar PostgreSQL antes de rodar testes
   - Skip testes de integração se banco indisponível

## Testes de Qualidade e Cobertura

### Validação Pré-Otimização

```bash
# Executar suite atual e medir
pytest tests/ -v --durations=10 --cov=src --cov-report=term

# Resultado esperado (atual):
# - 48 testes
# - Tempo: ~84 segundos
# - Cobertura: ~97%
```

### Validação Pós-Otimização

```bash
# Executar suite otimizada
pytest tests/ -v --durations=10 --cov=src --cov-report=term

# Resultado esperado (otimizado):
# - 20-30 testes
# - Tempo: 40-50 segundos
# - Cobertura: >= 85%
# - Menos warnings
```

### Testes de Integração com gpt-5-nano

**Cenários Obrigatórios**:

1. **Teste RN-001**: Pergunta com contexto
   - Input: Documento ingerido + pergunta relevante
   - Expected: Resposta baseada no documento (validar com assertions)

2. **Teste RN-002**: Pergunta sem contexto
   - Input: Documento ingerido + pergunta irrelevante
   - Expected: "Não tenho informações necessárias..."

3. **Teste RN-006**: k=10 resultados
   - Input: Query genérica
   - Expected: Máximo 10 chunks retornados

4. **Teste E2E Completo**:
   - Input: PDF → Ingest → Search → Chat
   - Expected: Fluxo completo funciona com LLM real

### Métricas de Sucesso

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Total de Testes | 48 | 20-30 | ~40% redução |
| Testes Unitários | 38 | 8-10 | ~75% redução |
| Testes Integração | 10 | 15-20 | 50-100% aumento |
| Tempo Execução | ~84s | ~40-50s | ~40% redução |
| Cobertura | 97% | >= 85% | Aceitável |
| Chamadas LLM | ~7 (mock) | 15-20 (real) | Real validation |
| Custo/Execução | $0 | ~$0.02-0.05 | Mínimo com gpt-5-nano |

## Documentação Necessária

### Código

- [ ] Docstrings em novas fixtures
- [ ] Comentários explicando escolhas de otimização
- [ ] README de testes atualizado

### README Principal

Atualizar seção de testes:

```markdown
## 🧪 Testes

### Suite Otimizada

Nossa suite de testes foi otimizada para:
- **Foco em Integração**: 70% testes E2E
- **Validação Real**: Usa gpt-5-nano para validar comportamento
- **Performance**: Execução em ~40-50 segundos
- **Custo Controlado**: ~$0.02-0.05 por execução completa

### Executar Testes

\`\`\`bash
# Todos os testes (unitários + integração)
pytest

# Somente unitários (rápido, sem custo)
pytest tests/unit/ -v

# Somente integração (validação completa)
pytest tests/integration/ -v

# Com cobertura
pytest --cov=src --cov-report=html
\`\`\`

### Configuração para Testes

\`\`\`bash
# Variáveis necessárias em .env
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-5-nano  # Modelo otimizado para testes
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
\`\`\`
```

### Documentação Técnica

**Arquivo**: `tests/README.md`

```markdown
# Documentação de Testes

## Estrutura

- `unit/`: Testes unitários críticos (validações, erros)
- `integration/`: Testes E2E com LLM real

## Filosofia

- **Menos é Mais**: Testes focados em valor
- **Real > Mock**: Validação com APIs reais
- **Fast Feedback**: Unitários rápidos, integração completa

## Modelo LLM

Usamos **gpt-5-nano** para testes por:
- Custo otimizado (~10x mais barato que gpt-4)
- Velocidade adequada
- Qualidade suficiente para validação

## Executar

\`\`\`bash
# Unitários (sem custo, < 5s)
pytest tests/unit/ -v

# Integração (custo mínimo, ~40s)
pytest tests/integration/ -v
\`\`\`
```

## Checklist de Finalização

- [ ] Suite reduzida de 48 para 20-30 testes
- [ ] Testes unitários reduzidos para 8-10 (críticos)
- [ ] Testes integração aumentados para 15-20
- [ ] Todos os mocks de ChatOpenAI removidos
- [ ] gpt-5-nano configurado e validado
- [ ] RN-001 validada com LLM real
- [ ] RN-002 validada com LLM real
- [ ] RN-006 validada
- [ ] Cobertura >= 85%
- [ ] Tempo execução <= 50 segundos
- [ ] Todos os testes passando
- [ ] README atualizado
- [ ] Documentação de testes criada
- [ ] Métricas de sucesso validadas

## Notas Adicionais

### Custo Estimado

**gpt-5-nano** (assumindo preços hipotéticos):
- Input: ~$0.10 / 1M tokens
- Output: ~$0.30 / 1M tokens

**Estimativa por execução**:
- 15-20 chamadas de LLM
- ~500 tokens input/chamada
- ~200 tokens output/chamada
- Total: ~10-15K tokens por execução
- **Custo: ~$0.02-0.05 por execução completa**

Execuções diárias: 10-20
**Custo mensal estimado: $6-30** (aceitável)

### Armadilhas Conhecidas

1. **Rate Limiting**: OpenAI pode limitar taxa de requisições
   - Solução: Adicionar retry com backoff

2. **Variabilidade de LLM**: Respostas podem variar
   - Solução: Usar assertions flexíveis (contains, not exact match)

3. **Tempo de Timeout**: LLM pode demorar
   - Solução: Timeout de 30s por teste

### Próximas Otimizações (Futuro)

1. Cache de embeddings para testes
2. Fixtures com lazy loading
3. Paralelização de testes de integração
4. Mock seletivo para desenvolvimento local

## Referências

- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Integration Testing Guide](https://martinfowler.com/bliki/IntegrationTest.html)
- [gpt-5-nano Documentation](https://platform.openai.com/docs/models) (verificar disponibilidade)
- [LangChain Testing](https://python.langchain.com/docs/contributing/testing)

## Exemplo de Execução

```bash
# 1. Limpar ambiente
docker-compose down -v
docker-compose up -d
sleep 10

# 2. Ativar venv
source .venv/bin/activate

# 3. Rodar testes otimizados
pytest tests/ -v --cov=src --cov-report=term --durations=10

# Output esperado:
# ======================== 25 passed in 45.2s =========================
# Coverage: 87%
# Slowest tests:
#   - test_rn001_answer_with_context: 3.2s
#   - test_rn002_no_context_standard_message: 2.8s
#   - test_e2e_complete_flow_with_real_llm: 4.5s
```
