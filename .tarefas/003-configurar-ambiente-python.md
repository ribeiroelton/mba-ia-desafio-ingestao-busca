# [003] - Configurar Ambiente Python e Dependências

## Metadados
- **ID**: 003
- **Grupo**: Fase 1 - Setup e Fundação
- **Prioridade**: Alta
- **Complexidade**: Média
- **Estimativa**: 1 dia

## Descrição
Configurar ambiente Python 3.13.9, criar `requirements.txt` completo com todas as 13 dependências do stack, instalar pacotes via pip e validar que todas as bibliotecas estão funcionando corretamente.

## Requisitos

### Requisitos Funcionais
- RF-004: Ambiente Python 3.13.9 configurado
- RF-005: Todas as 13 dependências instaladas via pip

### Requisitos Não-Funcionais
- RNF-007: Usar pip como gerenciador de pacotes (DA-008)
- RNF-008: Validar compatibilidade de todas as bibliotecas

## Fonte da Informação
- **Seção 3.1**: Stack Tecnológico Backend - 13 dependências listadas
- **Seção 3.1**: Ferramentas - pip como gerenciador
- **Seção 8.2**: Restrições Técnicas - Python 3.13.9 obrigatório
- **Seção 9.1**: Decisão sobre gerenciamento de dependências (pip)

## Stack Necessária
- **Python**: 3.13.9 (versão específica)
- **Gerenciador**: pip
- **Dependências (13)**:
  - langchain==0.3.27
  - langchain_core==0.3.79
  - langchain_text_splitters==0.3.11
  - langchain_openai==0.3.35
  - langchain_google_genai==2.1.12
  - langchain_postgres==0.0.16
  - langchain-community==0.4
  - pydantic==2.12.3
  - typer==0.20.0
  - psycopg==3.2.11
  - psycopg-binary==3.2.11
  - psycopg-pool==3.2.6
  - python-dotenv==1.0.0 (para carregar .env)

## Dependências

### Dependências Técnicas
- Tarefa 001: PostgreSQL rodando
- Tarefa 002: Estrutura de diretórios criada
- Python 3.13.9 instalado no sistema

### Dependências de Negócio
- OpenAI API Key obtida (para validação)

## Critérios de Aceite

1. [x] Python 3.13.9 instalado e verificado
2. [x] Arquivo `requirements.txt` preenchido com todas as 13 dependências
3. [x] Virtual environment criado (venv)
4. [x] Todas as dependências instaladas sem erros
5. [x] Import de todas as bibliotecas validado
6. [x] Conexão com PostgreSQL testada via psycopg
7. [x] OpenAI API Key validada
8. [x] Arquivo `.env` preenchido com configurações corretas
9. [x] Comando `pip list` mostra todas as bibliotecas

## Implementação Resumida

### requirements.txt Completo
```txt
# LangChain Core
langchain==0.3.27
langchain_core==0.3.79

# LangChain Components
langchain_text_splitters==0.3.11
langchain_openai==0.3.35
langchain_google_genai==2.1.12
langchain_postgres==0.0.16
langchain-community==0.4

# Utilities
pydantic==2.12.3
typer==0.20.0

# PostgreSQL Drivers
psycopg==3.2.11
psycopg-binary==3.2.11
psycopg-pool==3.2.6

# Environment Management
python-dotenv==1.0.0
```

