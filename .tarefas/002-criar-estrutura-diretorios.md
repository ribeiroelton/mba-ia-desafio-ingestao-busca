# [002] - Criar Estrutura de Diretórios e Arquivos de Configuração

## Metadados
- **ID**: 002
- **Grupo**: Fase 1 - Setup e Fundação
- **Prioridade**: Alta
- **Complexidade**: Baixa
- **Estimativa**: 1 dia

## Descrição
Criar a estrutura completa de diretórios do projeto e arquivos de configuração essenciais (`.env.example`, `.gitignore`, estrutura de pastas). Esta tarefa organiza o projeto seguindo padrões Python e prepara o ambiente para desenvolvimento.

## Requisitos

### Requisitos Funcionais
- RF-002: Estrutura de diretórios deve seguir padrões Python
- RF-003: Código Python deve ficar separado em pasta `src/`

### Requisitos Não-Funcionais
- RNF-004: Seguir convenções de estilo PEP 8
- RNF-005: API Keys devem ser armazenadas em `.env` (não versionado)
- RNF-006: Template `.env.example` sem valores reais

## Fonte da Informação
- **Seção 3.3**: Padrões e Convenções - Estrutura de diretórios completa
- **Seção 6.1**: Autenticação e Autorização - API Keys em `.env`
- **Seção 6.2**: Proteção de Dados - Template `.env.example`
- **Seção 9.1**: Decisão sobre estrutura de diretórios

## Stack Necessária
- **Sistema de Arquivos**: Estrutura de pastas e arquivos
- **Ferramentas**: Editor de texto, terminal

## Dependências

### Dependências Técnicas
- Tarefa 001 concluída (Docker Compose criado)
- Repositório Git inicializado

### Dependências de Negócio
- Nenhuma

## Critérios de Aceite

1. [x] Pasta `src/` criada na raiz do projeto
2. [x] Arquivo `.env.example` criado com template de variáveis
3. [x] Arquivo `.gitignore` criado com exclusões apropriadas
4. [x] Estrutura de diretórios corresponde ao documentado na seção 3.3
5. [x] Arquivo `.env` criado localmente (não versionado)
6. [x] Todos os arquivos seguem convenções Python
7. [x] README.md básico criado (será expandido na Tarefa 010)
8. [x] Estrutura validada visualmente e via comando `tree`

## Implementação Resumida

### Estrutura de Arquivos
```
projeto/
├── .env                    # CRIAR (não versionar)
├── .env.example            # CRIAR (versionar)
├── .gitignore              # CRIAR
├── requirements.txt        # Placeholder (será preenchido na Tarefa 003)
├── docker-compose.yaml     # JÁ EXISTE (Tarefa 001)
├── document.pdf            # Placeholder (PDF de exemplo)
├── README.md              # CRIAR (básico)
├── src/                   # CRIAR
│   ├── __init__.py        # CRIAR (módulo Python)
│   ├── ingest.py          # Placeholder (será implementado na Tarefa 004)
│   ├── search.py          # Placeholder (será implementado na Tarefa 005)
│   └── chat.py            # Placeholder (será implementado na Tarefa 006)
└── .tarefas/              # JÁ EXISTE (tarefas)
    └── ...
```

### Componentes a Implementar

#### .env.example
**Arquivo**: `.env.example`
**Responsabilidade**: Template de variáveis de ambiente (sem valores reais)
**Conteúdo**:
```bash
# OpenAI API Configuration (Provedor Padrão)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Google Gemini API Configuration (Alternativa - Opcional)
# GOOGLE_API_KEY=your-google-gemini-api-key-here

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rag
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# LLM Models
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
SEARCH_K=10
```

#### .env
**Arquivo**: `.env`
**Responsabilidade**: Variáveis de ambiente reais (não versionado)
**Conteúdo**: Copiar de `.env.example` e preencher com valores reais

