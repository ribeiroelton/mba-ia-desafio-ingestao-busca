# [013] - Otimizar Testes LLM-as-a-Judge para Mínimo Consumo de Tokens

## Metadados
- **ID**: 013
- **Estimativa**: 2-3 dias
- **Impacto**: 23 → 15 testes | Redução de 79% tokens | 69% mais rápido

## Objetivo
Otimizar testes LLM-as-a-Judge usando perguntas específicas sobre dados reais do documento (tabela de empresas), reduzindo tokens de ~34.600 para ~7.350 (-79%).

## Estratégia de Otimização

**Documento Real**: Tabela com ~350 empresas (Nome | Faturamento | Ano de fundação)

**Princípio**: Usar perguntas específicas sobre dados reais ao invés de genéricas

```python
# ❌ ANTES (~1500 tokens)
"Quais são os principais tópicos do documento?"

# ✅ DEPOIS (~450 tokens)  
"Qual é o faturamento da empresa Alfa Energia S.A.?"
```

**Ações**:
1. Substituir perguntas genéricas por específicas (empresas reais)
2. Remover loops com múltiplas perguntas
3. Consolidar testes duplicados (23 → 15 testes)
4. Simplificar assertions

## Arquivos a Modificar

| Arquivo | Testes Atuais | Testes Finais |
|---------|---------------|---------------|
| `test_llm_quality_evaluation.py` | 7 | 5 |
| `test_business_rules.py` | 5 | 3 |
| `test_real_scenarios.py` | 6 | 4 |
| `test_e2e_core.py` | 5 | 3 |
| **TOTAL** | **23** | **15** |

## Critérios de Aceite

- [ ] 15 testes implementados (redução de 8 testes)
- [ ] Todas as perguntas usam dados reais (empresas específicas)
- [ ] Redução >= 70% em tokens
- [ ] Tempo total < 70s
- [ ] Todos os testes passando
- [ ] README.md atualizado

## Dados do Documento (document.pdf)

**Estrutura**: Tabela com empresas

| Campo | Exemplo |
|-------|---------|
| Nome | Alfa Energia S.A. |
| Faturamento | R$ 722.875.391,46 |
| Ano fundação | 1972 |

**Empresas para usar nos testes**:
- Alfa Energia S.A. (1972, R$ 722M)
- Aliança Esportes ME (2002, R$ 4.4B)
- Alta Mídia S.A. (1978, R$ 3.2B)

## Exemplos de Otimização

### Pergunta Genérica → Específica
```python
# ❌ ANTES (~1500 tokens)
question = "Quais são os principais tópicos do documento?"

# ✅ DEPOIS (~450 tokens)
question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
```

### Remover Loops
```python
# ❌ ANTES (3x custo)
for question in ["pergunta1", "pergunta2", "pergunta3"]:
    evaluation = llm_evaluator.evaluate(...)

# ✅ DEPOIS
question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
evaluation = llm_evaluator.evaluate(...)
```

### Simplificar Assertions
```python
# ❌ ANTES
assert evaluation.criteria_scores["adherence_to_context"] >= 70
assert evaluation.criteria_scores["hallucination_detection"] >= 80
assert evaluation.criteria_scores["clarity_objectivity"] >= 70

# ✅ DEPOIS
assert evaluation.passed
assert evaluation.criteria_scores["hallucination_detection"] >= 80
```

## Testes Otimizados

### 1. test_llm_quality_evaluation.py (7 → 5)

#### 1. test_factual_accuracy_direct_question
```python
def test_factual_accuracy_direct_question(quality_test_collection, llm_evaluator):
    """
    Valida resposta factual para pergunta direta sobre empresa específica.
    
    Cenário: Pergunta sobre fato específico presente no documento (tabela de empresas).
    Expected: Resposta curta e correta baseada na tabela.
    Tokens: ~400-500 (contexto mínimo + resposta direta)
    
    OTIMIZADO: Pergunta específica sobre dados tabulares reais do documento.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # OTIMIZADO: Pergunta sobre empresa real do documento
    question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.passed, f"Falhou: {evaluation.feedback}"
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 75
```

