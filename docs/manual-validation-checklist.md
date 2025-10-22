# Checklist de Validação Manual

## 1. Validação de Ingestão

### Teste 1.1: Ingerir PDF válido
- [ ] Executar: `python src/ingest.py tests/fixtures/test_document.pdf`
- [ ] Verificar: Mensagem de sucesso
- [ ] Verificar: Logs mostram número de chunks
- [ ] Verificar: Tempo de processamento razoável

### Teste 1.2: Ingerir PDF inválido
- [ ] Executar: `python src/ingest.py arquivo_inexistente.pdf`
- [ ] Verificar: Mensagem de erro clara
- [ ] Verificar: Sistema não quebra

### Teste 1.3: Verificar chunks no banco
- [ ] Conectar ao PostgreSQL
- [ ] Query: `SELECT COUNT(*) FROM langchain_pg_embedding;`
- [ ] Verificar: Número de embeddings > 0

## 2. Validação de Busca

### Teste 2.1: Busca com resultados
- [ ] Executar busca por termo que existe no documento
- [ ] Verificar: Retorna k=10 ou menos resultados
- [ ] Verificar: Resultados relevantes

### Teste 2.2: Busca sem resultados
- [ ] Executar busca em coleção vazia
- [ ] Verificar: Retorna lista vazia
- [ ] Verificar: Sem erros

## 3. Validação de Chat (CT-001)

### Teste 3.1: Pergunta DENTRO do contexto
```
Pergunta: "Qual foi o faturamento da SuperTechIABrazil?"
Resposta esperada: "10 milhões de reais" ou similar
```

- [ ] Executar: `python src/chat.py`
- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta contém informação correta
- [ ] Verificar: Resposta NÃO é mensagem padrão

### Teste 3.2: Pergunta FORA do contexto (CT-002)
```
Pergunta: "Qual é a capital da França?"
Resposta esperada: "Não tenho informações necessárias para responder sua pergunta."
```

- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta é exatamente a mensagem padrão
- [ ] Verificar: LLM não inventou resposta

### Teste 3.3: Informação parcial (CT-003)
```
Pergunta: "Quantos funcionários internacionais a empresa tem?"
Resposta esperada: Admissão de limitação ou resposta parcial
```

- [ ] Fazer pergunta acima
- [ ] Verificar: Resposta é coerente
- [ ] Verificar: Se informação não existe, admite limitação

### Teste 3.4: Comandos de saída
```
Comando: quit / exit / sair
```

- [ ] Testar comando "quit"
- [ ] Testar comando "exit"
- [ ] Testar comando "sair"
- [ ] Verificar: Chat encerra gracefully

## 4. Validação de Regras de Negócio

### RN-001: Respostas baseadas no contexto
- [ ] Fazer 5 perguntas dentro do contexto
- [ ] Verificar: Todas as respostas baseadas em documentos
- [ ] Fazer 5 perguntas fora do contexto
- [ ] Verificar: Todas retornam mensagem padrão

### RN-003: Chunk size
- [ ] Query: `SELECT LENGTH(document) FROM langchain_pg_embedding;`
- [ ] Verificar: Todos os chunks <= 1500 caracteres

### RN-006: Top K=10
- [ ] Fazer busca qualquer
- [ ] Verificar código: `k=10` fixo
- [ ] Verificar resultado: máximo 10 itens

## 5. Validação de Performance

### Teste 5.1: Tempo de ingestão
- [ ] Ingerir PDF de ~10 páginas
- [ ] Verificar: Tempo < 60 segundos

### Teste 5.2: Tempo de busca
- [ ] Fazer busca semântica
- [ ] Verificar: Tempo < 5 segundos

### Teste 5.3: Tempo de resposta
- [ ] Fazer pergunta completa (busca + LLM)
- [ ] Verificar: Tempo < 15 segundos

## 6. Validação de Tratamento de Erros

### Teste 6.1: OpenAI API Key inválida
- [ ] Temporariamente invalidar key
- [ ] Tentar fazer pergunta
- [ ] Verificar: Erro claro e descritivo

### Teste 6.2: PostgreSQL desconectado
- [ ] Parar container do PostgreSQL
- [ ] Tentar ingerir documento
- [ ] Verificar: Erro de conexão claro

### Teste 6.3: Pergunta vazia
- [ ] Submeter pergunta vazia no chat
- [ ] Verificar: Tratamento adequado

## 7. Validação de Cobertura

### Análise do Relatório HTML
- [ ] Abrir `htmlcov/index.html`
- [ ] Verificar: Cobertura total >= 80%
- [ ] Verificar: `src/ingest.py` >= 80%
- [ ] Verificar: `src/search.py` >= 80%
- [ ] Verificar: `src/chat.py` >= 80%
- [ ] Identificar: Linhas não cobertas
- [ ] Avaliar: Necessidade de testes adicionais

## Assinatura

**Testado por**: _________________  
**Data**: _________________  
**Resultado**: [ ] Aprovado [ ] Reprovado  
**Observações**: 

---

## Interpretando Relatório de Cobertura

O relatório HTML (`htmlcov/index.html`) mostra:
- **Verde**: Linhas executadas (cobertas)
- **Vermelho**: Linhas não executadas (não cobertas)
- **Amarelo**: Linhas parcialmente executadas (branches)

## Ações Corretivas

**Se cobertura < 80%**:
1. Identificar módulos com baixa cobertura
2. Adicionar testes específicos para linhas não cobertas
3. Re-executar validação

**Se testes falharem**:
1. Revisar logs de erro
2. Ajustar implementação ou teste
3. Re-executar teste específico: `pytest path/to/test.py::test_name -v`

## Validação Manual Obrigatória

Mesmo com 80%+ de cobertura automatizada, execute validação manual:
1. Chat interativo (CT-001, CT-002, CT-003)
2. Tratamento de erros
3. Usabilidade da CLI