#### .gitignore
**Arquivo**: `.gitignore`
**Responsabilidade**: Excluir arquivos sensíveis e temporários do Git
**Conteúdo**:
```gitignore
# Environment Variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Logs
*.log

# Database
*.db
*.sqlite

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/
.coverage
htmlcov/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
```

#### src/__init__.py
**Arquivo**: `src/__init__.py`
**Responsabilidade**: Marcar `src/` como módulo Python
**Conteúdo**:
```python
"""
Sistema de Ingestão e Busca Semântica com LangChain e PostgreSQL.

Este módulo implementa um sistema RAG (Retrieval Augmented Generation)
para processar documentos PDF e permitir consultas semânticas.
"""

__version__ = "1.0.0"
__author__ = "Equipe de Desenvolvimento"
```

#### requirements.txt
**Arquivo**: `requirements.txt`
**Responsabilidade**: Placeholder para dependências (será preenchido na Tarefa 003)
**Conteúdo**:
```txt
# Dependências serão adicionadas na Tarefa 003
# Ver stack.md para lista completa
```

#### README.md
**Arquivo**: `README.md`
**Responsabilidade**: Documentação básica do projeto (será expandido na Tarefa 010)
**Conteúdo**:
```markdown
# Sistema de Ingestão e Busca Semântica

Sistema RAG (Retrieval Augmented Generation) baseado em LangChain e PostgreSQL com pgVector para processar documentos PDF e realizar consultas semânticas.

## Estrutura do Projeto

\`\`\`
├── .env                    # Variáveis de ambiente (não versionado)
├── .env.example            # Template de variáveis
├── requirements.txt        # Dependências Python
├── docker-compose.yaml     # Configuração Docker
├── document.pdf            # PDF para ingestão
├── README.md              # Este arquivo
└── src/                   # Código-fonte
    ├── ingest.py          # Script de ingestão
    ├── search.py          # Script de busca
    └── chat.py            # CLI interativo
\`\`\`

## Requisitos

- Python 3.13.9
- Docker e Docker Compose
- OpenAI API Key

## Configuração

Documentação completa será adicionada em breve.

## Licença

[Definir licença]
```

#### src/ingest.py (Placeholder)
**Arquivo**: `src/ingest.py`
**Conteúdo**:
```python
"""
Módulo de ingestão de documentos PDF.

Este módulo será implementado na Tarefa 004.
"""

# TODO: Implementar na Tarefa 004
```

#### src/search.py (Placeholder)
**Arquivo**: `src/search.py`
**Conteúdo**:
```python
"""
Módulo de busca semântica.

Este módulo será implementado na Tarefa 005.
"""

# TODO: Implementar na Tarefa 005
```

#### src/chat.py (Placeholder)
**Arquivo**: `src/chat.py`
**Conteúdo**:
```python
"""
Interface CLI interativa para consultas.

Este módulo será implementado na Tarefa 006.
"""

# TODO: Implementar na Tarefa 006
```

### Regras de Negócio a Implementar
- **RN-007**: API Keys nunca devem ser commitadas no repositório
- **RN-008**: Estrutura deve seguir convenções Python (Pythonic)

### Validações Necessárias
- `.env` está no `.gitignore`
- `.env.example` está versionado
- Estrutura de pastas corresponde ao documentado
- Todos os arquivos Python têm encoding UTF-8

### Tratamento de Erros
- **Pasta src/ já existe**: Verificar conteúdo, não sobrescrever
- **Arquivo .env já existe**: Não sobrescrever, avisar usuário
- **Permissões de escrita**: Verificar permissões do diretório

## Testes de Qualidade e Cobertura

### Testes de Integração
**Tipo**: Validação manual de estrutura

**Cenários a Testar**:

1. **Cenário 1: Estrutura de diretórios criada**
   - Comando: `tree -L 2 -a`
   - Expected: Estrutura corresponde ao documentado
   - Validação: Todos os diretórios e arquivos essenciais existem

