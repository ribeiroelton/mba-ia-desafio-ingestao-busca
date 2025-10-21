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


## Licença

[Definir licença]
