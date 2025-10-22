# [014] - Refatoração e Otimização do Framework LLM-as-a-Judge

## Metadados
- **ID**: 014
- **Grupo**: Fase 4 - Manutenção e Melhorias
- **Prioridade**: Alta
- **Complexidade**: Média
- **Estimativa**: 2-3 dias

## Descrição

Refatorar e otimizar o framework LLM-as-a-Judge (`tests/utils/llm_evaluator.py` e `tests/utils/evaluation_criteria.py`) para remover código não utilizado, melhorar eficiência e simplificar a base de testes. O objetivo é manter a mesma qualidade de avaliação enquanto reduz complexidade desnecessária e fortalece os testes de integração reais, minimizando uso de mocks.

O framework atual está funcional e bem estruturado, mas após revisão do código identificou-se oportunidades de:
- Remover métodos/atributos não utilizados
- Simplificar parsing de JSON (tratamento de edge cases desnecessários)
- Consolidar testes unitários focando no essencial
- Fortalecer testes de integração com cenários reais
- Melhorar documentação inline

## Requisitos

### Requisitos Funcionais
- RF-014.1: Manter todos os critérios de avaliação existentes (adherence_to_context, hallucination_detection, rule_following, clarity_objectivity)
- RF-014.2: Preservar interface pública do `LLMEvaluator.evaluate()` para não quebrar testes existentes
- RF-014.3: Manter cálculo de score ponderado conforme pesos definidos
- RF-014.4: Garantir compatibilidade com todos os testes de integração existentes

### Requisitos Não-Funcionais
- RNF-014.1: Cobertura de testes >= 80% (manter ou melhorar)
- RNF-014.2: Redução de código em pelo menos 10-15%
- RNF-014.3: Todos os testes existentes devem continuar passando
- RNF-014.4: Documentação clara das mudanças realizadas

## Fonte da Informação

**Arquivos Analisados**:
- `tests/utils/llm_evaluator.py` (298 linhas) - Framework principal de avaliação
- `tests/utils/evaluation_criteria.py` (126 linhas) - Definição de critérios
- `tests/unit/test_llm_evaluator_unit.py` (~300 linhas) - Testes unitários
- `tests/integration/test_llm_quality_evaluation.py` - Testes de integração
- `tests/conftest.py` - Fixture `llm_evaluator`
- Testes de integração que utilizam: `test_business_rules.py`, `test_e2e_core.py`, `test_real_scenarios.py`

**Contexto do Projeto**:
- README.md - Seção "Framework LLM-as-a-Judge"
- Sistema RAG com avaliação automática de qualidade de respostas
- Pattern LLM-as-a-Judge implementado para validar respostas do chatbot

## Stack Necessária

- **Linguagem**: Python 3.13.9
- **Framework de Testes**: pytest
- **Bibliotecas**:
  - `langchain-openai`: ChatOpenAI para LLM avaliador
  - `langchain-core`: Mensagens do sistema
  - `dataclasses`: EvaluationResult
- **LLM**: OpenAI gpt-5-nano (modelo de avaliação)
- **Ferramentas**: pytest-cov para cobertura

## Dependências

### Dependências Técnicas
- OpenAI API configurada (variável OPENAI_API_KEY)
- Ambiente de testes funcional com PostgreSQL + pgVector
- Fixture `llm_evaluator` no conftest.py
- Documentos de teste ingeridos para testes de integração

### Dependências de Negócio
- Nenhuma decisão de negócio pendente
- Framework já validado e em uso

## Critérios de Aceite

1. [ ] Código refatorado com redução de 10-15% de linhas mantendo funcionalidade
2. [ ] Todos os 11 testes existentes de integração que usam `llm_evaluator` continuam passando
3. [ ] Testes unitários revisados, removendo testes redundantes ou de baixo valor
4. [ ] Testes de integração fortalecidos com menos mocks e mais cenários reais
5. [ ] Cobertura de testes >= 80% mantida ou melhorada
6. [ ] Documentação inline atualizada (docstrings)
7. [ ] Nenhuma quebra de compatibilidade com interface pública
8. [ ] Build e linting sem erros ou warnings
9. [ ] Code review realizado

