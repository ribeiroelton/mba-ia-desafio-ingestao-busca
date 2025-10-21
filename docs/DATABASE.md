# Configuração do Banco de Dados PostgreSQL com pgVector

## Visão Geral

Este projeto utiliza PostgreSQL 17 com a extensão pgVector para armazenamento de embeddings vetoriais, configurado via Docker Compose.

## Pré-requisitos

- Docker instalado e em execução
- Docker Compose instalado
- Porta 5432 disponível no host

## Arquivos de Configuração

### docker-compose.yaml

Orquestra o container PostgreSQL com pgVector:
- **Imagem**: `pgvector/pgvector:pg17`
- **Container**: `rag-postgres`
- **Porta**: 5432 (exposta em localhost)
- **Banco de dados**: `rag`
- **Credenciais**: postgres/postgres (desenvolvimento)

### init.sql

Script de inicialização que:
- Habilita a extensão pgVector automaticamente
- Valida instalação da extensão
- Registra logs de inicialização

## Comandos Úteis

### Iniciar Containers
```bash
docker-compose up -d
```

### Parar Containers
```bash
docker-compose down
```

### Ver Logs
```bash
docker-compose logs -f postgres
```

### Acessar PostgreSQL via psql
```bash
docker exec -it rag-postgres psql -U postgres -d rag
```

### Verificar Extensão pgVector
```bash
docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

### Reiniciar Container
```bash
docker-compose restart postgres
```

### Remover Tudo (incluindo volumes)
```bash
docker-compose down -v
```

## Connection String

Para conectar ao banco de dados via aplicações Python ou outras ferramentas:

```
postgresql://postgres:postgres@localhost:5432/rag
```

## Verificação de Saúde (Healthcheck)

O container PostgreSQL possui healthcheck configurado:
- **Comando**: `pg_isready -U postgres`
- **Intervalo**: 10 segundos
- **Timeout**: 5 segundos
- **Retries**: 5 tentativas

Verificar status:
```bash
docker ps | grep rag-postgres
```

Status esperado: `(healthy)`

## Troubleshooting

### Porta 5432 já em uso

**Problema**: Outro serviço PostgreSQL está usando a porta 5432

**Solução 1**: Parar PostgreSQL local
```bash
# macOS
brew services stop postgresql

# Linux
sudo service postgresql stop
```

**Solução 2**: Mudar porta no docker-compose.yaml
```yaml
ports:
  - "5433:5432"  # Expor na porta 5433 do host
```

### Container falha no healthcheck

**Diagnóstico**:
```bash
# Ver logs detalhados
docker-compose logs postgres

# Verificar se PostgreSQL está pronto
docker exec -it rag-postgres pg_isready -U postgres
```

**Solução**:
```bash
# Reiniciar container
docker-compose restart postgres

# Se persistir, recriar do zero
docker-compose down -v
docker-compose up -d
```

### Extensão pgVector não instalada

**Diagnóstico**:
```bash
# Verificar extensões disponíveis
docker exec -it rag-postgres psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

**Solução**:
```bash
# Forçar criação da extensão
docker exec -it rag-postgres psql -U postgres -d rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Permissões de Volume

**Problema**: Docker não consegue criar volumes

**Solução**: Verificar permissões do Docker e reiniciar o serviço Docker

## Segurança

⚠️ **AVISO**: Esta configuração é para **ambiente de desenvolvimento** apenas.

- **Credenciais padrão**: `postgres/postgres`
- **Porta exposta**: Apenas em localhost (não acessível externamente)
- **Sem SSL**: Conexões sem criptografia

### Recomendações para Produção

1. Usar credenciais fortes e variáveis de ambiente
2. Habilitar SSL/TLS para conexões
3. Não expor porta 5432 publicamente
4. Configurar autenticação baseada em certificados
5. Implementar backup automatizado
6. Configurar replicação para alta disponibilidade

## Estrutura de Volumes

- **postgres_data**: Armazena dados do PostgreSQL (`/var/lib/postgresql/data`)
- **pgadmin_data**: Armazena configurações do pgAdmin (se utilizado)

Volumes são persistentes e mantêm dados entre reinicializações dos containers.

## Verificação da Instalação

Execute os testes de validação:

```bash
# 1. Container rodando
docker ps | grep rag-postgres
# Esperado: Status "healthy"

# 2. Banco de dados acessível
docker exec -it rag-postgres psql -U postgres -d rag -c "\l"
# Esperado: Banco "rag" listado

# 3. Extensão pgVector instalada
docker exec -it rag-postgres psql -U postgres -d rag -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
# Esperado: vector | 0.8.x

# 4. Conexão via connection string
docker exec -it rag-postgres psql "postgresql://postgres:postgres@localhost:5432/rag" -c "SELECT version();"
# Esperado: PostgreSQL 17.x

# 5. Teste de persistência
docker exec -it rag-postgres psql -U postgres -d rag -c "CREATE TABLE test_persistence (id INT);"
docker-compose restart postgres
sleep 5
docker exec -it rag-postgres psql -U postgres -d rag -c "\dt"
# Esperado: Tabela test_persistence listada
docker exec -it rag-postgres psql -U postgres -d rag -c "DROP TABLE test_persistence;"
```

## Referências

- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [pgVector GitHub](https://github.com/pgvector/pgvector)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [pgVector Docker Image](https://hub.docker.com/r/pgvector/pgvector)