2. **Cenário 2: .env não está versionado**
   - Comando: `git status`
   - Expected: `.env` não aparece em "Untracked files"
   - Validação: `.env` está listado no `.gitignore`

3. **Cenário 3: .env.example está versionado**
   - Comando: `git add .env.example && git status`
   - Expected: `.env.example` pronto para commit
   - Validação: Arquivo está staged

4. **Cenário 4: src/ é módulo Python válido**
   - Comando: `python -c "import src; print(src.__version__)"`
   - Expected: Imprime versão "1.0.0"
   - Validação: Sem erros de import

5. **Cenário 5: Arquivos têm encoding correto**
   - Comando: `file src/*.py`
   - Expected: Todos arquivos UTF-8
   - Validação: Saída contém "UTF-8"

### Testes de Segurança
1. **API Keys não commitadas**: `git log -p | grep -i "api.*key"` não retorna segredos
2. **.env no gitignore**: `cat .gitignore | grep ".env"`confirma exclusão

## Documentação Necessária

### Código
- [x] Comentários em `.env.example` explicando cada variável
- [x] Docstrings em `src/__init__.py`
- [x] README.md básico criado

### Técnica
- [x] Estrutura de diretórios documentada no README.md
- [x] Instruções de configuração inicial

## Checklist de Finalização

- [x] Pasta `src/` criada com `__init__.py`
- [x] Arquivo `.env.example` criado com todas as variáveis
- [x] Arquivo `.env` criado localmente (não versionado)
- [x] Arquivo `.gitignore` criado com exclusões apropriadas
- [x] Arquivo `requirements.txt` (placeholder) criado
- [x] README.md básico criado
- [x] Placeholders para `ingest.py`, `search.py`, `chat.py` criados
- [x] Estrutura validada com `tree` ou `ls -R`
- [x] Teste de import Python: `python -c "import src"`
- [x] Verificado que `.env` não está versionado
- [x] Verificado que `.env.example` está versionado
- [x] Todos os arquivos seguem encoding UTF-8

## Notas Adicionais

### Comandos Úteis
```bash
# Criar estrutura de uma vez
mkdir -p src
touch src/__init__.py src/ingest.py src/search.py src/chat.py
touch .env.example .gitignore requirements.txt README.md

# Visualizar estrutura
tree -L 2 -a

# ou (se tree não disponível)
find . -maxdepth 2 -not -path '*/\.git/*' -not -path '*/__pycache__/*'

# Verificar .gitignore
git status --ignored

# Testar import Python
python -c "import src; print(src.__version__)"

# Copiar .env.example para .env
cp .env.example .env

# Editar .env com valores reais
nano .env  # ou vim, code, etc
```

### Boas Práticas
- ✅ **Nunca commitar .env**: Sempre verificar antes de `git add .`
- ✅ **Manter .env.example atualizado**: Adicionar novas variáveis conforme necessário
- ✅ **Documentar variáveis**: Adicionar comentários explicativos no `.env.example`
- ✅ **Usar valores placeholder**: `.env.example` deve ter valores de exemplo, não reais

### Variáveis de Ambiente Críticas
1. **OPENAI_API_KEY**: Obrigatória para embeddings e LLM
2. **DATABASE_URL**: Connection string completa do PostgreSQL
3. **CHUNK_SIZE**: 1000 (fixo conforme RN-005)
4. **CHUNK_OVERLAP**: 150 (fixo conforme RN-005)
5. **SEARCH_K**: 10 (fixo conforme RN-006)

### Próximos Passos
Após conclusão desta tarefa:
1. Preencher `.env` com API Key real da OpenAI
2. Tarefa 003: Preencher `requirements.txt` e instalar dependências
3. Tarefas 004-006: Implementar os scripts Python

## Referências
- **PEP 8 - Style Guide**: https://peps.python.org/pep-0008/
- **Python Packaging**: https://packaging.python.org/
- **gitignore Python Template**: https://github.com/github/gitignore/blob/main/Python.gitignore
