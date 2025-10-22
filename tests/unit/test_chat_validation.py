"""
Testes unitários críticos para validação de chat.

Valida estrutura de prompts e regras de sistema.
"""
from src.chat import build_prompt, SYSTEM_PROMPT


def test_system_prompt_contains_rules():
    """
    Valida que SYSTEM_PROMPT contém regras críticas de negócio.
    
    Regras obrigatórias:
    - RN-001: Respostas baseadas EXCLUSIVAMENTE no contexto
    - RN-002: Mensagem padrão quando sem informação
    - RN-003: Nunca inventar informações
    - RN-004: Não produzir opiniões
    """
    required_elements = [
        "EXCLUSIVAMENTE",
        "contexto fornecido",
        "Não tenho informações necessárias",
        "NUNCA",
        "invente",
    ]
    
    for element in required_elements:
        assert element in SYSTEM_PROMPT, f"Falta elemento obrigatório: {element}"


def test_build_prompt_structure():
    """
    Valida estrutura do prompt construído.
    
    Expected: Prompt contém CONTEXTO e PERGUNTA claramente demarcados
    """
    context = "Contexto de teste com informações relevantes."
    question = "Pergunta de teste?"
    
    prompt = build_prompt(context, question)
    
    # Validar elementos estruturais
    assert "CONTEXTO:" in prompt
    assert context in prompt
    assert "PERGUNTA DO USUÁRIO:" in prompt
    assert question in prompt


def test_build_prompt_preserves_content():
    """
    Valida que prompt preserva conteúdo exato do contexto e pergunta.
    
    Expected: Sem alterações no texto fornecido
    """
    context = "Faturamento: R$ 10 milhões\nCrescimento: 25%"
    question = "Qual o faturamento?"
    
    prompt = build_prompt(context, question)
    
    # Conteúdo deve estar intacto
    assert "R$ 10 milhões" in prompt
    assert "25%" in prompt
    assert "Qual o faturamento?" in prompt


def test_build_prompt_handles_empty_context():
    """
    Valida construção de prompt com contexto vazio.
    
    Expected: Prompt válido mesmo sem contexto
    """
    context = ""
    question = "Pergunta sem contexto?"
    
    prompt = build_prompt(context, question)
    
    # Estrutura deve existir
    assert "CONTEXTO:" in prompt
    assert "PERGUNTA DO USUÁRIO:" in prompt
    assert question in prompt
