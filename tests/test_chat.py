"""Testes para módulo de chat."""
import pytest
from src.chat import build_prompt, SYSTEM_PROMPT


def test_build_prompt():
    """Testa construção do prompt."""
    context = "Contexto de teste"
    question = "Pergunta de teste"
    
    prompt = build_prompt(context, question)
    
    assert "CONTEXTO:" in prompt
    assert context in prompt
    assert "PERGUNTA DO USUÁRIO:" in prompt
    assert question in prompt
    assert "RESPONDA A \"PERGUNTA DO USUÁRIO\":" in prompt


def test_build_prompt_with_special_characters():
    """Testa construção do prompt com caracteres especiais."""
    context = "Texto com 'aspas' e \"aspas duplas\""
    question = "Pergunta com acentuação: ção, ães?"
    
    prompt = build_prompt(context, question)
    
    assert context in prompt
    assert question in prompt


def test_build_prompt_with_multiline_context():
    """Testa construção do prompt com contexto multi-linha."""
    context = """Linha 1
Linha 2
Linha 3"""
    question = "Qual informação?"
    
    prompt = build_prompt(context, question)
    
    assert "Linha 1" in prompt
    assert "Linha 2" in prompt
    assert "Linha 3" in prompt
    assert question in prompt
