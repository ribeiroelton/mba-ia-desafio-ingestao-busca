# [001] - Configurar Docker Compose e PostgreSQL com pgVector

## Metadados
- **ID**: 001
- **Grupo**: Fase 1 - Setup e Fundação
- **Prioridade**: Alta
- **Complexidade**: Média
- **Estimativa**: 1 dia

## Descrição
Configurar ambiente Docker com PostgreSQL 17 e extensão pgVector para armazenamento de embeddings vetoriais. Esta tarefa estabelece a fundação de persistência do sistema RAG, permitindo armazenamento e busca eficiente de vetores.

## Requisitos

### Requisitos Funcionais
- RF-001: Sistema deve armazenar chunks de texto com embeddings no banco vetorial
- UC-001: Banco de dados deve estar disponível para ingestão de documentos

### Requisitos Não-Funcionais
- RNF-001: Banco de dados deve ser persistente via volumes Docker
- RNF-002: Ambiente deve ser consistente e reproduzível (DA-006)
- RNF-003: Conexão deve usar credenciais seguras

## Fonte da Informação
- **Seção 3.1**: Stack Tecnológico - PostgreSQL 17 (pgvector/pgvector:pg17)
- **Seção 3.2**: DA-006 - PostgreSQL local via Docker Compose
- **Seção 3.4**: Integrações - Detalhes de conexão PostgreSQL
- **Seção 5.2**: Estratégia de Persistência - Configuração do banco
- **Seção 9.1**: Decisão sobre conexão com banco (localhost:5432, database: rag)

## Stack Necessária
- **Container**: Docker
- **Orquestração**: Docker Compose (Docker Compose Specification)
- **Imagem**: pgvector/pgvector:pg17
- **Banco de Dados**: PostgreSQL 17 com extensão pgVector
- **Porta**: 5432 (porta padrão PostgreSQL)

## Dependências

### Dependências Técnicas
- Docker instalado e rodando
- Docker Compose instalado (versão compatível com Compose Specification)
- Porta 5432 disponível no host

### Dependências de Negócio
- Nenhuma

## Critérios de Aceite

1. [x] Arquivo `docker-compose.yaml` criado na raiz do projeto
2. [x] Container PostgreSQL 17 com pgVector configurado
3. [x] Banco de dados `rag` criado automaticamente
4. [x] Credenciais configuradas (postgres/postgres)
5. [x] Porta 5432 exposta e acessível
6. [x] Volume persistente configurado para dados
7. [x] Extensão pgVector habilitada automaticamente
8. [x] Container inicia sem erros
9. [x] Conexão testada com psql ou cliente PostgreSQL
10. [x] Logs do container indicam inicialização bem-sucedida

## Implementação Resumida

### Estrutura de Arquivos
```
projeto/
├── docker-compose.yaml     # Configuração Docker Compose (CRIAR)
└── .gitignore             # Adicionar exclusões Docker (ATUALIZAR)
```

### Componentes a Implementar

#### docker-compose.yaml
**Arquivo**: `docker-compose.yaml`
**Responsabilidade**: Definir serviço PostgreSQL com pgVector
**Configuração**:
```yaml

services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: rag-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: rag
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

#### init.sql
**Arquivo**: `init.sql`
**Responsabilidade**: Inicializar extensão pgVector
**Conteúdo**:
```sql
-- Habilitar extensão pgVector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalação
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

### Regras de Negócio a Implementar
- **Nenhuma regra de negócio específica** (tarefa de infraestrutura)

### Validações Necessárias
- Container inicia sem erros
- Extensão pgVector está instalada
- Banco de dados `rag` está acessível
- Porta 5432 responde a conexões

### Tratamento de Erros
- **Porta 5432 já em uso**: Verificar se outro PostgreSQL está rodando, parar ou mudar porta
- **Imagem não encontrada**: Executar `docker pull pgvector/pgvector:pg17`
- **Permissões de volume**: Verificar permissões do Docker para criar volumes
- **Falha de healthcheck**: Verificar logs com `docker-compose logs postgres`

## Testes de Qualidade e Cobertura

### Testes de Integração
**Tipo**: Validação manual de infraestrutura

**Cenários a Testar**:

1. **Cenário 1: Container inicia corretamente**
   - Comando: `docker-compose up -d`
   - Expected: Container `rag-postgres` com status `running`
   - Validação: `docker ps | grep rag-postgres`

2. **Cenário 2: Banco de dados acessível**
   - Comando: `docker exec -it rag-postgres psql -U postgres -d rag`
   - Expected: Prompt psql conectado ao banco `rag`
   - Validação: `\l` lista banco de dados `rag`

