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
import importlib.metadata

required = [
    ('langchain', '0.3.27'),
    ('langchain-openai', '0.3.1'),
    ('langchain-postgres', '0.0.17'),
    ('psycopg', '3.2.11'),
    ('typer', '0.20.0'),
    ('pypdf', '5.1.0'),
    ('python-dotenv', '1.0.1'),
    ('pytest', '8.3.4'),
    ('pytest-cov', '6.0.0'),
]

print('Verificando pacotes...')
missing = []
for package, expected_version in required:
    try:
        version = importlib.metadata.version(package)
        print(f'✅ {package}=={version}')
    except importlib.metadata.PackageNotFoundError:
        print(f'❌ {package} não encontrado')
        missing.append(package)

if missing:
    print(f'\n❌ Pacotes faltando: {missing}')
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
    'DATABASE_URL',
    'OPENAI_API_KEY',
]

missing = []
for var in required_vars:
    value = os.getenv(var)
    if not value:
        missing.append(var)
    elif 'your-' in value or 'sk-proj-your-' in value:
        print(f'⚠️  {var} parece não estar configurada (valor de exemplo)')
        missing.append(var)

if missing:
    print(f'❌ Variáveis faltando ou não configuradas: {missing}')
    exit(1)

print('✅ Todas as variáveis configuradas')
"
echo ""

# 4. Executar testes unitários
echo "4️⃣ Executando testes unitários..."
pytest tests/test_*.py -v --tb=short || {
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
