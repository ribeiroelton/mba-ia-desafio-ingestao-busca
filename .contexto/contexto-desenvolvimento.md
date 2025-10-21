# Contexto de Desenvolvimento - Sistema de Ingestão e Busca Semântica

## 1. Visão Geral do Projeto

### 1.1 Resumo Executivo
Sistema de ingestão e busca semântica baseado em LangChain e PostgreSQL com pgVector. O software permite processar documentos PDF, armazená-los como embeddings vetoriais e realizar consultas semânticas através de uma interface CLI, retornando respostas contextualizadas baseadas exclusivamente no conteúdo ingerido.

### 1.2 Objetivos de Negócio
- Permitir ingestão automatizada de documentos PDF em base de dados vetorial
- Possibilitar consultas em linguagem natural sobre o conteúdo dos documentos
- Garantir respostas precisas baseadas apenas no contexto disponível
- Prevenir alucinações do modelo evitando respostas fora do contexto

### 1.3 Escopo
**Inclui:**
- Ingestão de arquivos PDF com chunking e vetorização
- Armazenamento de embeddings em PostgreSQL com pgVector
- Interface CLI para consultas em linguagem natural
- Busca semântica por similaridade vetorial
- Geração de respostas contextualizadas via LLM
- Validação de respostas baseadas no contexto disponível

**Exclui:**
- Interface gráfica web ou mobile
- Múltiplos formatos de documentos (apenas PDF)
- Autenticação e controle de acesso
- Histórico de conversações persistente
- Análise de sentimentos ou classificação de documentos

## 2. Domínio e Requisitos de Negócio

### 2.1 Contexto do Domínio
Sistema de RAG (Retrieval Augmented Generation) para permitir consultas precisas sobre documentos corporativos. O sistema atua como um assistente que responde perguntas baseando-se exclusivamente no conteúdo de documentos previamente processados, evitando informações externas ou alucinações do modelo de linguagem.

### 2.2 Personas e Usuários
- **Analista de Dados**: Necessita consultar informações específicas em documentos corporativos de forma rápida e precisa, sem precisar ler todo o conteúdo manualmente.
- **Gestor de Negócios**: Busca informações de relatórios e documentos para tomada de decisão, esperando respostas diretas e confiáveis.

### 2.3 Processos de Negócio

#### Processo de Ingestão de Documentos
1. Usuário executa script de ingestão informando o documento PDF
2. Sistema carrega e divide o PDF em chunks de texto
3. Sistema gera embeddings para cada chunk
4. Sistema armazena chunks e embeddings no banco de dados vetorial
5. Processo finaliza com confirmação de sucesso

**Atores**: Usuário técnico (analista, desenvolvedor)
**Regras**: 
- Chunks devem ter 1000 caracteres
- Overlap entre chunks deve ser de 150 caracteres
- Apenas arquivos PDF são aceitos

#### Processo de Consulta Semântica
1. Usuário inicia interface CLI
2. Usuário digita pergunta em linguagem natural
3. Sistema vetoriza a pergunta
4. Sistema busca os 10 chunks mais similares no banco
5. Sistema monta prompt com contexto recuperado
6. Sistema envia prompt para LLM
7. Sistema valida resposta da LLM
8. Sistema exibe resposta ao usuário
9. Usuário pode fazer nova pergunta ou sair

**Atores**: Usuário final (analista, gestor)
**Regras**:
- Sempre buscar exatamente 10 resultados (k=10)
- Responder apenas com base no contexto recuperado
- Informar explicitamente quando não houver informação suficiente

### 2.4 Regras de Negócio
- **[RN-001]**: Respostas devem ser baseadas exclusivamente no contexto recuperado do banco de dados
- **[RN-002]**: Quando a informação não estiver no contexto, o sistema deve responder: "Não tenho informações necessárias para responder sua pergunta."
- **[RN-003]**: O sistema nunca deve inventar informações ou usar conhecimento externo
- **[RN-004]**: O sistema nunca deve produzir opiniões ou interpretações além do que está escrito
- **[RN-005]**: Chunks de texto devem ter exatamente 1000 caracteres com overlap de 150 caracteres
- **[RN-006]**: A busca semântica deve retornar sempre os 10 resultados mais relevantes (k=10)

### 2.5 Entidades Principais
- **Documento**: Arquivo PDF a ser processado e armazenado
  - Atributos: caminho, nome, conteúdo
  