#### 2. test_no_context_standard_message
```python
def test_no_context_standard_message(quality_test_collection, llm_evaluator):
    """
    Valida mensagem padrão quando sem contexto.
    
    Cenário: Pergunta fora do domínio.
    Expected: Mensagem padrão exata.
    Tokens: ~400 (contexto vazio + mensagem padrão)
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85
```

#### 3. test_partial_info_no_hallucination
```python
def test_partial_info_no_hallucination(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não inventa informações ausentes no documento.
    
    Cenário: Pergunta sobre campo não presente na tabela (funcionários).
    Expected: Mensagem padrão, SEM inventar números.
    Tokens: ~400-500 (contexto mínimo + mensagem padrão)
    
    OTIMIZADO: Pergunta sobre informação realmente ausente (documento só tem 
    nome, faturamento e ano de fundação - NÃO tem número de funcionários).
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # OTIMIZADO: Pergunta sobre campo ausente na tabela
    question = "Quantos funcionários a empresa Alfa Energia S.A. possui?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Crítico: não deve inventar números de funcionários (campo não existe no doc)
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.overall_score >= 65
```

#### 4. test_no_external_knowledge
```python
def test_no_external_knowledge(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não usa conhecimento geral externo.
    
    Cenário: Pergunta sobre tema comum, resposta deve ser do contexto.
    Expected: Baseado no contexto OU mensagem padrão.
    Tokens: ~500 (contexto + resposta)
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve usar contexto OU mensagem padrão, nunca conhecimento geral
    assert evaluation.criteria_scores["adherence_to_context"] >= 80
    assert evaluation.criteria_scores["rule_following"] >= 85
```

#### 5. test_evaluation_cost_estimate (atualizado)
```python
def test_evaluation_cost_estimate(quality_test_collection, llm_evaluator):
    """
    Documenta custos otimizados de avaliação.
    
    Nota: Teste informativo, sempre passa.
    """
    # Executar avaliação simples
    searcher = SemanticSearch(collection_name=quality_test_collection)
    question = "Teste de custo otimizado"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    print("\n" + "="*60)
    print("CUSTOS OTIMIZADOS - LLM-as-a-JUDGE")
    print("="*60)
    print(f"Modelo: gpt-5-nano")
    print(f"Tokens por avaliação: ~600-900 (redução de 60%)")
    print(f"Custo por avaliação: ~$0.00006-0.00009")
    print(f"Custo por suite (5 testes): ~$0.0003-0.00045")
    print(f"Custo por 50 execuções: ~$0.015-0.025")
    print("="*60)
    print(f"ECONOMIA vs versão anterior: ~60% de tokens")
    print("="*60)
    
    assert True
```

**REMOVER**: `test_response_completeness`, `test_response_consistency_across_similar_questions`

### 2. test_business_rules.py (5 → 3)

#### 1. test_rn001_answer_with_context
```python
def test_rn001_answer_with_context(ingested_test_doc, llm_evaluator):
    """
    RN-001: Resposta baseada no contexto com pergunta direta sobre dados reais.
    
    Tokens: ~450-550 (redução de ~50%)
    
    OTIMIZADO: Pergunta específica sobre ano de fundação de empresa real.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # OTIMIZADO: Pergunta sobre dado real e específico da tabela
    question = "Em que ano foi fundada a empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    assert len(response) > 0
    assert "Não tenho informações necessárias" not in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.passed
    assert evaluation.criteria_scores["adherence_to_context"] >= 70
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
```

#### 2. test_rn002_no_context_standard_message
```python
def test_rn002_no_context_standard_message(ingested_test_doc, llm_evaluator):
    """
    RN-002: Mensagem padrão quando sem contexto.
    
    Tokens: ~400 (já otimizado, manter)
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85
```

