# Tarefas do Projeto - Sistema de Ingestão e Busca Semântica

## Resumo Executivo
- **Total de tarefas**: 10
- **Grupos**: 3 fases
- **Estimativa total**: 2 sprints (10 dias úteis)
- **Duração por tarefa**: 1 dia

## Agrupamento e Ordenação

### Fase 1: Setup e Fundação (3 dias)
**Objetivo**: Preparar ambiente completo de desenvolvimento e infraestrutura  
**Entregas**: Ambiente funcional com Docker, Python configurado, estrutura de projeto criada e documentada

#### Sprint 1 - Grupo 1: Infraestrutura Base (Dias 1-3)
- **Tarefa 001**: Configurar Docker Compose e PostgreSQL com pgVector
- **Tarefa 002**: Criar estrutura de diretórios e arquivos de configuração
- **Tarefa 003**: Configurar ambiente Python e dependências

**Critério de aceite da fase**: Docker rodando, banco de dados acessível, ambiente Python funcional

---

### Fase 2: Implementação Core RAG (5 dias)
**Objetivo**: Implementar funcionalidades principais de ingestão e busca semântica  
**Entregas**: Scripts funcionais para ingestão de PDF e busca vetorial com testes

#### Sprint 1 - Grupo 2: Ingestão e Persistência (Dias 4-5)
- **Tarefa 004**: Implementar módulo de ingestão de PDFs (ingest.py)
- **Tarefa 005**: Implementar módulo de busca semântica (search.py)

#### Sprint 2 - Grupo 3: Interface e Integração (Dias 6-8)
- **Tarefa 006**: Implementar CLI interativo (chat.py)
- **Tarefa 007**: Integrar componentes e implementar validação de contexto
- **Tarefa 008**: Implementar testes de integração

**Critério de aceite da fase**: Fluxo completo de ingestão → busca → resposta funcionando

---

### Fase 3: Qualidade e Documentação (2 dias)
**Objetivo**: Garantir qualidade, testes e documentação completa  
**Entregas**: Testes validados, documentação completa, sistema pronto para uso

#### Sprint 2 - Grupo 4: Finalização (Dias 9-10)
- **Tarefa 009**: Validar cenários de teste e ajustar cobertura
- **Tarefa 010**: Documentar README e instruções de uso

**Critério de aceite da fase**: Todos os testes passando, documentação completa, sistema pronto para entrega

---

## Dependências Críticas

### Dependências Sequenciais Obrigatórias
1. **Tarefa 001** → Todas as outras (PostgreSQL precisa estar rodando)
2. **Tarefa 002** → Tarefa 003+ (estrutura de diretórios antes de código)
3. **Tarefa 003** → Tarefa 004+ (ambiente Python antes de implementação)
4. **Tarefa 004** → Tarefa 006 (ingestão antes de chat)
5. **Tarefa 005** → Tarefa 006 (busca antes de chat)
6. **Tarefa 006** → Tarefa 007 (CLI antes de integração)
7. **Tarefa 007** → Tarefa 008 (integração antes de testes)
8. **Tarefa 008** → Tarefa 009 (testes antes de validação)

### Dependências Paralelas Possíveis
- **Tarefa 004 e 005**: Podem ser desenvolvidas em paralelo após Tarefa 003
- **Tarefa 009 e 010**: Podem ter trabalho paralelo (testes + documentação)

---

## Riscos e Atenções

### Riscos Técnicos
1. **Compatibilidade Python 3.13.9**: Versão específica pode ter limitações de bibliotecas
   - Mitigação: Validar todas as dependências na Tarefa 003
   
2. **Modelo OpenAI gpt-5-nano**: Modelo pode não estar disponível publicamente
   - Mitigação: Validar acesso ao modelo na Tarefa 003, preparar fallback para gpt-5-nano

3. **Latência de embeddings**: Processamento de PDFs grandes pode ser lento
   - Mitigação: Implementar logging de progresso na Tarefa 004

4. **Qualidade de respostas**: LLM pode alucinar mesmo com contexto
   - Mitigação: Prompt engineering rigoroso na Tarefa 007

### Riscos de Negócio
1. **Contexto insuficiente**: PDFs podem não ter informação suficiente
   - Mitigação: Mensagem padrão "Não tenho informações necessárias" (RN-002)

2. **Custo de API OpenAI**: Uso frequente pode gerar custos significativos
   - Mitigação: Documentar custos estimados na Tarefa 010

### Pontos de Atenção
- ✅ **Chunking exato**: 1000 caracteres com overlap de 150 (RN-005)
- ✅ **k=10 fixo**: Sempre retornar 10 resultados (RN-006)
- ✅ **Prompt estrito**: Incluir exemplos de perguntas fora do contexto
- ✅ **Segurança**: API Keys apenas em .env, nunca em código
- ✅ **PEP 8**: Seguir rigorosamente padrões Python

---

## Estrutura de Arquivos por Tarefa

```
Tarefa 001: docker-compose.yaml
Tarefa 002: .env.example, estrutura de pastas
Tarefa 003: requirements.txt, .env
Tarefa 004: src/ingest.py
Tarefa 005: src/search.py
Tarefa 006: src/chat.py
Tarefa 007: Integração nos 3 scripts
Tarefa 008: tests/ (novos arquivos)
Tarefa 009: Validações e ajustes
Tarefa 010: README.md
```

---

## Checklist de Progresso

### Fase 1: Setup ⬜
- [ ] Tarefa 001 - Docker e PostgreSQL
- [ ] Tarefa 002 - Estrutura de diretórios
- [ ] Tarefa 003 - Ambiente Python

### Fase 2: Implementação ⬜
- [ ] Tarefa 004 - Ingestão
- [ ] Tarefa 005 - Busca
- [ ] Tarefa 006 - CLI
- [ ] Tarefa 007 - Integração
- [ ] Tarefa 008 - Testes

### Fase 3: Finalização ⬜
- [ ] Tarefa 009 - Validação
- [ ] Tarefa 010 - Documentação

---

## Notas de Execução

### Ordem Recomendada
Executar estritamente na ordem 001 → 010, respeitando dependências críticas.

### Paralelização (Opcional)
Se houver mais de um desenvolvedor:
- Dev 1: Tarefas 001-003 (setup)
- Dev 2: Preparação de testes (Tarefa 008 planejamento)
- Após Tarefa 003:
  - Dev 1: Tarefa 004 (ingestão)
  - Dev 2: Tarefa 005 (busca)

### Validação Contínua
Após cada tarefa, validar:
1. Código segue PEP 8
2. Testes passam (quando aplicável)
3. Documentação atualizada
4. Dependências satisfeitas para próxima tarefa
