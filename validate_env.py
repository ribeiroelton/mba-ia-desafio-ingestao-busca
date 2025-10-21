"""Script de validação do ambiente."""
import sys


def validate_python_version() -> bool:
    """Valida versão Python 3.13.9."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    assert version.major == 3 and version.minor == 13, "Python 3.13.x obrigatório"
    return True


def validate_imports() -> bool:
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


def validate_postgres_connection() -> bool:
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


def validate_openai_key() -> bool:
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
