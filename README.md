# Sistema RAG - Ingestão e Busca Semântica

![Python](https://img.shields.io/badge/python-3.13+-blue)
![LangChain](https://img.shields.io/badge/langchain-0.3.27-green)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

Sistema de **Retrieval Augmented Generation (RAG)** para ingestão de documentos PDF e consultas semânticas com respostas baseadas **exclusivamente** no conteúdo dos documentos.

## 🎯 O que faz?

Este sistema implementa um pipeline completo de RAG:

1. **Ingere documentos PDF** → Divide em chunks e armazena embeddings
2. **Busca semântica** → Encontra os 10 trechos mais relevantes
3. **Responde perguntas** → Usa LLM baseado **exclusivamente** no contexto encontrado

### ✨ Características Principais

- ✅ Respostas baseadas **somente** no conteúdo dos documentos
- ✅ Mensagem clara quando a informação não está disponível
- ✅ Interface CLI simples e intuitiva
- ✅ Testes automatizados com avaliação LLM (LLM-as-a-Judge)
- ✅ Validação completa de regras de negócio

## 🚀 Início Rápido

### 1. Pré-requisitos

- Python 3.13+
- Docker (para PostgreSQL)
- Chave de API da OpenAI

### 2. Instalação

\`\`\`bash
# Clone o repositório
git clone https://github.com/ribeiroelton/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Inicie o PostgreSQL
docker-compose up -d
\`\`\`

### 3. Configure as Variáveis de Ambiente

Crie um arquivo \`.env\` na raiz do projeto:

\`\`\`bash
# PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# OpenAI
OPENAI_API_KEY=sk-proj-sua-chave-aqui
\`\`\`

## 💡 Como Usar

### Ingerir Documentos

\`\`\`bash
# Ingerir um PDF
python src/ingest.py documento.pdf

# Com nome de coleção personalizado
python src/ingest.py relatorio.pdf --collection relatorios_2024
\`\`\`

**Saída esperada:**
\`\`\`
📄 Carregando PDF: documento.pdf
✓ 15 páginas carregadas
✂️  Dividindo em chunks...
✓ 45 chunks criados
💾 Armazenando embeddings...
✅ Ingestão concluída!
\`\`\`

### Fazer Perguntas (Chat)

\`\`\`bash
# Iniciar chat
python src/chat.py

# Com coleção específica
python src/chat.py --collection relatorios_2024
\`\`\`

**Exemplo de uso:**

\`\`\`
🤖 Sistema de Busca Semântica
Digite 'sair' para encerrar

💬 Sua pergunta: Qual foi o faturamento em 2024?

🔍 Buscando...
�� Gerando resposta...

📝 Resposta:
O faturamento da empresa em 2024 foi de 10 milhões de reais.

💬 Sua pergunta: Qual é a capital da França?

📝 Resposta:
Não tenho informações necessárias para responder sua pergunta.

💬 Sua pergunta: sair
👋 Até logo!
\`\`\`

## 🧪 Testes

### Executar Testes

\`\`\`bash
# Suite completa (unitários + integração)
pytest

# Apenas testes rápidos (unitários, < 1s)
pytest tests/unit/ -v

# Apenas testes de integração (~50-60s)
pytest tests/integration/ -v

# Com relatório de cobertura
pytest --cov=src --cov-report=html
open htmlcov/index.html
\`\`\`

### Validação Completa do Ambiente

Use o script de validação para verificar todo o sistema:

\`\`\`bash
chmod +x scripts/validate.sh
./scripts/validate.sh
\`\`\`

Este script verifica:
- ✅ Python 3.13+ instalado
- ✅ Dependências instaladas
- ✅ Variáveis de ambiente configuradas
- ✅ PostgreSQL rodando e acessível
- ✅ OpenAI API funcionando
- ✅ Todos os testes unitários passando

## 📋 Regras de Negócio

| Regra | Descrição |
|-------|-----------|
| **RN-001** | Respostas baseadas **exclusivamente** no contexto recuperado |
| **RN-002** | Mensagem padrão quando informação não disponível: _"Não tenho informações necessárias para responder sua pergunta."_ |
| **RN-003** | Sistema nunca usa conhecimento externo ao documento |
| **RN-004** | Respostas objetivas e diretas |
| **RN-005** | Chunks de 1000 caracteres com overlap de 150 |
| **RN-006** | Busca retorna exatamente 10 resultados (k=10) |

## ��️ Arquitetura

\`\`\`
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  ingest.py  │─────▶│  PostgreSQL  │◀─────│  search.py  │
│ (PDFs → DB) │      │  + pgVector  │      │ (Busca)     │
└─────────────┘      └──────────────┘      └─────────────┘
                            ↓                       ↓
                       Embeddings            ┌─────────────┐
                        (OpenAI)             │  chat.py    │
                                             │  (CLI)      │
                                             └─────────────┘
                                                    ↓
                                             ┌─────────────┐
                                             │ OpenAI LLM  │
                                             │ (Resposta)  │
                                             └─────────────┘
\`\`\`

### Componentes

- **src/ingest.py**: Processa PDFs e armazena embeddings
- **src/search.py**: Busca semântica por similaridade de cosseno
- **src/chat.py**: Interface CLI para perguntas/respostas
- **PostgreSQL + pgVector**: Armazenamento de embeddings com extensão pgVector
- **OpenAI**: Embeddings (text-embedding-3-small) + LLM (gpt-4o-mini)

## 🔧 Troubleshooting

### Erro: "Connection refused" (PostgreSQL)

\`\`\`bash
# Verificar se está rodando
docker ps | grep postgres

# Iniciar se necessário
docker-compose up -d

# Verificar logs
docker-compose logs postgres
\`\`\`

### Erro: "Invalid API key"

1. Verifique se o arquivo \`.env\` existe na raiz do projeto
2. Confirme que \`OPENAI_API_KEY\` está configurada corretamente
3. Teste a chave em: https://platform.openai.com/api-keys

### Erro: "ModuleNotFoundError"

\`\`\`bash
# Certifique-se que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/Mac

# Reinstale as dependências
pip install -r requirements.txt
\`\`\`

### LLM inventa informações (não segue RN-003)

O sistema está configurado para **nunca** usar conhecimento externo. Se isso ocorrer:

1. Verifique o \`SYSTEM_PROMPT\` em \`src/chat.py\`
2. Execute os testes de integração: \`pytest tests/integration/test_business_rules.py -v\`
3. Os testes com LLM-as-a-Judge detectarão violações automaticamente

## 📁 Estrutura do Projeto

\`\`\`
mba-ia-desafio-ingestao-busca/
├── src/
│   ├── __init__.py
│   ├── ingest.py          # Ingestão de PDFs
│   ├── search.py          # Busca semântica
│   └── chat.py            # Interface CLI
├── tests/
│   ├── conftest.py        # Fixtures compartilhadas
│   ├── unit/              # Testes unitários (31 testes)
│   │   ├── test_chat_validation.py
│   │   ├── test_ingest_validation.py
│   │   ├── test_search_validation.py
│   │   └── test_llm_evaluator_unit.py
│   ├── integration/       # Testes E2E (24 testes)
│   │   ├── test_business_rules.py
│   │   ├── test_e2e_core.py
│   │   ├── test_llm_quality_evaluation.py
│   │   └── test_real_scenarios.py
│   └── utils/             # Framework de avaliação LLM
│       ├── llm_evaluator.py
│       └── evaluation_criteria.py
├── scripts/
│   └── validate.sh        # Script de validação completa
├── docker-compose.yaml    # PostgreSQL + pgVector
├── requirements.txt       # Dependências Python
├── pytest.ini             # Configuração de testes
├── .env                   # Configurações (criar manualmente)
└── README.md              # Este arquivo
\`\`\`

## 📊 Métricas de Qualidade

Nossa suite de testes inclui **avaliação automatizada com LLM-as-a-Judge**:

### Testes
- **31 testes unitários** (validação rápida, < 1s)
- **24 testes de integração** (18 com avaliação LLM)
- **Cobertura**: 64%+ (focada em código crítico)
- **Tempo de execução**: ~50-60s
- **Custo por execução**: ~$0.03-0.05

### LLM-as-a-Judge

18 testes de integração (75%) incluem avaliação automatizada de qualidade com 4 critérios:

1. **Aderência ao Contexto** (30%) - Valida RN-001
2. **Detecção de Alucinação** (30%) - Valida RN-003
3. **Seguimento de Regras** (25%) - Valida RN-002, RN-003, RN-004
4. **Clareza e Objetividade** (15%) - Valida RN-004

**Threshold**: 70/100 (testes falham se qualidade cai abaixo)

Para mais detalhes sobre os testes, consulte [tests/README.md](tests/README.md).

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: \`git checkout -b feature/nova-funcionalidade\`
3. Commit suas mudanças: \`git commit -m 'Adiciona nova funcionalidade'\`
4. Push para a branch: \`git push origin feature/nova-funcionalidade\`
5. Abra um Pull Request

### Requisitos para Contribuição

- Adicione testes para novas funcionalidades
- Mantenha a cobertura acima de 60%
- Siga PEP 8 para estilo de código
- Documente funções públicas com docstrings
- Execute \`./scripts/validate.sh\` antes de commitar

## 📝 Licença

Este projeto está sob a licença Apache 2.0. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🔗 Links Úteis

### Documentação
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [pgVector Extension](https://github.com/pgvector/pgvector)
- [Typer CLI Framework](https://typer.tiangolo.com/)

### Tutoriais
- [RAG Tutorial - LangChain](https://python.langchain.com/docs/tutorials/rag/)
- [PostgreSQL + pgVector Guide](https://github.com/langchain-ai/langchain-postgres)

---

**Desenvolvido como parte do MBA em Inteligência Artificial**

Para dúvidas ou suporte, abra uma [issue](https://github.com/ribeiroelton/mba-ia-desafio-ingestao-busca/issues) no repositório.