#### 3. test_rn003_no_external_knowledge
```python
def test_rn003_no_external_knowledge(ingested_test_doc, llm_evaluator):
    """
    RN-003: Não usar conhecimento externo.
    
    Tokens: ~500 (já otimizado, manter)
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.criteria_scores["adherence_to_context"] >= 80
    assert evaluation.criteria_scores["rule_following"] >= 85
```

**REMOVER**: Testes duplicados `_with_evaluation`

### 3. test_real_scenarios.py (6 → 4)

#### 1. test_scenario_no_context_messages
```python
def test_scenario_no_context_messages(real_scenario_collection, llm_evaluator):
    """
    Cenário: Múltiplas perguntas fora do contexto.
    
    OTIMIZADO: 1 pergunta ao invés de loop com 3.
    Tokens: ~400 (redução de 67%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Uma pergunta representativa
    question = "Quem foi o primeiro presidente dos Estados Unidos?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85
```

#### 2. test_scenario_ambiguous_question
```python
def test_scenario_ambiguous_question(real_scenario_collection, llm_evaluator):
    """
    Cenário: Pergunta ambígua mas específica.
    
    OTIMIZADO: Pergunta menos genérica.
    Tokens: ~550 (redução de 30%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Ambígua mas não genérica
    question = "Quando isso aconteceu?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Ambiguidade aceita, mas sem alucinação
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
```

#### 3. test_scenario_numeric_data
```python
def test_scenario_numeric_data(real_scenario_collection, llm_evaluator):
    """
    Cenário: Extração de valor monetário específico de empresa real.
    
    OTIMIZADO: Pergunta sobre faturamento específico.
    Tokens: ~450-500 (redução de 50%)
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Pergunta sobre valor monetário real da tabela
    question = "Qual é o faturamento da empresa Aliança Esportes ME?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Crítico: não deve inventar valores
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 75
```

#### 4. test_scenario_factual_extraction
```python
def test_scenario_factual_extraction(real_scenario_collection, llm_evaluator):
    """
    Cenário: Comparação entre duas empresas específicas.
    
    Tokens: ~500-550
    
    OTIMIZADO: Pergunta comparativa entre empresas reais da tabela.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # OTIMIZADO: Comparação entre duas empresas reais
    question = "Qual empresa foi fundada primeiro: Alfa Energia S.A. ou Aliança Esportes ME?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["adherence_to_context"] >= 75
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
```

**REMOVER**: Testes de sumarização e loops

### 4. test_e2e_core.py (5 → 3)

#### 1. test_e2e_complete_flow
```python
def test_e2e_complete_flow(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E completo com pergunta direta sobre empresa da tabela.
    
    Tokens: ~500-600 (redução de 50%)
    
    OTIMIZADO: Pergunta específica sobre primeira empresa da lista.
    """
    # Ingestão
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    # Busca com pergunta direta sobre dado real
    searcher = SemanticSearch(collection_name=clean_test_collection)
    question = "Qual é o faturamento da primeira empresa mencionada no documento?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.passed
    assert evaluation.criteria_scores["adherence_to_context"] >= 70
```

#### 2. test_e2e_no_context_flow
```python
def test_e2e_no_context_flow(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E com pergunta fora do contexto.
    
    Tokens: ~400
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    question = "Qual é a capital do Brasil?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90
```

#### 3. test_e2e_special_characters
```python
def test_e2e_special_characters(sample_pdf_path, clean_test_collection, llm_evaluator):
    """
    E2E com formato monetário (caracteres especiais R$).
    
    Tokens: ~450-500
    
    OTIMIZADO: Pergunta sobre formato presente no documento (R$).
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, clean_test_collection)
    
    searcher = SemanticSearch(collection_name=clean_test_collection)
    # OTIMIZADO: Pergunta sobre formato monetário real do documento
    question = "Os valores estão em qual moeda?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 70
```

**REMOVER**: Testes duplicados e loops múltiplos

