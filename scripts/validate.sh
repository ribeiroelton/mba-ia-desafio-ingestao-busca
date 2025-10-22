#!/bin/bash

# Script de validação completa do ambiente e sistema RAG
# Uso: ./scripts/validate.sh

set -e

echo "🔍 Validação Completa - Sistema RAG"
echo "===================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Validar Python
echo "1️⃣ Validando Python..."
python3 --version | grep -q "3.13" && echo -e "${GREEN}✅ Python 3.13+${NC}" || {
    echo -e "${RED}❌ Python 3.13+ necessário${NC}"
    exit 1
}

# 2. Validar dependências
echo ""
echo "2️⃣ Validando dependências..."
python3 -c "
import sys
try:
    import langchain
    import langchain_openai
    import langchain_postgres
    import typer
    import pytest
    print('✅ Dependências instaladas')
except ImportError as e:
    print(f'❌ Erro: {e}')
    print('Execute: pip install -r requirements.txt')
    sys.exit(1)
"

# 3. Validar variáveis de ambiente
echo ""
echo "3️⃣ Validando variáveis de ambiente..."
python3 -c "
import os
import sys
from dotenv import load_dotenv

load_dotenv()

errors = []

# DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    errors.append('DATABASE_URL não configurada')
elif 'postgresql' not in db_url:
    errors.append('DATABASE_URL inválida')
else:
    print('✅ DATABASE_URL configurada')

# OPENAI_API_KEY
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    errors.append('OPENAI_API_KEY não configurada')
elif 'sk-' not in api_key or 'your' in api_key:
    errors.append('OPENAI_API_KEY parece inválida')
else:
    print('✅ OPENAI_API_KEY configurada')

if errors:
    print('\n❌ Problemas encontrados:')
    for err in errors:
        print(f'   - {err}')
    print('\nCrie um arquivo .env com:')
    print('DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag')
    print('OPENAI_API_KEY=sk-proj-sua-chave')
    sys.exit(1)
"

# 4. Validar PostgreSQL
echo ""
echo "4️⃣ Validando PostgreSQL..."
python3 -c "
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import psycopg
    db_url = os.getenv('DATABASE_URL', '').replace('postgresql+psycopg://', 'postgresql://')
    conn = psycopg.connect(db_url, connect_timeout=5)
    conn.close()
    print('✅ PostgreSQL conectado')
except Exception as e:
    print(f'❌ PostgreSQL não acessível: {e}')
    print('\nInicie o banco: docker-compose up -d')
    sys.exit(1)
"

# 5. Validar OpenAI API
echo ""
echo "5️⃣ Validando OpenAI API..."
python3 -c "
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
    # Teste rápido
    result = embeddings.embed_query('teste')
    assert len(result) > 0
    print('✅ OpenAI API funcionando')
except Exception as e:
    print(f'❌ OpenAI API com problemas: {e}')
    print('\nVerifique sua chave em: https://platform.openai.com/api-keys')
    sys.exit(1)
"

# 6. Executar testes unitários
echo ""
echo "6️⃣ Executando testes unitários..."
pytest tests/unit/ -v --tb=short -q || {
    echo -e "${RED}❌ Testes unitários falharam${NC}"
    exit 1
}
echo -e "${GREEN}✅ Testes unitários OK${NC}"

# 7. Executar testes de integração (apenas coleta)
echo ""
echo "7️⃣ Verificando testes de integração..."
pytest tests/integration/ --co -q > /dev/null && {
    echo -e "${GREEN}✅ Testes de integração disponíveis${NC}"
} || {
    echo -e "${YELLOW}⚠️  Problemas com testes de integração${NC}"
}

# Resumo
echo ""
echo "========================================"
echo -e "${GREEN}✅ Validação Completa${NC}"
echo "========================================"
echo ""
echo "Sistema pronto para uso!"
echo ""
echo "Próximos passos:"
echo "  1. Ingerir um PDF:  python src/ingest.py documento.pdf"
echo "  2. Iniciar chat:    python src/chat.py"
echo "  3. Rodar testes:    pytest"
echo ""
