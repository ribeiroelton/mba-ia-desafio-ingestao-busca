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

Documentação completa será adicionada em breve.

## Licença

[Definir licença]