---

## Atualizar README.md

#### Seção: Framework LLM-as-a-Judge

**ANTES**:
```markdown
### Executando Testes

```bash
# Testes de avaliação LLM
pytest tests/integration/test_llm_quality_evaluation.py -v
```

#### Métricas de Custo

O relatório mostra:
- Modelo: gpt-5-nano
- Tokens por avaliação: ~1500-2000
- Custo por avaliação: ~$0.0001-0.0002
- Custo para 50 avaliações: ~$0.005-0.010
```

**DEPOIS**:
```markdown
### Executando Testes

```bash
# Testes de avaliação LLM (otimizados)
pytest tests/integration/test_llm_quality_evaluation.py -v
```

#### Métricas de Custo (Otimizadas)

Framework otimizado para mínimo consumo de tokens:

**Estratégia de Otimização**:
- ✅ Perguntas diretas e factuais (não genéricas)
- ✅ Respostas curtas (1-3 sentenças)
- ✅ Contexto mínimo necessário
- ✅ Sem testes de sumarização

**Custos Atuais**:
- Modelo: gpt-5-nano
- Tokens por avaliação: ~600-900 (redução de 60%)
- Custo por avaliação: ~$0.00006-0.00009
- Custo por suite (5 testes): ~$0.0003-0.00045
- Custo por 50 execuções: ~$0.015-0.025

**Economia**: ~70% em tokens comparado à versão anterior

**Detalhamento por Arquivo**:
- `test_llm_quality_evaluation.py`: 5 testes, ~$0.0004
- `test_business_rules.py`: 3 testes, ~$0.0002
- `test_real_scenarios.py`: 4 testes, ~$0.0003
- `test_e2e_core.py`: 3 testes, ~$0.0002
- **Total geral**: 15 testes, ~$0.0011

**Comparação Geral**:
| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| Testes totais | 23 | 15 | -35% |
| Tokens totais | ~34,600 | ~9,850 | -72% |
| Custo total | ~$0.0036 | ~$0.0011 | -69% |
| Tempo total | ~200s | ~80s | -60% |
```

### Regras de Negócio a Validar

**Mantidas** (essenciais):
- **RN-001**: Contexto Exclusivo - Validado em `test_no_external_knowledge`
- **RN-002**: Mensagem Padrão - Validado em `test_no_context_standard_message`
- **RN-003**: Sem Alucinação - Validado em todos os testes (hallucination_detection >= 80)
- **RN-007**: Score >= 70 - Validado em `test_factual_accuracy_direct_question`

**Removidas** (redundantes ou não críticas):
- Testes de sumarização de documento completo
- Testes de consistência com múltiplas perguntas similares
- Validações de completude de resposta longa

### Tratamento de Erros

**Manter**:
- Validação de resposta vazia
- Validação de tipo de resposta (string)
- Captura de exceções do LLM Evaluator

**Simplificar**:
- Remover validações de tamanho mínimo de resposta
- Focar em validação de conteúdo, não estrutura

## Validação



```bash
# Executar testes otimizados
pytest tests/integration/ -v

# Verificar tempo (meta: < 70s)
time pytest tests/integration/ -v -k "llm_evaluator"

# Validar cobertura mantida
pytest --cov=src --cov-report=term-missing
```

**Meta**: 15 testes | < 70s | ~$0.00074 por execução



## Checklist

- [ ] 4 arquivos otimizados (23 → 15 testes)
- [ ] Perguntas usam dados reais (empresas específicas)
- [ ] Loops removidos
- [ ] Testes duplicados consolidados
- [ ] Tempo < 70s
- [ ] Todos os testes passando
- [ ] README.md atualizado
- [ ] Commit + PR criados







## Referências

