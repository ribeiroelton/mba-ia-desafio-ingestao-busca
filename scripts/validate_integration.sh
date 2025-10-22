#!/bin/bash

# Script de validação manual de integração
# Valida ambiente, dependências e componentes do sistema RAG

set -e

echo "🔍 Validação de Integração - Sistema RAG"
echo "=========================================="

# 1. Validar ambiente
echo ""
echo "1️⃣ Validando ambiente Python..."
python3 -c "
import sys
assert sys.version_info >= (3, 13), 'Python 3.13+ necessário'
print(f'✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
"

# 2. Validar dependências
echo ""
echo "2️⃣ Validando dependências..."
python3 -c "
try:
    import langchain
    import langchain_openai
    import langchain_postgres
    import typer
    import psycopg
    print('✅ Dependências instaladas')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    exit(1)
"

# 3. Validar PostgreSQL
echo ""
echo "3️⃣ Validando PostgreSQL..."
python3 -c "
import os
import sys
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print('❌ DATABASE_URL não configurada')
    sys.exit(1)

try:
    import psycopg
    # Converter postgresql+psycopg:// para postgresql://
    conn_str = database_url.replace('postgresql+psycopg://', 'postgresql://')
    conn = psycopg.connect(conn_str)
    conn.close()
    print('✅ PostgreSQL conectado')
except Exception as e:
    print(f'❌ Erro ao conectar PostgreSQL: {e}')
    print('⚠️  Certifique-se de que o Docker está rodando: docker-compose up -d')
    sys.exit(1)
"

# 4. Validar OpenAI API
echo ""
echo "4️⃣ Validando OpenAI API..."
python3 -c "
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print('❌ OPENAI_API_KEY não configurada')
    sys.exit(1)

try:
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
    result = embeddings.embed_query('teste')
    assert len(result) > 0
    print('✅ OpenAI API funcionando')
except Exception as e:
    print(f'❌ Erro ao validar OpenAI: {e}')
    sys.exit(1)
"

# 5. Validar arquivo de teste
echo ""
echo "5️⃣ Validando arquivo de teste..."
if [ -f "document.pdf" ]; then
    echo "✅ document.pdf encontrado"
else
    echo "❌ document.pdf não encontrado na raiz do projeto"
    exit 1
fi

# 6. Teste de ingestão
echo ""
echo "6️⃣ Testando ingestão..."
python3 -c "
from src.ingest import load_pdf, split_documents
from pathlib import Path

pdf_path = Path('document.pdf')
documents = load_pdf(str(pdf_path))
chunks = split_documents(documents)

print(f'✅ Ingestão OK - {len(documents)} páginas, {len(chunks)} chunks')
"

# 7. Validar configuração de chunks
echo ""
echo "7️⃣ Validando RN-003 (chunk size 1000/150)..."
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '150'))

assert chunk_size == 1000, f'CHUNK_SIZE deve ser 1000, é {chunk_size}'
assert chunk_overlap == 150, f'CHUNK_OVERLAP deve ser 150, é {chunk_overlap}'

print(f'✅ Chunk size: {chunk_size}, Overlap: {chunk_overlap}')
"

# 8. Validar k=10
echo ""
echo "8️⃣ Validando RN-006 (k=10)..."
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

search_k = int(os.getenv('SEARCH_K', '10'))
assert search_k == 10, f'SEARCH_K deve ser 10, é {search_k}'

print(f'✅ SEARCH_K configurado: {search_k}')
"

# 9. Informação sobre testes manuais
echo ""
echo "=========================================="
echo "✅ Validação Automática Completa"
echo ""
echo "📋 Próximos passos para validação manual:"
echo ""
echo "1. Execute os testes de integração:"
echo "   pytest tests/integration/test_e2e.py -v"
echo ""
echo "2. Teste o chat interativo:"
echo "   python src/ingest.py document.pdf --collection validation_test"
echo "   python src/chat.py --collection validation_test"
echo ""
echo "   Testes no chat:"
echo "   - Pergunta DENTRO do contexto (ex: 'O que é RAG?')"
echo "   - Pergunta FORA do contexto (ex: 'Qual a capital da França?')"
echo "   - Digite 'quit' para sair"
echo ""
echo "3. Validar que RN-001 e RN-002 estão sendo respeitadas:"
echo "   - Respostas dentro do contexto devem ser específicas"
echo "   - Respostas fora do contexto devem retornar mensagem padrão"
echo ""