- **Chunk**: Fragmento de texto extraído do documento
  - Atributos: texto, índice, documento_origem, embedding
  - Relacionamentos: pertence a um Documento
  
- **Embedding**: Representação vetorial de um chunk de texto
  - Atributos: vetor (dimensões variáveis conforme modelo), chunk_id
  - Relacionamentos: representa um Chunk
  
- **Consulta**: Pergunta feita pelo usuário
  - Atributos: texto_pergunta, embedding_pergunta, timestamp
  
- **Resultado**: Resposta gerada pelo sistema
  - Atributos: texto_resposta, chunks_utilizados, score_similaridade, timestamp
  - Relacionamentos: relacionada a uma Consulta

## 3. Arquitetura e Tecnologias

### 3.1 Stack Tecnológico

#### Backend
- **Python**: 3.13.9 - Linguagem principal do projeto
- **LangChain**: 0.3.27 - Framework para orquestração de LLMs e RAG
- **langchain_core**: 0.3.79 - Componentes centrais do LangChain
- **langchain_text_splitters**: 0.3.11 - Divisão de documentos em chunks
- **langchain_openai**: 0.3.35 - Integração com APIs da OpenAI
- **langchain_google_genai**: 2.1.12 - Integração com APIs do Google Gemini
- **langchain_postgres**: 0.0.16 - Integração com PostgreSQL e pgVector
- **langchain-community**: 0.4 - Componentes comunitários (PyPDFLoader)
- **Pydantic**: 2.12.3 - Validação de dados e configurações
- **Typer**: 0.20.0 - Framework para criação de CLI
- **psycopg**: 3.2.11 - Driver PostgreSQL para Python (conexão com banco de dados)
- **psycopg-binary**: 3.2.11 - Versão binária do psycopg
- **psycopg-pool**: 3.2.6 - Pool de conexões para psycopg

#### Banco de Dados
- **PostgreSQL**: 17 (pgvector/pgvector:pg17) - Banco de dados relacional
- **pgVector**: Extensão para armazenamento e busca de vetores

#### Infraestrutura
- **Docker**: Containerização do banco de dados
- **Docker Compose**: Orquestração de containers seguindo Docker Compose Specification

#### Ferramentas e Serviços
- **pip**: Gerenciador de pacotes Python (padrão)
- **OpenAI API**: 
  - Modelo de embeddings: text-embedding-3-small
  - Modelo de LLM: gpt-5-nano
- **Google Gemini API** (alternativa):
  - Modelo de embeddings: models/embedding-001
  - Modelo de LLM: gemini-2.5-flash-lite

### 3.2 Arquitetura do Sistema

#### Padrão Arquitetural
Arquitetura modular baseada em scripts Python independentes, seguindo o padrão RAG (Retrieval Augmented Generation):
- **Camada de Ingestão**: Processa documentos e armazena embeddings
- **Camada de Persistência**: PostgreSQL com pgVector
- **Camada de Consulta**: Busca semântica e geração de respostas
- **Camada de Apresentação**: CLI interativo

#### Diagrama de Componentes
```
[document.pdf] 
    ↓
[ingest.py] → [PyPDFLoader] → [RecursiveCharacterTextSplitter]
    ↓
[OpenAI Embeddings - text-embedding-3-small] (padrão)
    ↓
[PGVector] ← [PostgreSQL + pgVector Extension]
              (localhost:5432, database: rag)
    ↑
[search.py] → [similarity_search_with_score(k=10)]
    ↓
[OpenAI LLM - gpt-5-nano] (padrão)
    ↓
[chat.py] → [CLI Interface (Typer)]
    ↓
[Usuário]

Alternativa: Gemini (embedding-001 + gemini-2.5-flash-lite)
```

**Componentes principais**:
1. **ingest.py**: Carrega PDF, divide em chunks, gera embeddings e armazena no banco
2. **search.py**: Implementa busca semântica por similaridade vetorial
3. **chat.py**: Interface CLI para interação com o usuário
4. **PGVector**: Armazenamento e recuperação de vetores
5. **LangChain**: Orquestração de componentes RAG

