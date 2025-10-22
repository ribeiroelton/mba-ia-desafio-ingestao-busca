"""Testes unitários para módulo de chat."""
import os
import pytest
from unittest.mock import patch, MagicMock

from src.chat import build_prompt, ask_llm, SYSTEM_PROMPT


def test_build_prompt_format():
    """Testa formatação do prompt."""
    context = "Contexto de teste com informações."
    question = "Qual é a informação?"
    
    prompt = build_prompt(context, question)
    
    # Validar estrutura
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


def test_build_prompt_empty_context():
    """Testa construção do prompt com contexto vazio."""
    context = ""
    question = "Qual informação?"
    
    prompt = build_prompt(context, question)
    
    assert "CONTEXTO:" in prompt
    assert "PERGUNTA DO USUÁRIO:" in prompt
    assert question in prompt


def test_build_prompt_preserves_formatting():
    """Testa que prompt preserva formatação do contexto."""
    context = "Faturamento: R$ 10 milhões\nCrescimento: 25%\nFuncionários: 50"
    question = "Qual o faturamento?"
    
    prompt = build_prompt(context, question)
    
    assert "R$ 10 milhões" in prompt
    assert "25%" in prompt
    assert "Funcionários: 50" in prompt


def test_system_prompt_has_required_rules():
    """Testa que SYSTEM_PROMPT tem regras obrigatórias (RN-001 a RN-004)."""
    required_elements = [
        "REGRAS OBRIGATÓRIAS",
        "EXCLUSIVAMENTE",
        "contexto fornecido",
        "Não tenho informações necessárias",
        "NUNCA invente",
        "conhecimento externo",
        "opiniões",
    ]
    
    for element in required_elements:
        assert element in SYSTEM_PROMPT, f"Falta elemento obrigatório: {element}"


def test_system_prompt_has_examples():
    """Testa que SYSTEM_PROMPT contém exemplos."""
    assert "EXEMPLOS" in SYSTEM_PROMPT
    assert "Pergunta:" in SYSTEM_PROMPT
    assert "Resposta:" in SYSTEM_PROMPT


@patch('src.chat.ChatOpenAI')
def test_ask_llm_with_context(mock_chat):
    """Testa chamada ao LLM com contexto."""
    # Mock da resposta do LLM
    mock_response = MagicMock()
    mock_response.content = "Resposta baseada no contexto fornecido"
    mock_chat.return_value.invoke.return_value = mock_response
    
    # Chamar função
    question = "Qual o faturamento?"
    context = "O faturamento foi de 10 milhões."
    
    answer = ask_llm(question, context)
    
    # Validar
    assert answer == "Resposta baseada no contexto fornecido"
    mock_chat.return_value.invoke.assert_called_once()
    
    # Validar argumentos da chamada
    call_args = mock_chat.return_value.invoke.call_args
    messages = call_args[0][0]
    assert len(messages) == 2  # SystemMessage e HumanMessage


@patch('src.chat.ChatOpenAI')
def test_ask_llm_without_context(mock_chat):
    """Testa chamada ao LLM sem contexto relevante."""
    # Mock da resposta padrão (RN-002)
    mock_response = MagicMock()
    mock_response.content = "Não tenho informações necessárias para responder sua pergunta."
    mock_chat.return_value.invoke.return_value = mock_response
    
    # Chamar função
    question = "Qual a capital da França?"
    context = "O faturamento foi de 10 milhões."  # Contexto não relacionado
    
    answer = ask_llm(question, context)
    
    # Validar resposta padrão
    assert "não tenho informações necessárias" in answer.lower()


@patch('src.chat.ChatOpenAI')
def test_ask_llm_temperature_zero(mock_chat):
    """Testa que LLM usa temperature=0 para respostas determinísticas."""
    mock_response = MagicMock()
    mock_response.content = "Resposta"
    mock_chat.return_value.invoke.return_value = mock_response
    
    ask_llm("Pergunta", "Contexto")
    
    # Validar que ChatOpenAI foi chamado com temperature=0
    mock_chat.assert_called_once()
    call_kwargs = mock_chat.call_args[1]
    assert call_kwargs.get("temperature") == 0


@patch('src.chat.ChatOpenAI')
def test_ask_llm_uses_correct_model(mock_chat):
    """Testa que LLM usa modelo configurado."""
    mock_response = MagicMock()
    mock_response.content = "Resposta"
    mock_chat.return_value.invoke.return_value = mock_response
    
    with patch.dict(os.environ, {"LLM_MODEL": "gpt-4"}):
        ask_llm("Pergunta", "Contexto")
    
    # Validar que modelo correto foi usado
    call_kwargs = mock_chat.call_args[1]
    assert call_kwargs.get("model") == "gpt-4"


@patch('src.chat.ChatOpenAI')
def test_ask_llm_message_structure(mock_chat):
    """Testa estrutura das mensagens enviadas ao LLM."""
    mock_response = MagicMock()
    mock_response.content = "Resposta"
    mock_chat.return_value.invoke.return_value = mock_response
    
    question = "Teste"
    context = "Contexto de teste"
    
    ask_llm(question, context)
    
    # Pegar mensagens enviadas
    call_args = mock_chat.return_value.invoke.call_args
    messages = call_args[0][0]
    
    # Validar estrutura
    assert len(messages) == 2
    
    # Primeira mensagem é SystemMessage
    from langchain_core.messages import SystemMessage
    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == SYSTEM_PROMPT
    
    # Segunda mensagem é HumanMessage
    from langchain_core.messages import HumanMessage
    assert isinstance(messages[1], HumanMessage)
    assert context in messages[1].content
    assert question in messages[1].content


@patch('src.chat.ChatOpenAI')
def test_ask_llm_handles_long_context(mock_chat):
    """Testa que LLM lida com contexto longo."""
    mock_response = MagicMock()
    mock_response.content = "Resposta processada"
    mock_chat.return_value.invoke.return_value = mock_response
    
    # Criar contexto longo (10 chunks)
    long_context = "\n\n".join([f"[Chunk {i}]\n" + "A" * 800 for i in range(1, 11)])
    question = "Qual informação?"
    
    answer = ask_llm(question, long_context)
    
    assert answer == "Resposta processada"
    mock_chat.return_value.invoke.assert_called_once()


@patch('src.chat.ChatOpenAI')
def test_ask_llm_with_empty_context(mock_chat):
    """Testa comportamento com contexto vazio."""
    mock_response = MagicMock()
    mock_response.content = "Não tenho informações necessárias para responder sua pergunta."
    mock_chat.return_value.invoke.return_value = mock_response
    
    answer = ask_llm("Pergunta", "")
    
    # Deve retornar mensagem padrão
    assert "não tenho informações necessárias" in answer.lower()