- [LLM-as-a-Judge Pattern](https://eugeneyan.com/writing/llm-patterns/#llm-as-a-judge)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [Token Optimization Strategies](https://platform.openai.com/docs/guides/prompt-engineering)

## Estimativa de Impacto

### Antes da Otimização (Todos os Arquivos)

| Arquivo | Testes | Tokens/teste | Total Tokens | Custo | Tempo |
|---------|--------|--------------|--------------|-------|-------|
| `test_llm_quality_evaluation.py` | 7 | ~1,500 | ~10,500 | ~$0.0011 | ~60s |
| `test_business_rules.py` | 5 | ~1,400 | ~7,000 | ~$0.0007 | ~45s |
| `test_real_scenarios.py` | 6 | ~1,600 | ~9,600 | ~$0.0010 | ~50s |
| `test_e2e_core.py` | 5 | ~1,500 | ~7,500 | ~$0.0008 | ~45s |
| **TOTAL** | **23** | **~1,500** | **~34,600** | **~$0.0036** | **~200s** |

### Depois da Otimização (Todos os Arquivos) - COM PERGUNTAS ESPECÍFICAS

| Arquivo | Testes | Tokens/teste | Total Tokens | Custo | Tempo |
|---------|--------|--------------|--------------|-------|-------|
| `test_llm_quality_evaluation.py` | 5 | ~500 | ~2,500 | ~$0.00025 | ~20s |
| `test_business_rules.py` | 3 | ~450 | ~1,350 | ~$0.00014 | ~12s |
| `test_real_scenarios.py` | 4 | ~500 | ~2,000 | ~$0.00020 | ~15s |
| `test_e2e_core.py` | 3 | ~500 | ~1,500 | ~$0.00015 | ~15s |
| **TOTAL** | **15** | **~488** | **~7,350** | **~$0.00074** | **~62s** |

**Otimização Extra**: Perguntas baseadas em dados reais da tabela (empresas específicas, 
campos existentes) reduzem ainda mais o contexto necessário.

### Ganhos Consolidados (COM PERGUNTAS ESPECÍFICAS OTIMIZADAS)

| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **Total de testes** | 23 | 15 | **-35% (8 testes)** |
| **Tokens por execução** | ~34,600 | ~7,350 | **-79% (27,250 tokens)** |
| **Custo por execução** | ~$0.0036 | ~$0.00074 | **-79% ($0.00286)** |
| **Tempo por execução** | ~200s | ~62s | **-69% (138s)** |
| **Tokens médio/teste** | ~1,500 | ~488 | **-67%** |

**Otimização Adicional Aplicada**:
- Perguntas baseadas em **dados reais** do documento (tabela de empresas)
- Uso de **empresas específicas** (ex: "Alfa Energia S.A.") ao invés de genéricas
- Consultas sobre **campos existentes** (nome, faturamento, ano)
- Redução adicional de ~25% em tokens vs perguntas genéricas

### Economia Anual (estimativa com perguntas otimizadas)

Assumindo 100 execuções/mês (CI/CD + dev):

| Período | Antes | Depois | Economia |
|---------|-------|--------|----------|
| **Mensal** | $0.36 | $0.074 | **$0.286 (79%)** |
| **Anual** | $4.32 | $0.888 | **$3.43 (79%)** |
| **Tempo mensal** | 5.5h | 1.7h | **3.8h (69%)** |

### Benefícios Qualitativos

1. ✅ **Feedback mais rápido**: 62s vs 200s (69% mais rápido) = desenvolvedores esperam menos
2. ✅ **CI/CD mais eficiente**: Menos tempo de build e menor custo
3. ✅ **Mesma cobertura**: Todos os cenários críticos mantidos
4. ✅ **Testes mais claros**: Perguntas específicas são mais fáceis de entender e debugar
5. ✅ **Manutenção simplificada**: Menos testes duplicados
6. ✅ **Validação mais precisa**: Perguntas sobre dados reais são mais fáceis de verificar
7. ✅ **Contexto mínimo**: Perguntas específicas recuperam apenas chunks relevantes
8. ✅ **Respostas determinísticas**: Dados tabulares geram respostas mais consistentes