#### Decisões Arquiteturais
- **[DA-001]**: Uso de PostgreSQL com pgVector - Justificativa: Permite combinar dados estruturados com busca vetorial em um único banco, simplificando a arquitetura e manutenção
- **[DA-002]**: Scripts Python independentes ao invés de aplicação monolítica - Justificativa: Separação clara de responsabilidades, facilita testes e manutenção
- **[DA-003]**: LangChain como framework RAG - Justificativa: Abstrações prontas para chunking, embeddings e integração com LLMs, reduz código boilerplate
- **[DA-004]**: CLI com Typer - Justificativa: Interface simples e eficiente para casos de uso específicos do projeto, sem overhead de interface web
- **[DA-005]**: OpenAI como provedor padrão de LLM - Justificativa: Maturidade, estabilidade e qualidade comprovada. Gemini mantido como alternativa opcional
- **[DA-006]**: PostgreSQL local via Docker Compose - Justificativa: Ambiente consistente e reproduzível, facilita setup e distribuição do projeto
- **[DA-007]**: Índice vetorial padrão do pgVector - Justificativa: LangChain gerencia automaticamente otimizações, reduz complexidade de configuração manual
- **[DA-008]**: pip como gerenciador de dependências - Justificativa: Simplicidade, compatibilidade universal com Python, amplamente suportado e documentado. Uso de requirements.txt como padrão da comunidade

### 3.3 Padrões e Convenções

#### Código
- **Estilo**: PEP 8 - Guia oficial de estilo Python
- **Princípios**: Pythonic - Convenções idiomáticas da comunidade Python
- **Nomenclatura**: snake_case para funções e variáveis, PascalCase para classes
- **Organização**: Módulos separados por responsabilidade (ingest, search, chat)
- **Estrutura de diretórios**:
  ```
  ├── .env                    # Variáveis de ambiente (não versionado)
  ├── .env.example            # Template de variáveis de ambiente
  ├── requirements.txt        # Dependências Python
  ├── docker-compose.yaml     # Configuração Docker
  ├── document.pdf            # PDF para ingestão
  ├── README.md              # Documentação do projeto
  ├── src/                   # Código-fonte Python
  │   ├── ingest.py          # Script de ingestão
  │   ├── search.py          # Script de busca
  │   └── chat.py            # CLI interativo
  ```

#### Dados
- **Chunking**: 1000 caracteres por chunk, 150 caracteres de overlap
- **Vetorização**: Dimensões conforme modelo escolhido (text-embedding-3-small ou embedding-001)
- **Armazenamento**: PostgreSQL com extensão pgVector

#### APIs
- **OpenAI**: REST API com autenticação via API Key
- **Google Gemini**: REST API com autenticação via API Key
- **Configuração**: Variáveis de ambiente via arquivo `.env`

### 3.4 Integrações
- **OpenAI API**: Geração de embeddings e respostas LLM (provedor padrão) - Protocolo: HTTPS/REST - Dependência: API Key válida configurada em `.env`
- **Google Gemini API**: Alternativa para embeddings e LLM - Protocolo: HTTPS/REST - Dependência: API Key válida (opcional)
- **PostgreSQL**: Persistência de dados - Protocolo: PostgreSQL Wire Protocol - Dependência: Container Docker rodando
  - **Driver**: psycopg 3.2.11 (com psycopg-binary e psycopg-pool)
  - **Host**: localhost
  - **Porta**: 5432 (porta padrão PostgreSQL)
  - **Usuário**: postgres
  - **Senha**: postgres
  - **Database**: rag
  - **Connection string**: `postgresql+psycopg://postgres:postgres@localhost:5432/rag`

## 4. Requisitos Funcionais e Técnicos

### 4.1 Casos de Uso Principais

**[UC-001] Ingerir Documento PDF**
- **Descrição**: Processar documento PDF e armazená-lo como embeddings no banco vetorial
- **Atores**: Usuário técnico
- **Pré-condições**: 
  - Banco de dados PostgreSQL rodando
  - Arquivo PDF disponível no diretório do projeto
  - API Key configurada
- **Fluxo básico**:
  1. Usuário executa `python src/ingest.py`
  2. Sistema carrega documento PDF usando PyPDFLoader
  3. Sistema divide documento em chunks de 1000 caracteres com overlap de 150
  4. Sistema gera embeddings para cada chunk
  5. Sistema armazena chunks e embeddings no PGVector
  6. Sistema confirma sucesso da ingestão
- **Pós-condições**: Documento processado e disponível para consultas

**[UC-002] Realizar Consulta Semântica**
- **Descrição**: Fazer pergunta em linguagem natural e receber resposta baseada no conteúdo ingerido
- **Atores**: Usuário final
- **Pré-condições**:
  - Banco de dados com documentos ingeridos
  - API Key configurada