## Implementação Resumida

### Estrutura de Arquivos

```
tests/
├── utils/
│   ├── __init__.py
│   ├── llm_evaluator.py          # Refatorar e otimizar
│   └── evaluation_criteria.py    # Revisar e simplificar
├── unit/
│   └── test_llm_evaluator_unit.py # Consolidar testes
└── integration/
    ├── test_llm_quality_evaluation.py # Fortalecer
    ├── test_business_rules.py         # Validar compatibilidade
    ├── test_e2e_core.py              # Validar compatibilidade
    └── test_real_scenarios.py        # Validar compatibilidade
```

### Componentes a Implementar

#### 1. `tests/utils/llm_evaluator.py` (Refatoração)

**Responsabilidade**: Framework de avaliação LLM-as-a-Judge

**Otimizações Identificadas**:

1. **Simplificar `_parse_evaluation_response()`**:
   - Código atual tem lógica complexa para tratar JSON com markdown e regex para escapar aspas
   - Simplificar: GPT-5-nano é consistente e retorna JSON limpo
   - Manter apenas tratamento básico de markdown code blocks
   - Remover regex complexo de escape de feedback

```python
def _parse_evaluation_response(self, response_text: str) -> Dict:
    """
    Parseia resposta JSON do avaliador.
    
    Args:
        response_text: Texto da resposta do LLM
        
    Returns:
        Dict com dados de avaliação
        
    Raises:
        json.JSONDecodeError: Se JSON inválido
    """
    text = response_text.strip()
    
    # Remover markdown code blocks se presentes
    if text.startswith("```json") or text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    text = text.strip()
    
    return json.loads(text, strict=False)
```

2. **Remover atributo `details` não utilizado em `EvaluationResult`**:
   - Atributo `details: Dict[str, str]` não é utilizado em nenhum teste
   - Sempre inicializado como `{}` vazio
   - Remover para simplificar

```python
@dataclass
class EvaluationResult:
    """Resultado de uma avaliação LLM."""
    score: int  # 0-100
    criteria_scores: Dict[str, int]  # Scores por critério
    feedback: str  # Feedback detalhado
    passed: bool  # Se passou no threshold
    
    @property
    def overall_score(self) -> int:
        """Alias para score (compatibilidade)."""
        return self.score
```

3. **Simplificar docstrings excessivamente longas**:
   - Manter informação essencial
   - Remover exemplos redundantes

#### 2. `tests/utils/evaluation_criteria.py` (Revisão)

**Responsabilidade**: Definição de critérios de avaliação

**Otimizações Identificadas**:

1. **Remover atributos `examples_good` e `examples_bad` não utilizados**:
   - Nunca referenciados no código de avaliação
   - Não utilizados em testes
   - Ocupam espaço desnecessário

```python
@dataclass
class EvaluationCriterion:
    """Critério de avaliação para respostas LLM."""
    name: str
    weight: float  # 0.0-1.0
    description: str
```

2. **Simplificar classe mantendo o essencial**:
   - Manter critérios (constantes)
   - Manter `get_all_criteria()`
   - Manter `calculate_weighted_score()`

#### 3. `tests/unit/test_llm_evaluator_unit.py` (Consolidação)

**Responsabilidade**: Testes unitários do framework

**Otimizações Identificadas**:

1. **Consolidar classes de teste relacionadas**:
   - Atual: 7 classes separadas (TestLLMEvaluatorInitialization, TestPromptBuilding, etc)
   - Proposta: 3-4 classes focadas no essencial

2. **Remover testes redundantes**:
   - `test_criteria_have_examples` - Não faz sentido após remover examples
   - `test_parse_json_with_markdown` - Simplificar para um teste básico
   - Consolidar testes de `_build_evaluation_result` (3 testes → 2 testes)

3. **Manter testes essenciais**:
   - Inicialização (1 teste consolidado)
   - Build de prompt (2 testes: com e sem system_prompt)
   - Parse JSON (2 testes: válido e inválido)
   - Build de resultado (2 testes: completo e com cálculos)
   - Cálculo de score ponderado (2 testes: normal e edge cases)
   - Critérios (2 testes: estrutura e pesos)

**Estrutura Proposta**:
```python
class TestLLMEvaluator:
    """Testes core do avaliador."""
    
    def test_initialization_defaults(self): ...
    def test_initialization_custom(self): ...
    def test_build_prompt_basic(self): ...
    def test_build_prompt_with_system_prompt(self): ...

