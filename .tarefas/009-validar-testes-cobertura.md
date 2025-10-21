# [009] - Validar Cenários de Teste e Cobertura

## Metadados
- **ID**: 009
- **Grupo**: Fase 3 - Qualidade e Entrega
- **Prioridade**: Alta
- **Complexidade**: Baixa
- **Estimativa**: 1 dia

## Descrição
Executar suite completa de testes, validar todos os cenários apresentados no projeto.md (CT-001, CT-002, CT-003), medir cobertura de código e ajustar testes para casos de uso críticos.

## Requisitos

### Requisitos Funcionais
- RF-022: Validação de todos os casos de teste
- RF-023: Relatório de cobertura

### Requisitos Não-Funcionais
- RNF-014: Cobertura >= 80%
- RNF-017: Todos os cenários críticos cobertos
- RNF-018: Relatório de qualidade gerado

## Fonte da Informação
- **Seção 5**: Casos de Teste (CT-001, CT-002, CT-003)
- **Seção 7.2**: Estratégia de Testes

## Stack Necessária
- **Python**: 3.13.9
- **Pytest**: 8.3.4
- **Pytest-cov**: 6.0.0

## Dependências

### Dependências Técnicas
- Tarefa 008: Testes implementados
- Suite de testes completa

## Critérios de Aceite

1. [x] Todos os testes executados
2. [x] CT-001 validado (pergunta com contexto)
3. [x] CT-002 validado (pergunta sem contexto)
4. [x] CT-003 validado (informação parcial)
5. [x] Cobertura >= 80%
6. [x] Relatório HTML gerado
7. [x] Casos críticos identificados
8. [x] Testes ajustados se necessário
9. [x] Zero falhas na suite
10. [x] Documentação de resultados

## Implementação Resumida

### Script de Validação Completa

**Arquivo**: `scripts/run_full_validation.sh`

```bash
#!/bin/bash

# Script de validação completa do sistema

set -e

echo "🧪 Validação Completa - Sistema RAG"
echo "===================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Limpar ambiente
echo "1️⃣ Limpando ambiente de testes..."
rm -rf .pytest_cache htmlcov .coverage
echo -e "${GREEN}✅ Ambiente limpo${NC}"
echo ""

# 2. Validar dependências
echo "2️⃣ Validando dependências..."
python -c "
import sys
import pkg_resources

required = [
    'langchain==0.3.27',
    'langchain-openai==0.3.1',
    'langchain-postgres==0.0.17',
    'psycopg==3.2.11',
    'typer==0.20.0',
    'pypdf==5.1.0',
    'python-dotenv==1.0.1',
    'pytest==8.3.4',
    'pytest-cov==6.0.0',
]

print('Verificando pacotes...')
for package in required:
    try:
        pkg_resources.require(package)
        print(f'✅ {package}')
    except:
        print(f'❌ {package}')
        sys.exit(1)

print('\n✅ Todas as dependências OK')
"
echo ""

# 3. Validar ambiente
echo "3️⃣ Validando variáveis de ambiente..."
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'CONNECTION_STRING',
    'OPENAI_API_KEY',
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f'❌ Variáveis faltando: {missing}')
    exit(1)

print('✅ Todas as variáveis configuradas')
"
echo ""

# 4. Executar testes unitários
echo "4️⃣ Executando testes unitários..."
pytest tests/unit/ -v --tb=short || {
    echo -e "${RED}❌ Testes unitários falharam${NC}"
    exit 1
}
echo -e "${GREEN}✅ Testes unitários OK${NC}"
echo ""

# 5. Executar testes de integração
echo "5️⃣ Executando testes de integração..."
pytest tests/integration/ -v --tb=short || {
    echo -e "${RED}❌ Testes de integração falharam${NC}"
    exit 1
}
echo -e "${GREEN}✅ Testes de integração OK${NC}"
echo ""

# 6. Gerar relatório de cobertura
echo "6️⃣ Gerando relatório de cobertura..."
pytest --cov=src --cov-report=term --cov-report=html --cov-fail-under=80 || {
    echo -e "${RED}❌ Cobertura abaixo de 80%${NC}"
    exit 1
}
echo -e "${GREEN}✅ Cobertura >= 80%${NC}"
echo ""

# 7. Validar cenários críticos
echo "7️⃣ Validando cenários críticos..."

# CT-001: Pergunta com contexto
echo "   Testing CT-001..."
pytest tests/integration/test_e2e.py::test_e2e_flow_with_context -v || {
    echo -e "${RED}❌ CT-001 falhou${NC}"
    exit 1
}

# CT-002: Pergunta sem contexto
echo "   Testing CT-002..."
pytest tests/integration/test_e2e.py::test_e2e_flow_without_context -v || {
    echo -e "${RED}❌ CT-002 falhou${NC}"
    exit 1
}

# CT-003: Informação parcial
echo "   Testing CT-003..."
pytest tests/integration/test_e2e.py::test_e2e_partial_information -v || {
    echo -e "${RED}❌ CT-003 falhou${NC}"
    exit 1
}

echo -e "${GREEN}✅ Todos os cenários críticos OK${NC}"
echo ""

# 8. Resumo final
echo "===================================="
echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA APROVADA${NC}"
echo "===================================="
echo ""
echo "📊 Relatórios gerados:"
echo "   - Terminal: Acima"
echo "   - HTML: htmlcov/index.html"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Revisar relatório HTML de cobertura"
echo "   2. Identificar áreas não cobertas"
echo "   3. Adicionar testes se necessário"
echo "   4. Executar validação manual (chat interativo)"
echo ""
```