### Script de Validação
**Arquivo**: `validate_env.py`
```python
"""Script de validação do ambiente."""
import sys

def validate_python_version():
    """Valida versão Python 3.13.9."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    assert version.major == 3 and version.minor == 13, "Python 3.13.x obrigatório"
    return True

def validate_imports():
    """Valida imports de todas as bibliotecas."""
    imports = [
        "langchain",
        "langchain_core",
        "langchain_text_splitters",
        "langchain_openai",
        "langchain_google_genai",
        "langchain_postgres",
        "langchain_community",
        "pydantic",
        "typer",
        "psycopg",
        "psycopg_pool",
        "dotenv",
    ]
    
    for module in imports:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    return True

def validate_postgres_connection():
    """Valida conexão com PostgreSQL."""
    import psycopg
    try:
        conn = psycopg.connect(
            "postgresql://postgres:postgres@localhost:5432/rag"
        )
        conn.close()
        print("✓ PostgreSQL connection")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection: {e}")
        return False

def validate_openai_key():
    """Valida OpenAI API Key."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("✗ OPENAI_API_KEY not set in .env")
        return False
    
    if api_key.startswith("sk-proj-") or api_key.startswith("sk-"):
        print("✓ OPENAI_API_KEY format valid")
        return True
    else:
        print("✗ OPENAI_API_KEY format invalid")
        return False

if __name__ == "__main__":
    print("=== Validação de Ambiente ===\n")
    
    checks = [
        ("Python Version", validate_python_version),
        ("Imports", validate_imports),
        ("PostgreSQL", validate_postgres_connection),
        ("OpenAI Key", validate_openai_key),
    ]
    
    results = []
    for name, check in checks:
        print(f"\n{name}:")
        try:
            results.append(check())
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append(False)
    
    print("\n=== Resultado ===")
    if all(results):
        print("✅ Ambiente configurado corretamente!")
        sys.exit(0)
    else:
        print("❌ Falhas na configuração do ambiente")
        sys.exit(1)
```

## Testes de Qualidade e Cobertura

### Testes de Integração

**Cenários a Testar**:

1. **Cenário 1: Python versão correta**
   ```bash
   python --version
   # Expected: Python 3.13.9
   ```

2. **Cenário 2: Dependências instaladas**
   ```bash
   pip list | grep langchain
   # Expected: Lista com todas as libs langchain
   ```

3. **Cenário 3: Validação completa**
   ```bash
   python validate_env.py
   # Expected: Todas as validações passam
   ```

4. **Cenário 4: Conexão PostgreSQL**
   ```bash
   python -c "import psycopg; conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/rag'); print('OK')"
   # Expected: OK
   ```

5. **Cenário 5: OpenAI import**
   ```bash
   python -c "from langchain_openai import OpenAIEmbeddings; print('OK')"
   # Expected: OK
   ```

## Checklist de Finalização

- [x] Python 3.13.9 instalado
- [x] Virtual environment criado
- [x] `requirements.txt` preenchido
- [x] `pip install -r requirements.txt` executado
- [x] Todas as 13 dependências instaladas
- [x] Script `validate_env.py` criado
- [x] Validações executadas com sucesso
- [x] `.env` preenchido com OpenAI API Key real
- [x] Conexão PostgreSQL testada
- [x] Documentação de setup atualizada

## Notas Adicionais

### Comandos de Setup
```bash
# Verificar versão Python
python --version  # Deve ser 3.13.9

# Criar virtual environment
python -m venv venv

# Ativar venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Validar ambiente
python validate_env.py

# Ver dependências instaladas
pip list
```

### Troubleshooting

**Python 3.13.9 não disponível**:
```bash
# macOS (via pyenv)
pyenv install 3.13.9
pyenv local 3.13.9

# Ou via Python.org
# Baixar de https://www.python.org/downloads/
```

**Erro ao instalar psycopg-binary**:
```bash
# Instalar dependências do sistema
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install libpq-dev

# Reinstalar
pip install psycopg-binary --force-reinstall
```

**OpenAI API Key inválida**:
- Gerar nova em: https://platform.openai.com/api-keys
- Formato deve começar com `sk-proj-` ou `sk-`

## Referências
- **Python 3.13 Release**: https://www.python.org/downloads/
- **pip Documentation**: https://pip.pypa.io/
- **venv Documentation**: https://docs.python.org/3/library/venv.html
- **OpenAI API Keys**: https://platform.openai.com/api-keys
