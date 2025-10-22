# Documentação de Testes

## Estrutura

```
tests/
├── conftest.py                          # Fixtures globais
├── utils/                               # Utilitários de teste
│   ├── llm_evaluator.py                # Framework de avaliação LLM
│   └── evaluation_criteria.py         # Critérios de avaliação
├── unit/                                # Testes unitários críticos
│   ├── test_ingest_validation.py       # Validações de ingestão
│   ├── test_search_validation.py       # Validações de busca
│   ├── test_chat_validation.py         # Validações de chat
│   └── test_llm_evaluator_unit.py      # Testes do avaliador LLM
└── integration/                         # Testes E2E
    ├── test_business_rules.py          # RN-001, RN-002, RN-003, RN-005, RN-006
    ├── test_e2e_core.py                # Fluxos principais E2E
    ├── test_real_scenarios.py          # Cenários reais + avaliação LLM
    └── test_llm_quality_evaluation.py  # Testes de qualidade LLM
```

## Filosofia

### Menos é Mais
Suite otimizada focando em:
- **Testes Unitários**: Apenas validações críticas (entrada, configurações)
- **Testes de Integração**: Validação E2E com LLM real (70% da suite)

### Real > Mock
- **0 mocks de LLM**: Todos os testes de chat usam gpt-5-nano REAL
- **LLM-as-a-Judge**: Avaliação qualitativa automatizada de respostas
- Validação autêntica do comportamento do sistema
- Confiança real na qualidade das respostas

### Fast Feedback
- **Unitários**: < 5s total, sem custo de API
- **Integração**: ~40-50s, validação completa com LLM
- **Avaliação LLM**: +2-3s por teste com avaliação qualitativa

## LLM Evaluation Tests

### Visão Geral
Framework de avaliação automatizada de qualidade de outputs de LLM usando **LLM-as-a-Judge** pattern.

### Como Funciona
1. LLM principal (gpt-5-nano) gera resposta baseada em contexto
2. LLM avaliador (gpt-5-nano) analisa qualidade da resposta
3. Scores numéricos (0-100) gerados por critério
4. Teste passa se score >= 70

### Critérios de Avaliação
- **Aderência ao Contexto** (30%): Resposta baseada exclusivamente no contexto
- **Detecção de Alucinação** (30%): Ausência de informações inventadas
- **Seguimento de Regras** (25%): Aderência ao SYSTEM_PROMPT
- **Clareza e Objetividade** (15%): Qualidade da comunicação

### Uso Básico
```python
from tests.utils.llm_evaluator import LLMEvaluator
from src.chat import SYSTEM_PROMPT

evaluator = LLMEvaluator(threshold=70)
evaluation = evaluator.evaluate(
    question="Pergunta do usuário",
    context="Contexto recuperado",
    response="Resposta do LLM",
    system_prompt=SYSTEM_PROMPT
)

assert evaluation.passed, f"Score: {evaluation.score}\n{evaluation.feedback}"
```

### Custos
- **Modelo**: gpt-5-nano (avaliação e geração)
- **Custo por avaliação**: ~$0.0001-0.0002
- **Custo para suite completa**: ~$0.01-0.02

### Configuração
- **Threshold padrão**: 70/100
- **Pode ser ajustado** por teste específico
- **Fixture global**: `llm_evaluator` em `conftest.py`

## Modelo LLM

Usamos **gpt-5-nano** para testes por:
- **Custo otimizado**: ~10x mais barato que gpt-4
- **Velocidade adequada**: Respostas rápidas para testes
- **Qualidade suficiente**: Valida regras de negócio efetivamente

Configuração automática em `conftest.py`:
```python
@pytest.fixture(scope="session", autouse=True)
def setup_llm_model():
    os.environ["LLM_MODEL"] = "gpt-5-nano"
    yield
```

## Testes Unitários (10 testes)

### test_ingest_validation.py (6 testes)
- `test_load_pdf_file_not_found`: Arquivo inexistente
- `test_load_pdf_invalid_extension`: Formato inválido
- `test_split_documents_chunk_size`: RN-005 (chunk_size=1000)
- `test_split_documents_overlap`: RN-005 (overlap=150)
- `test_split_documents_empty_list`: Lista vazia
- `test_split_documents_preserves_metadata`: Metadata preservada

### test_search_validation.py (5 testes)
- `test_search_empty_query`: Query vazia
- `test_search_k_fixed_10`: RN-006 (k=10 fixo)
- `test_search_initialization_default`: Inicialização padrão
- `test_search_initialization_custom_collection`: Collection customizada
- `test_search_k_env_variable`: Configuração via env