class TestEvaluationParsing:
    """Testes de parsing e construção de resultados."""
    
    def test_parse_valid_json(self): ...
    def test_parse_json_with_markdown_blocks(self): ...
    def test_parse_invalid_json_raises(self): ...
    def test_build_result_complete(self): ...
    def test_build_result_calculates_missing_fields(self): ...

class TestWeightedScore:
    """Testes de cálculo de score ponderado."""
    
    def test_calculate_weighted_score_normal(self): ...
    def test_calculate_weighted_score_edge_cases(self): ...

class TestEvaluationCriteria:
    """Testes dos critérios de avaliação."""
    
    def test_all_criteria_structure(self): ...
    def test_weights_sum_to_one(self): ...
```

#### 4. `tests/integration/test_llm_quality_evaluation.py` (Fortalecimento)

**Responsabilidade**: Testes de integração reais do framework

**Melhorias Propostas**:

1. **Remover teste de custo** (`test_evaluation_cost_estimate`):
   - Não é teste funcional
   - Apenas documenta custos
   - Pode ir para documentação

2. **Fortalecer assertions**:
   - Adicionar validação de `evaluation.score` além de `passed`
   - Validar ranges de scores por critério
   - Adicionar mensagens de falha mais descritivas

3. **Adicionar teste de resiliência**:
   - Testar resposta do avaliador quando LLM retorna formato inesperado
   - Validar timeout/retry (se aplicável)

### Regras de Negócio a Implementar

- **RN-014.1**: Manter fidelidade do pattern LLM-as-a-Judge
  - Avaliador deve continuar usando segundo LLM para validar respostas
  - Critérios de avaliação não devem mudar
  
- **RN-014.2**: Compatibilidade retroativa obrigatória
  - Interface `evaluate(question, context, response, system_prompt)` deve ser mantida
  - `EvaluationResult` deve ter mesmos atributos públicos (pode remover internos não usados)

### Validações Necessárias

1. **Validação de Interface**:
   - Garantir que `llm_evaluator.evaluate()` retorna `EvaluationResult` com mesma estrutura
   - Validar que `result.score`, `result.passed`, `result.feedback`, `result.criteria_scores` funcionam

2. **Validação de Testes Existentes**:
   - Executar todos os testes de integração antes e depois
   - Comparar resultados para garantir comportamento idêntico

3. **Validação de Cobertura**:
   - Rodar `pytest --cov=tests/utils --cov-report=term-missing`
   - Garantir cobertura >= 80%

### Tratamento de Erros

- **Parsing de JSON**: Manter `json.JSONDecodeError` explícito com mensagem clara
- **Comunicação com LLM**: Manter tratamento de exceções genéricas
- **Validação de Scores**: Garantir conversão para int e validação de range (0-100)

## Testes de Qualidade e Cobertura (Obrigatório)

### Testes Unitários

**Arquivo**: `tests/unit/test_llm_evaluator_unit.py`  
**Cobertura Mínima**: 85%

**Cenários Essenciais a Testar**:

1. **Inicialização**:
   - Input: `LLMEvaluator()` e `LLMEvaluator(threshold=80, model="gpt-4")`
   - Expected: Atributos corretos, LLM instanciado

2. **Build Prompt**:
   - Input: question, context, response (com e sem system_prompt)
   - Expected: String formatada corretamente com todas as seções

3. **Parse JSON**:
   - Input: JSON válido, JSON com markdown, JSON inválido
   - Expected: Dict correto ou exceção

4. **Build Result**:
   - Input: Dict com todos os campos, Dict com campos faltando
   - Expected: EvaluationResult correto com cálculos adequados

5. **Cálculo de Score**:
   - Input: Scores variados por critério
   - Expected: Score ponderado correto (30% + 30% + 25% + 15% = 100%)

6. **Critérios**:
   - Input: Chamada de `get_all_criteria()`
   - Expected: 4 critérios, pesos somam 1.0

**Estrutura de Teste**:
```python
class TestLLMEvaluator:
    def test_initialization_defaults(self):
        evaluator = LLMEvaluator()
        assert evaluator.threshold == 70
        assert evaluator.model == "gpt-5-nano"
        assert evaluator.llm is not None
    
    def test_build_prompt_basic(self):
        evaluator = LLMEvaluator()
        prompt = evaluator.build_evaluation_prompt(
            question="Test?",
            context="Context",
            response="Response"
        )
        assert "CONTEXTO FORNECIDO" in prompt
        assert "Test?" in prompt
        assert "Context" in prompt