- **Fluxo básico**:
  1. Usuário executa `python src/chat.py`
  2. Sistema exibe prompt "Faça sua pergunta:"
  3. Usuário digita pergunta
  4. Sistema vetoriza a pergunta
  5. Sistema busca 10 chunks mais similares usando similarity_search_with_score
  6. Sistema monta prompt com contexto recuperado
  7. Sistema envia para LLM (gpt-5-nano ou gemini-2.5-flash-lite)
  8. Sistema recebe e exibe resposta
  9. Fluxo retorna ao passo 2
- **Fluxo alternativo - Pergunta fora do contexto**:
  - No passo 7, se LLM identificar que não há informação suficiente
  - Sistema retorna: "Não tenho informações necessárias para responder sua pergunta."
- **Pós-condições**: Usuário recebe resposta contextualizada ou mensagem de falta de informação

**[UC-003] Validar Resposta Baseada em Contexto**
- **Descrição**: Garantir que respostas sejam baseadas apenas no contexto recuperado
- **Atores**: Sistema (automático)
- **Fluxo básico**:
  1. Sistema recupera chunks relevantes
  2. Sistema monta prompt com regras estritas de contexto
  3. Sistema inclui exemplos de perguntas fora do contexto
  4. Sistema instrui LLM a responder apenas com base no contexto fornecido
  5. Sistema valida que resposta não contém conhecimento externo

### 4.2 Requisitos Não-Funcionais

- **Segurança**: 
  - API Keys armazenadas em variáveis de ambiente, nunca em código
  - Arquivo `.env.example` fornecido como template (sem chaves reais)
  - Conexão com banco de dados via credenciais seguras
  
- **Escalabilidade**: 
  - Suporte para múltiplos documentos no banco vetorial
  - Arquitetura preparada para adicionar novos PDFs sem reprocessar existentes
  
- **Disponibilidade**: 
  - Sistema deve funcionar offline após ingestão (exceto chamadas à API de LLM)
  - Banco de dados deve ser persistente via volumes Docker
  
- **Manutenibilidade**: 
  - Código modular com separação clara de responsabilidades
  - Seguir padrões Pythonic e PEP 8
  - Documentação clara no README sobre execução e configuração

- **Usabilidade**:
  - CLI intuitivo com prompts claros
  - Mensagens de erro descritivas
  - Exemplos de uso no README

- **Testabilidade**:
  - Testes de integração para os cenários apresentados no projeto
  - Cobertura de casos de uso críticos (ingestão, busca semântica, validação de contexto)
  - Validação de respostas dentro e fora do contexto

## 5. Modelo de Dados

### 5.1 Entidades e Relacionamentos

**Estrutura no PGVector** (gerenciada pelo LangChain):
```
Tabela: langchain_pg_embedding (ou nome customizado)
- id: UUID (PK)
- document: TEXT (conteúdo do chunk)
- embedding: VECTOR (dimensões conforme modelo)
- metadata: JSONB (informações adicionais do documento)
  - source: caminho do arquivo PDF
  - page: número da página
  - chunk_index: índice do chunk
```

**Relacionamentos**:
- Cada documento PDF pode ter N chunks
- Cada chunk tem exatamente 1 embedding
- Embeddings são indexados para busca por similaridade (HNSW ou IVFFlat)

### 5.2 Estratégia de Persistência
- **Banco primário**: PostgreSQL 17 com extensão pgVector
- **Host**: localhost via Docker Compose
- **Porta**: 5432
- **Database**: rag
- **Credenciais**: postgres/postgres
- **Tipo de índice**: Padrão do pgVector para LangChain (gerenciado automaticamente)
  - LangChain utiliza configuração otimizada do pgVector
  - Índice vetorial para busca por similaridade (cosine similarity)
- **Persistência**: Volumes Docker para garantir dados persistentes
- **Backup**: Responsabilidade do administrador do banco (não implementado no escopo inicial)

## 6. Segurança

### 6.1 Autenticação e Autorização
- **API Keys**: Armazenadas em arquivo `.env` (não versionado)
- **Acesso ao banco**: Credenciais configuradas no docker-compose.yml
- **Escopo**: Sistema monousuário sem controle de acesso (ambiente de desenvolvimento)

### 6.2 Proteção de Dados
- **API Keys**: Nunca commitadas no repositório
- **Template**: `.env.example` fornecido sem valores reais
- **Dados sensíveis**: PDFs podem conter informações corporativas - responsabilidade do usuário