### Checklist de Validação Manual

**Arquivo**: `docs/manual-validation-checklist.md`

```markdown
# Checklist de Validação Manual

## 1. Validação de Ingestão

### Teste 1.1: Ingerir PDF válido
- [ ] Executar: `python src/ingest.py tests/fixtures/test_document.pdf`
- [ ] Verificar: Mensagem de sucesso
- [ ] Verificar: Logs mostram número de chunks
- [ ] Verificar: Tempo de processamento razoável

### Teste 1.2: Ingerir PDF inválido
- [ ] Executar: `python src/ingest.py arquivo_inexistente.pdf`
- [ ] Verificar: Mensagem de erro clara
- [ ] Verificar: Sistema não quebra

### Teste 1.3: Verificar chunks no banco
- [ ] Conectar ao PostgreSQL
- [ ] Query: `SELECT COUNT(*) FROM langchain_pg_embedding;`
- [ ] Verificar: Número de embeddings > 0

## 2. Validação de Busca

### Teste 2.1: Busca com resultados
- [ ] Executar busca por termo que existe no documento
- [ ] Verificar: Retorna k=10 ou menos resultados
- [ ] Verificar: Resultados relevantes

### Teste 2.2: Busca sem resultados
- [ ] Executar busca em coleção vazia
- [ ] Verificar: Retorna lista vazia
- [ ] Verificar: Sem erros

## 3. Validação de Chat (CT-001)

### Teste 3.1: Pergunta DENTRO do contexto
```
Pergunta: "Qual foi o faturamento da SuperTechIABrazil?"
Resposta esperada: "10 milhões de reais" ou similar
```

- [ ] Executar: `python src/chat.py`
- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta contém informação correta
- [ ] Verificar: Resposta NÃO é mensagem padrão

### Teste 3.2: Pergunta FORA do contexto (CT-002)
```
Pergunta: "Qual é a capital da França?"
Resposta esperada: "Não tenho informações necessárias para responder sua pergunta."
```

- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta é exatamente a mensagem padrão
- [ ] Verificar: LLM não inventou resposta

### Teste 3.3: Informação parcial (CT-003)
```
Pergunta: "Quantos funcionários internacionais a empresa tem?"
Resposta esperada: Admissão de limitação ou resposta parcial
```

- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta é coerente
- [ ] Verificar: Se informação não existe, admite limitação

### Teste 3.4: Comandos de saída
```
Comando: quit / exit / sair
```

- [ ] Testar comando "quit"
- [ ] Testar comando "exit"
- [ ] Testar comando "sair"
- [ ] Verificar: Chat encerra gracefully

## 4. Validação de Regras de Negócio

### RN-001: Respostas baseadas no contexto
- [ ] Fazer 5 perguntas dentro do contexto
- [ ] Verificar: Todas as respostas baseadas em documentos
- [ ] Fazer 5 perguntas fora do contexto
- [ ] Verificar: Todas retornam mensagem padrão

### RN-003: Chunk size
- [ ] Query: `SELECT LENGTH(document) FROM langchain_pg_embedding;`
- [ ] Verificar: Todos os chunks <= 1500 caracteres

### RN-006: Top K=10
- [ ] Fazer busca qualquer
- [ ] Verificar código: `k=10` fixo
- [ ] Verificar resultado: máximo 10 itens

## 5. Validação de Performance

### Teste 5.1: Tempo de ingestão
- [ ] Ingerir PDF de ~10 páginas
- [ ] Verificar: Tempo < 60 segundos

### Teste 5.2: Tempo de busca
- [ ] Fazer busca semântica
- [ ] Verificar: Tempo < 5 segundos

### Teste 5.3: Tempo de resposta
- [ ] Fazer pergunta completa (busca + LLM)
- [ ] Verificar: Tempo < 15 segundos

## 6. Validação de Tratamento de Erros

### Teste 6.1: OpenAI API Key inválida
- [ ] Temporariamente invalidar key
- [ ] Tentar fazer pergunta
- [ ] Verificar: Erro claro e descritivo

### Teste 6.2: PostgreSQL desconectado
- [ ] Parar container do PostgreSQL
- [ ] Tentar ingerir documento
- [ ] Verificar: Erro de conexão claro

### Teste 6.3: Pergunta vazia
- [ ] Submeter pergunta vazia no chat
- [ ] Verificar: Tratamento adequado

## 7. Validação de Cobertura

### Análise do Relatório HTML
- [ ] Abrir `htmlcov/index.html`
- [ ] Verificar: Cobertura total >= 80%
- [ ] Verificar: `src/ingest.py` >= 80%
- [ ] Verificar: `src/search.py` >= 80%
- [ ] Verificar: `src/chat.py` >= 80%
- [ ] Identificar: Linhas não cobertas
- [ ] Avaliar: Necessidade de testes adicionais

## Assinatura

**Testado por**: _________________
**Data**: _________________
**Resultado**: [ ] Aprovado [ ] Reprovado
**Observações**: 
```

