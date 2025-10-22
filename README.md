# Sistema de Ingestão e Busca Semântica

Sistema RAG (Retrieval Augmented Generation) baseado em LangChain e PostgreSQL com pgVector para processar documentos PDF e realizar consultas semânticas.

## Estrutura do Projeto

```
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
```

## Requisitos

- Python 3.13.9
- Docker e Docker Compose
- OpenAI API Key

## Configuração

### 1. Clone o Repositório

```bash
git clone <repo-url>
cd mba-ia-desafio-ingestao-busca
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e configure sua OpenAI API Key
# OPENAI_API_KEY=sk-proj-your-api-key-here
```

### 3. Inicie o PostgreSQL

```bash
docker-compose up -d
```

### 4. Configure o Ambiente Python

```bash
# Verifique se está usando Python 3.13.9
python --version  # Deve ser 3.13.9

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 5. Valide o Ambiente

```bash
# Execute o script de validação
python validate_env.py
```

Você deve ver:
```
✅ Ambiente configurado corretamente!
```

## Testes e Validação

### Executar Todos os Testes

```bash
# Executar suite completa de testes
pytest

# Executar com cobertura
pytest --cov=src --cov-report=term --cov-report=html
```

### Validação Completa Automatizada

```bash
# Executar validação completa (testes + cobertura + cenários críticos)
./scripts/run_full_validation.sh
```

O script executa:
1. Limpeza do ambiente
2. Validação de dependências
3. Verificação de variáveis de ambiente
4. Testes unitários
5. Testes de integração
6. Geração de relatório de cobertura
7. Validação de cenários críticos (CT-001, CT-002, CT-003)

### Análise de Cobertura

```bash
# Analisar cobertura detalhada
python scripts/analyze_coverage.py

# Visualizar relatório HTML
open htmlcov/index.html  # macOS
# ou
xdg-open htmlcov/index.html  # Linux
# ou
start htmlcov/index.html  # Windows
```

### Validação Manual

Para validação manual completa, siga o checklist em:
- `docs/manual-validation-checklist.md`

### Métricas de Qualidade

- **Cobertura de Testes**: >= 97%
- **Testes Aprovados**: 57/57 (100%)
- **Cenários Críticos**: CT-001, CT-002, CT-003 validados

Para mais detalhes, consulte:
- `docs/test-results.md` - Resultados detalhados de validação

## Licença

[Definir licença]