### 6.3 Segurança de API
- **Rate limiting**: Gerenciado pelos provedores (OpenAI/Google)
- **Validação de entrada**: Pydantic para validação de configurações
- **Proteção contra injection**: LangChain gerencia sanitização de prompts

## 7. Ambiente e Deploy

### 7.1 Ambientes
- **Desenvolvimento**: 
  - Python 3.13.9 local
  - PostgreSQL via Docker Compose
  - API Keys de desenvolvimento
  - Documentos de teste

- **Produção**: Não aplicável (escopo inicial é ambiente local/desenvolvimento)

### 7.2 Pipeline CI/CD
- **Escopo inicial**: Não implementado
- **Recomendação futura**: GitHub Actions para testes automatizados

### 7.3 Monitoramento e Observabilidade
- **Logs**: Saída padrão do Python (stdout/stderr)
- **Métricas**: Não implementadas no escopo inicial
- **Alertas**: Não implementados no escopo inicial
- **Ferramentas**: Logs básicos do console para debugging

## 8. Dependências e Restrições

### 8.1 Dependências Externas
- **OpenAI API**: Crítica - Provedor padrão para embeddings (text-embedding-3-small) e LLM (gpt-5-nano)
- **Google Gemini API**: Opcional - Alternativa à OpenAI (não prioritária)
- **Docker**: Crítica - Necessário para executar PostgreSQL
- **PostgreSQL com pgVector**: Crítica - Banco de dados vetorial (localhost:5432, database: rag)

### 8.2 Restrições Técnicas
- **Python 3.13.9**: Versão específica obrigatória
- **Formato de arquivo**: Apenas PDFs são suportados
- **Chunking fixo**: 1000 caracteres com overlap de 150 (não configurável)
- **Top-k fixo**: Sempre retorna 10 resultados (k=10)
- **Modelos específicos**: 
  - **OpenAI (padrão)**: text-embedding-3-small e gpt-5-nano
  - Gemini (alternativa): embedding-001 e gemini-2.5-flash-lite

### 8.3 Restrições de Negócio
- **Contexto restrito**: Respostas apenas baseadas no conteúdo ingerido
- **Sem alucinações**: Proibido inventar informações não presentes no contexto
- **Formato de resposta padrão**: Mensagem específica quando informação não disponível
- **CLI apenas**: Sem interface gráfica no escopo

## 9. Decisões Tomadas

### 9.1 Decisões Arquiteturais e Técnicas
- **[Conexão com banco]**: ✅ **DEFINIDO**
  - Host: localhost (via Docker Compose)
  - Porta: 5432 (padrão PostgreSQL)
  - Usuário: postgres
  - Senha: postgres
  - Database: rag
  - Connection string: `postgresql://postgres:postgres@localhost:5432/rag`
  
- **[Tratamento de erros]**: ✅ **DEFINIDO**
  - Estratégia: Testes de integração para os cenários apresentados no projeto
  - Cobertura: Casos de uso críticos (ingestão, busca, validação de contexto)
  - Abordagem: Validação de respostas dentro e fora do contexto
  
- **[Configurações de índice vetorial]**: ✅ **DEFINIDO**
  - Utilizar configuração padrão do pgVector para LangChain
  - LangChain gerencia automaticamente a criação e otimização do índice
  - Tipo: Índice vetorial otimizado para busca por similaridade (cosine)
  
- **[Provedor de LLM padrão]**: ✅ **DEFINIDO**
  - Provedor: **OpenAI** (padrão)
  - Modelo de embeddings: text-embedding-3-small
  - Modelo de LLM: gpt-5-nano
  - Alternativa: Google Gemini (opcional, não prioritário)

- **[Estrutura de diretórios]**: ✅ **DEFINIDO**
  - Arquivos de configuração na raiz: `.env`, `.env.example`, `requirements.txt`, `docker-compose.yaml`, `README.md`
  - Código Python na pasta `src/`: `ingest.py`, `search.py`, `chat.py`
  - Documento PDF na raiz: `document.pdf`
  - Estrutura completa documentada na seção 3.3

- **[Gerenciamento de dependências]**: ✅ **DEFINIDO**
  - Ferramenta escolhida: **pip** (gerenciador padrão Python)
  - Arquivo de dependências: `requirements.txt` na raiz do projeto
  - Justificativa: Simplicidade, compatibilidade universal, amplamente suportado

## 10. Próximos Passos