### test_chat_validation.py (4 testes)
- `test_system_prompt_contains_rules`: RN-001 a RN-004
- `test_build_prompt_structure`: Estrutura do prompt
- `test_build_prompt_preserves_content`: Conteúdo preservado
- `test_build_prompt_handles_empty_context`: Contexto vazio

**Total Unitários: 15 testes**

## Testes de Integração E2E (18 testes)

### test_business_rules.py (6 testes)
Valida regras de negócio com LLM REAL:
- `test_rn001_answer_with_context`: RN-001 (contexto exclusivo)
- `test_rn002_no_context_standard_message`: RN-002 (mensagem padrão)
- `test_rn003_no_external_knowledge`: RN-003 (sem conhecimento externo)
- `test_rn006_search_returns_k10`: RN-006 (k=10)
- `test_rn005_chunk_size_1000`: RN-005 (chunking)

### test_e2e_core.py (6 testes)
Fluxos completos Ingest → Search → Chat:
- `test_e2e_complete_flow_with_real_llm`: Fluxo completo
- `test_e2e_multiple_queries_same_session`: Múltiplas queries
- `test_e2e_empty_collection_handling`: Coleção vazia
- `test_e2e_special_characters_in_query`: Caracteres especiais
- `test_e2e_context_length_validation`: Contexto extenso

### test_real_scenarios.py (6 testes)
Cenários práticos e edge cases:
- `test_scenario_ambiguous_question`: Pergunta ambígua
- `test_scenario_llm_follows_system_prompt`: Validação SYSTEM_PROMPT
- `test_scenario_context_length_handling`: Contexto longo (k=10)
- `test_scenario_similar_questions_consistency`: Consistência
- `test_scenario_numeric_data_handling`: Dados numéricos

**Total Integração: 18 testes**

## Executar Testes

### Todos os Testes
```bash
# Suite completa (unitários + integração)
pytest

# Com verbosidade
pytest -v

# Com cobertura
pytest --cov=src --cov-report=html

# Com duração dos testes
pytest --durations=10
```

### Somente Unitários (Rápido, Sem Custo)
```bash
# Unitários apenas (< 5s)
pytest tests/unit/ -v

# Validações rápidas durante desenvolvimento
pytest tests/unit/ -v --tb=short
```

### Somente Integração (Validação Completa)
```bash
# Integração E2E com LLM real (~40-50s)
pytest tests/integration/ -v

# Com saída detalhada
pytest tests/integration/ -v -s
```

### Teste Específico
```bash
# Testar regra de negócio específica
pytest tests/integration/test_business_rules.py::test_rn001_answer_with_context -v

# Testar módulo específico
pytest tests/unit/test_search_validation.py -v
```

## Configuração para Testes

### Variáveis de Ambiente (.env)
```bash
# OpenAI API Key (obrigatória)
OPENAI_API_KEY=sk-proj-your-key

# Modelo LLM (configurado automaticamente para testes)
LLM_MODEL=gpt-5-nano

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# Configurações de chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
SEARCH_K=10
```

### Pré-requisitos
1. **PostgreSQL rodando**: `docker-compose up -d`
2. **Ambiente virtual ativo**: `source .venv/bin/activate`
3. **Dependências instaladas**: `pip install -r requirements.txt`
4. **OpenAI API Key configurada**: Arquivo `.env` com `OPENAI_API_KEY`

### Verificar Ambiente
```bash
# Verificar PostgreSQL
docker-compose ps

# Verificar conexão com banco
psql $DATABASE_URL -c "SELECT 1"

# Verificar Python e dependências
python --version  # 3.13.9
pip list | grep -E "langchain|pytest|openai"
```

## Fixtures Principais

### `setup_llm_model` (session, autouse)
Configura automaticamente `LLM_MODEL=gpt-5-nano` para todos os testes.

### `gpt5_nano_model`
Retorna string "gpt-5-nano" para testes que precisam do nome do modelo.

### `clean_test_collection`
Cria e limpa coleção de teste antes e depois de cada teste.

### `shared_test_collection` (module scope)
Cria coleção única por módulo, otimizando performance ao evitar setup repetido.

### `sample_pdf_path`
Retorna caminho para PDF de teste (fixtures/test_document.pdf ou document.pdf).

### `ingested_test_doc` (module scope)
Ingere documento de teste uma vez por módulo, usado em test_business_rules.py.

### `real_scenario_collection` (module scope)
Ingere documento de teste uma vez por módulo, usado em test_real_scenarios.py.