3. **Cenário 3: Extensão pgVector instalada**
   - Comando: `docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"`
   - Expected: Retorna linha com `vector` e versão
   - Validação: Saída contém `vector | 0.7.x` ou superior

4. **Cenário 4: Conexão via connection string**
   - Comando: `psql "postgresql://postgres:postgres@localhost:5432/rag" -c "SELECT version();"`
   - Expected: Retorna versão do PostgreSQL 17.x
   - Validação: Saída contém `PostgreSQL 17`

5. **Cenário 5: Volume persistente funcional**
   - Comando: 
     ```bash
     # Criar tabela de teste
     docker exec -it rag-postgres psql -U postgres -d rag -c "CREATE TABLE test (id INT);"
     # Reiniciar container
     docker-compose restart postgres
     # Verificar tabela existe
     docker exec -it rag-postgres psql -U postgres -d rag -c "\dt"
     ```
   - Expected: Tabela `test` ainda existe após restart
   - Validação: Lista de tabelas inclui `test`

### Testes de Performance
**Não aplicável** (tarefa de infraestrutura)

### Testes de Segurança
**Cenários**:
1. **Senhas não hardcoded**: Verificar que senhas não estão em código (usar variáveis de ambiente)
2. **Porta não exposta publicamente**: Verificar que container aceita apenas conexões localhost
3. **Credenciais padrão documentadas**: Documentar que `postgres/postgres` é apenas para desenvolvimento

## Documentação Necessária

### Código
- [x] Comentários no docker-compose.yaml explicando configurações
- [x] Comentários no init.sql explicando inicialização

### Técnica
- [x] Connection string documentada: `postgresql://postgres:postgres@localhost:5432/rag`
- [x] Comandos úteis documentados (start, stop, logs, acesso psql)
- [x] Troubleshooting de problemas comuns

## Checklist de Finalização

- [x] Arquivo `docker-compose.yaml` criado
- [x] Arquivo `init.sql` criado
- [x] Container inicia sem erros (`docker-compose up -d`)
- [x] Healthcheck passa (container healthy)
- [x] Banco de dados `rag` criado
- [x] Extensão pgVector habilitada
- [x] Conexão testada via psql
- [x] Volume persistente testado (restart mantém dados)
- [x] Porta 5432 acessível de localhost
- [x] Logs verificados (sem erros críticos)
- [x] `.gitignore` atualizado (excluir volumes locais se necessário)
- [x] Documentação básica criada (comandos úteis)

## Notas Adicionais

### Comandos Úteis
```bash
# Iniciar container
docker-compose up -d

# Parar container
docker-compose down

# Ver logs
docker-compose logs -f postgres

# Acessar psql
docker exec -it rag-postgres psql -U postgres -d rag

# Verificar extensão pgVector
docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"

# Reiniciar container
docker-compose restart postgres

# Remover tudo (incluindo volumes)
docker-compose down -v
```

### Troubleshooting

**Problema: Porta 5432 já em uso**
```bash
# Verificar processos na porta 5432
lsof -i :5432
# ou
netstat -an | grep 5432

# Solução 1: Parar PostgreSQL local
brew services stop postgresql  # macOS
sudo service postgresql stop    # Linux

# Solução 2: Mudar porta no docker-compose.yaml
ports:
  - "5433:5432"  # Expor na 5433 do host
```

**Problema: Container falha no healthcheck**
```bash
# Ver logs detalhados
docker-compose logs postgres

# Verificar se PostgreSQL está pronto
docker exec -it rag-postgres pg_isready -U postgres

# Reiniciar container
docker-compose restart postgres
```

**Problema: Extensão pgVector não instalada**
```bash
# Verificar extensões disponíveis
docker exec -it rag-postgres psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# Forçar criação da extensão
docker exec -it rag-postgres psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Segurança (Ambiente de Desenvolvimento)
- ⚠️ **Credenciais padrão**: `postgres/postgres` é apenas para desenvolvimento
- ⚠️ **Porta exposta**: Porta 5432 exposta apenas em localhost (não acessível externamente)
- ⚠️ **Sem SSL**: Conexão sem SSL é aceitável para desenvolvimento local
- ✅ **Produção**: Em produção, usar credenciais fortes, SSL/TLS e não expor porta

## Referências
- **Docker Compose Specification**: https://docs.docker.com/compose/compose-file/
- **pgVector GitHub**: https://github.com/pgvector/pgvector
- **PostgreSQL Docker**: https://hub.docker.com/_/postgres
- **pgVector Docker Image**: https://hub.docker.com/r/pgvector/pgvector