```

### Testes de Integração

**Arquivo**: `tests/integration/test_llm_quality_evaluation.py`  
**Cobertura Mínima**: Validação funcional completa

**Cenários Reais a Testar**:

1. **Resposta Factual Precisa**:
   - Input: Pergunta direta sobre dado no PDF, contexto relevante, resposta correta
   - Expected: `passed=True`, `hallucination_detection >= 80`, `adherence_to_context >= 75`

2. **Mensagem Padrão Sem Contexto**:
   - Input: Pergunta fora do escopo, contexto vazio/irrelevante, mensagem padrão
   - Expected: `rule_following >= 90`, `overall_score >= 85`

3. **Detecção de Informação Parcial**:
   - Input: Pergunta sobre dado não presente, contexto parcial
   - Expected: `hallucination_detection >= 80`, sem invenção de dados

4. **Rejeição de Conhecimento Externo**:
   - Input: Pergunta de conhecimento geral, contexto irrelevante
   - Expected: `adherence_to_context >= 80`, `rule_following >= 85`

5. **Validação de Resiliência** (NOVO):
   - Input: Resposta do LLM com formatação inesperada ou edge case
   - Expected: Tratamento gracioso ou erro explícito

**Estrutura de Teste**:
```python
def test_factual_accuracy_direct_question(quality_test_collection, llm_evaluator):
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
    
    assert evaluation.passed, f"Falhou com score {evaluation.score}: {evaluation.feedback}"
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        "Detecção de alucinação abaixo do esperado"
    assert evaluation.criteria_scores["adherence_to_context"] >= 75, \
        "Aderência ao contexto abaixo do esperado"
    assert 70 <= evaluation.score <= 100, \
        f"Score fora do range esperado: {evaluation.score}"
```

### Testes de Compatibilidade

**Validação com Testes Existentes**:

Execute os seguintes testes para garantir compatibilidade:

```bash
# Testes de integração que usam llm_evaluator
pytest tests/integration/test_business_rules.py -v
pytest tests/integration/test_e2e_core.py -v  
pytest tests/integration/test_real_scenarios.py -v
pytest tests/integration/test_llm_quality_evaluation.py -v

# Todos devem passar sem alterações
```

**Validação Esperada**:
- 11+ testes de integração usando `llm_evaluator` fixture
- 100% de taxa de sucesso mantida
- Nenhuma mudança de comportamento observada

## Documentação Necessária (Obrigatório)

### Código

- [x] Atualizar docstrings de métodos públicos refatorados
- [x] Adicionar comentários em otimizações não óbvias
- [x] Documentar mudanças de interface (se houver)

### README

- [x] Atualizar seção "Framework LLM-as-a-Judge" se necessário
- [x] Documentar breaking changes (se houver - evitar)
- [x] Atualizar badges de cobertura se mudarem

### CHANGELOG (Criar se não existir)

Criar entrada de changelog:

```markdown
## [Unreleased]