### Análise de Cobertura

**Arquivo**: `scripts/analyze_coverage.py`

```python
"""
Analisa relatório de cobertura e identifica gaps.
"""
import json
import sys
from pathlib import Path


def load_coverage_report():
    """Carrega relatório de cobertura."""
    coverage_file = Path(".coverage")
    
    if not coverage_file.exists():
        print("❌ Arquivo .coverage não encontrado")
        print("   Execute: pytest --cov=src")
        sys.exit(1)
    
    # Importar coverage para análise
    from coverage import Coverage
    
    cov = Coverage()
    cov.load()
    
    return cov


def analyze_module_coverage(cov, module_path):
    """Analisa cobertura de um módulo específico."""
    analysis = cov.analysis(module_path)
    
    # analysis = (filename, executed, excluded, missing)
    filename, executed, excluded, missing = analysis
    
    total_lines = len(executed) + len(missing)
    coverage_pct = (len(executed) / total_lines * 100) if total_lines > 0 else 0
    
    return {
        "filename": filename,
        "total_lines": total_lines,
        "executed": len(executed),
        "missing": len(missing),
        "coverage": coverage_pct,
        "missing_lines": sorted(missing),
    }


def main():
    """Análise principal."""
    print("📊 Análise de Cobertura\n")
    
    cov = load_coverage_report()
    
    # Módulos a analisar
    modules = [
        "src/ingest.py",
        "src/search.py",
        "src/chat.py",
    ]
    
    results = []
    
    for module in modules:
        try:
            result = analyze_module_coverage(cov, module)
            results.append(result)
        except Exception as e:
            print(f"⚠️  Erro ao analisar {module}: {e}")
    
    # Exibir resultados
    print("=" * 70)
    print(f"{'Módulo':<30} {'Cobertura':<15} {'Linhas':<15}")
    print("=" * 70)
    
    total_coverage = 0
    
    for result in results:
        module_name = result['filename'].split('/')[-1]
        coverage = result['coverage']
        lines = f"{result['executed']}/{result['total_lines']}"
        
        # Cor baseada em cobertura
        if coverage >= 80:
            status = "✅"
        elif coverage >= 60:
            status = "⚠️ "
        else:
            status = "❌"
        
        print(f"{status} {module_name:<27} {coverage:>6.1f}%       {lines:<15}")
        
        # Linhas não cobertas
        if result['missing_lines']:
            print(f"   Linhas não cobertas: {result['missing_lines'][:10]}")
            if len(result['missing_lines']) > 10:
                print(f"   ... e mais {len(result['missing_lines']) - 10} linhas")
        
        total_coverage += coverage
    
    print("=" * 70)
    
    avg_coverage = total_coverage / len(results) if results else 0
    
    print(f"\n📈 Cobertura Média: {avg_coverage:.1f}%")
    
    if avg_coverage >= 80:
        print("✅ Cobertura adequada (>= 80%)")
        return 0
    else:
        print("❌ Cobertura insuficiente (< 80%)")
        print("\n🎯 Ações recomendadas:")
        print("   1. Adicionar testes para linhas não cobertas")
        print("   2. Revisar se linhas são realmente testáveis")
        print("   3. Considerar remover código não utilizado")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Testes de Qualidade e Cobertura

### Executar Validação Completa

```bash
# Dar permissão de execução
chmod +x scripts/run_full_validation.sh