### 10.1 Prioridades Imediatas
1. Criar estrutura de diretórios do projeto (raiz + pasta src/)
2. Criar arquivo `requirements.txt` com todas as dependências
3. Configurar ambiente Python 3.13.9 e instalar dependências via pip
4. Criar e configurar arquivo `.env` com API Keys (baseado em `.env.example`)
5. Subir container PostgreSQL com pgVector via docker-compose
6. Implementar `src/ingest.py` com PyPDFLoader e chunking
7. Implementar `src/search.py` com PGVector e similarity_search
8. Implementar `src/chat.py` com interface CLI usando Typer
9. Documentar processo de execução no README.md
10. Testar fluxo completo com documento de exemplo

### 10.2 Roadmap Técnico
- **Fase 1 - Setup e Ingestão**:
  - Configuração do ambiente e dependências
  - Implementação do script de ingestão
  - Validação de armazenamento no PGVector
  
- **Fase 2 - Busca e Consulta**:
  - Implementação da busca semântica
  - Integração com LLM para geração de respostas
  - Validação de respostas contextualizadas
  
- **Fase 3 - Interface e Testes**:
  - Implementação do CLI interativo
  - Testes de cobertura conforme cenários definidos
  - Documentação completa e exemplos

- **Fase 4 - Melhorias Futuras** (fora do escopo inicial):
  - Suporte a múltiplos formatos de documento
  - Interface web
  - Histórico de conversações
  - Métricas e observabilidade

## 11. Referências

### 11.1 Fontes de Informação
- **projeto.md**: Requisitos de negócio, objetivos, casos de uso, regras de validação, exemplos de interação
- **stack.md** (v1.0): Stack tecnológico inicial, versões de bibliotecas, modelos de LLM, padrões de desenvolvimento, requisitos de testes
- **stack.md** (v1.1 - 20/10/2025): Adição de bibliotecas psycopg para conexão com PostgreSQL

### 11.2 Documentação Relacionada
- **LangChain Documentation**: https://python.langchain.com/docs/
- **pgVector Documentation**: https://github.com/pgvector/pgvector
- **OpenAI API Reference**: https://platform.openai.com/docs/
- **Google Gemini API**: https://ai.google.dev/docs
- **Typer Documentation**: https://typer.tiangolo.com/
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/

---
**Versão**: 1.3  
**Última Atualização**: 20 de outubro de 2025  
**Responsável**: Equipe de Desenvolvimento

---

## Histórico de Versões

### v1.3 - 20/10/2025
**Atualizações**:
- ✅ Definida estrutura completa de diretórios do projeto
  - Arquivos de configuração na raiz (.env, requirements.txt, etc)
  - Código Python na pasta src/
- ✅ Definido gerenciador de dependências: **pip** (ao invés de UV)
- ✅ Atualizada seção 3.3 (Padrões e Convenções) com estrutura completa
- ✅ Atualizada seção 3.1 (Ferramentas e Serviços) com pip
- ✅ Reorganizada seção 9: todas pendências resolvidas
- ✅ Atualizada seção 10.1 (Prioridades Imediatas) com novos passos

### v1.2 - 20/10/2025
**Atualizações**:
- ✅ Adicionadas bibliotecas psycopg para conexão com PostgreSQL
  - psycopg 3.2.11 (driver principal)
  - psycopg-binary 3.2.11 (versão binária)
  - psycopg-pool 3.2.6 (pool de conexões)
- ✅ Atualizada seção 3.1 (Stack Tecnológico - Backend)
- ✅ Atualizada seção 3.4 (Integrações) com detalhes do driver

### v1.1 - 20/10/2025
**Atualizações**:
- ✅ Definida configuração de conexão PostgreSQL (localhost:5432, database: rag, user/pass: postgres)
- ✅ Definida estratégia de tratamento de erros (testes de integração para cenários do projeto)
- ✅ Definidas configurações de índice vetorial (padrão pgVector para LangChain)
- ✅ Definido provedor padrão de LLM (OpenAI como principal)
- ✅ Adicionada seção de testabilidade nos requisitos não-funcionais
- ✅ Atualizada seção de dependências externas com priorização OpenAI
- ✅ Consolidadas decisões tomadas na seção 9.3

### v1.0 - 20/10/2025
**Criação inicial**:
- Documento base gerado a partir de projeto.md e stack.md
- Todas as seções principais documentadas
- Requisitos de negócio e técnicos mapeados