### Changed
- Otimizou framework LLM-as-a-Judge removendo código não utilizado
- Simplificou parsing de JSON em `_parse_evaluation_response()`
- Consolidou testes unitários focando no essencial

### Removed
- Atributo `details` não utilizado de `EvaluationResult`
- Atributos `examples_good` e `examples_bad` de `EvaluationCriterion`
- Testes unitários redundantes

### Improved
- Fortaleceu testes de integração com menos mocks
- Melhorou documentação inline
- Redução de ~15% no código do framework mantendo funcionalidade
```

## Checklist de Finalização

- [ ] Código refatorado seguindo padrões do projeto
- [ ] Todos os critérios de aceite atendidos
- [ ] Redução de 10-15% de código confirmada
- [ ] Testes unitários consolidados e passando
- [ ] Testes de integração fortalecidos e passando
- [ ] Todos os 11+ testes existentes com `llm_evaluator` ainda passam
- [ ] Cobertura >= 80% mantida (verificar com pytest-cov)
- [ ] Code review realizado
- [ ] Documentação atualizada (docstrings, README se necessário)
- [ ] Build passa sem erros
- [ ] Linting passa sem warnings (`ruff check` ou equivalente)
- [ ] Nenhuma quebra de compatibilidade introduzida
- [ ] Commits descritivos e atômicos

## Notas Adicionais

### Armadilhas Conhecidas

1. **Não remover método `build_evaluation_prompt`**:
   - Mesmo que pareça simples, é útil para testes e pode ser usado externamente
   - Manter como método público

2. **Preservar exatamente a interface de `evaluate()`**:
   - Parâmetros: `question`, `context`, `response`, `system_prompt` (opcional)
   - Retorno: `EvaluationResult` com mesma estrutura pública

3. **Cuidado ao simplificar parsing**:
   - Testar com respostas reais do GPT-5-nano antes de remover lógica
   - Se modelo ocasionalmente retorna formato inesperado, manter tratamento

4. **Manter fixture `llm_evaluator` em conftest.py**:
   - Não alterar sem revisar todos os usos
   - 11+ testes dependem desta fixture

### Dicas de Implementação

1. **Abordagem Incremental**:
   - Refatorar `llm_evaluator.py` primeiro
   - Rodar testes unitários após cada mudança
   - Refatorar `evaluation_criteria.py` em seguida
   - Consolidar testes unitários
   - Fortalecer testes de integração por último

2. **Validação Contínua**:
   - Após cada commit, rodar: `pytest tests/ -v`
   - Verificar cobertura: `pytest --cov=tests/utils --cov-report=term-missing`
   - Validar com linting: `ruff check tests/`

3. **Comunicação de Mudanças**:
   - Se alguma interface mudar (evitar!), documentar claramente
   - Atualizar docstrings imediatamente
   - Criar mensagens de commit descritivas

### Estimativa de Tempo

- **Dia 1 (4h)**: 
  - Refatorar `llm_evaluator.py` e `evaluation_criteria.py`
  - Rodar testes existentes para validar
  
- **Dia 2 (4h)**:
  - Consolidar testes unitários
  - Fortalecer testes de integração
  - Validar cobertura
  
- **Dia 3 (2-3h)**:
  - Atualizar documentação
  - Code review final
  - Validação completa da suite de testes

## Referências

- Pattern LLM-as-a-Judge: https://arxiv.org/abs/2306.05685
- LangChain ChatOpenAI: https://python.langchain.com/docs/integrations/chat/openai
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest-cov: https://pytest-cov.readthedocs.io/

---

**Notas do Tech Lead**:

Esta tarefa é focada em melhoria de qualidade e manutenibilidade. O framework está funcional e bem testado, mas há oportunidades claras de simplificação sem perda de funcionalidade. O desenvolvedor deve ter autonomia para tomar decisões de refatoração dentro das diretrizes estabelecidas, sempre validando que os testes existentes continuam passando.

Priorize compatibilidade acima de otimização agressiva. Se houver dúvida sobre remover algum código, mantenha e documente a dúvida para discussão.