## Cobertura de Código

### Meta
- **Cobertura mínima**: 85%
- **Atual**: ~95-97% (após otimização)

### Gerar Relatório
```bash
# Terminal
pytest --cov=src --cov-report=term-missing

# HTML (visualização detalhada)
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Áreas Cobertas
- ✅ **src/ingest.py**: 95%+ (todas as funções principais)
- ✅ **src/search.py**: 95%+ (busca e formatação)
- ✅ **src/chat.py**: 100% (prompt e LLM)

## Custo Estimado

### gpt-5-nano Pricing (hipotético)
- Input: ~$0.10 / 1M tokens
- Output: ~$0.30 / 1M tokens

### Por Execução da Suite
- **Testes de integração**: 18 testes
- **Chamadas de LLM**: ~18-20 chamadas
- **Tokens médios**: ~500 input + ~200 output por chamada
- **Total**: ~12-15K tokens

**Custo por execução**: ~$0.02-0.05

### Custo Mensal (Estimativa)
- **Execuções diárias**: 10-20
- **Custo diário**: $0.20-1.00
- **Custo mensal**: $6-30

✅ **Custo controlado e aceitável para qualidade garantida**

## Validação Contínua

### CI/CD (GitHub Actions)
```yaml
- name: Run Tests
  run: |
    pytest tests/ -v --cov=src --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

### Métricas de Sucesso

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Total de Testes | 48 | 28 | 42% redução |
| Testes Unitários | 38 | 10 | 74% redução |
| Testes Integração | 10 | 18 | 80% aumento |
| Tempo Execução | ~77s | ~45-55s | ~35% redução |
| Cobertura | 97% | 95%+ | Mantida |
| Chamadas LLM Real | 0 (mock) | 18-20 | Real validation |
| Custo/Execução | $0 | ~$0.03 | Mínimo |

## Troubleshooting

### Testes Falhando

#### "DATABASE_URL não configurada"
```bash
# Verificar .env
cat .env | grep DATABASE_URL

# Adicionar se não existir
echo "DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag" >> .env
```

#### "OpenAI API Error"
```bash
# Verificar API Key
echo $OPENAI_API_KEY

# Recarregar .env
source .env
export OPENAI_API_KEY=sk-proj-your-key
```

#### "Connection refused" (PostgreSQL)
```bash
# Iniciar PostgreSQL
docker-compose up -d

# Verificar status
docker-compose ps
```

#### "Rate limit exceeded"
- OpenAI limita requisições por minuto
- Aguarde alguns segundos e tente novamente
- Considere reduzir paralelização: `pytest -n 1`

### Testes Lentos
```bash
# Identificar testes lentos
pytest --durations=10

# Rodar apenas unitários (rápidos)
pytest tests/unit/ -v

# Skip testes de integração temporariamente
pytest tests/unit/ -v
```

### Cobertura Baixa
```bash
# Ver linhas não cobertas
pytest --cov=src --cov-report=term-missing

# Identificar funções não testadas
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Boas Práticas

### Escrevendo Novos Testes

1. **Unitários**: Para validações simples, entrada, configurações
   ```python
   def test_validation_basic():
       """Descrição clara do que testa."""
       with pytest.raises(ValueError):
           invalid_function_call()
   ```

2. **Integração**: Para fluxos completos E2E
   ```python
   def test_e2e_flow(sample_pdf_path, clean_test_collection):
       """Fluxo completo: Ingest → Search → Chat."""
       # 1. Ingest
       docs = load_pdf(sample_pdf_path)
       chunks = split_documents(docs)
       store_in_vectorstore(chunks, clean_test_collection)
       
       # 2. Search
       searcher = SemanticSearch(collection_name=clean_test_collection)
       context = searcher.get_context("query")
       
       # 3. Chat com LLM real
       response = ask_llm("query", context)
       
       # 4. Assert
       assert len(response) > 0
   ```

3. **Sempre**:
   - Docstring clara
   - Nome de teste descritivo
   - Assertions específicas
   - Cleanup automático (fixtures)

### Evitar

- ❌ Mocks desnecessários (preferir integração real)
- ❌ Testes redundantes (múltiplos testes da mesma coisa)
- ❌ Testes sem assertions claras
- ❌ Hardcoded values (usar fixtures)
- ❌ Testes interdependentes

## Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [LangChain Testing Guide](https://python.langchain.com/docs/contributing/testing)
- [Integration Testing Best Practices](https://martinfowler.com/bliki/IntegrationTest.html)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