# Executar validação
./scripts/run_full_validation.sh

# Analisar cobertura detalhada
python scripts/analyze_coverage.py

# Abrir relatório HTML
open htmlcov/index.html
```

### Métricas de Sucesso

| Métrica | Meta | Como Validar |
|---------|------|--------------|
| Cobertura Total | >= 80% | `pytest --cov=src` |
| Testes Unitários | 100% pass | `pytest tests/unit/` |
| Testes Integração | 100% pass | `pytest tests/integration/` |
| CT-001 | Pass | Teste manual ou `test_e2e_flow_with_context` |
| CT-002 | Pass | Teste manual ou `test_e2e_flow_without_context` |
| CT-003 | Pass | Teste manual ou `test_e2e_partial_information` |

## Checklist de Finalização

- [x] Script de validação completa criado
- [x] Todos os testes executados
- [x] CT-001, CT-002, CT-003 validados
- [x] Cobertura >= 80%
- [x] Relatório HTML gerado e revisado
- [x] Script de análise de cobertura criado
- [x] Checklist de validação manual criado
- [x] Gaps de cobertura identificados
- [x] Testes ajustados se necessário
- [x] Documentação atualizada

## Notas Adicionais

### Interpretando Relatório de Cobertura

O relatório HTML (`htmlcov/index.html`) mostra:
- **Verde**: Linhas executadas (cobertas)
- **Vermelho**: Linhas não executadas (não cobertas)
- **Amarelo**: Linhas parcialmente executadas (branches)

### Ações Corretivas

**Se cobertura < 80%**:
1. Identificar módulos com baixa cobertura
2. Adicionar testes específicos para linhas não cobertas
3. Re-executar validação

**Se testes falharem**:
1. Revisar logs de erro
2. Ajustar implementação ou teste
3. Re-executar teste específico: `pytest path/to/test.py::test_name -v`

### Validação Manual Obrigatória

Mesmo com 80%+ de cobertura automatizada, execute validação manual:
1. Chat interativo (CT-001, CT-002, CT-003)
2. Tratamento de erros
3. Usabilidade da CLI

## Referências
- **Coverage.py**: https://coverage.readthedocs.io/
- **Pytest Coverage**: https://pytest-cov.readthedocs.io/
- **Testing Best Practices**: https://testdriven.io/blog/testing-best-practices/
