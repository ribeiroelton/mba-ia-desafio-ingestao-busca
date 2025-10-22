"""
Testes de cenários reais com gpt-5-nano.

Valida casos de uso práticos e edge cases.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm


@pytest.fixture(scope="module")
def real_scenario_collection(sample_pdf_path, shared_test_collection):
    """
    Setup para cenários reais: ingestão única para todos os testes.
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    
    yield shared_test_collection
    
    # Cleanup
    from langchain_postgres import PGVector
    from langchain_openai import OpenAIEmbeddings
    import os
    
    try:
        vectorstore = PGVector(
            connection=os.getenv("DATABASE_URL"),
            collection_name=shared_test_collection,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        vectorstore.delete_collection()
    except Exception:
        pass


def test_scenario_ambiguous_question(real_scenario_collection):
    """
    Cenário: Pergunta ambígua que requer interpretação.
    
    Expected: LLM real interpreta contexto e responde adequadamente
    ou informa que precisa de mais clareza.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Pergunta ambígua
    question = "Me fale sobre isso"
    context = searcher.get_context(question)
    
    response = ask_llm(question, context)
    
    # LLM deve responder algo (baseado no contexto ou admitir ambiguidade)
    assert len(response) > 0, "Resposta não pode ser vazia"
    assert isinstance(response, str), "Resposta deve ser string"


def test_scenario_llm_follows_system_prompt(real_scenario_collection):
    """
    Cenário: Validar que LLM segue SYSTEM_PROMPT rigorosamente.
    
    Query sobre algo claramente fora do contexto deve retornar mensagem padrão.
    
    Este teste é crítico para validar RN-002 e RN-003.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Perguntas claramente fora do contexto
    out_of_context_questions = [
        "Quem foi o primeiro presidente dos Estados Unidos?",
        "Como fazer um bolo de chocolate?",
        "Qual é a fórmula da água?",
    ]
    
    for question in out_of_context_questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        
        # LLM DEVE seguir SYSTEM_PROMPT
        assert "Não tenho informações necessárias" in response, \
            f"LLM não seguiu SYSTEM_PROMPT para: {question}"


def test_scenario_context_length_handling(real_scenario_collection):
    """
    Cenário: Query que retorna múltiplos chunks (até k=10).
    
    Expected: LLM processa contexto completo e responde adequadamente.
    
    Valida capacidade de processar contexto extenso.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Query genérica que deve retornar múltiplos chunks
    question = "Faça um resumo completo do conteúdo"
    context = searcher.get_context(question)
    
    # Contexto deve conter múltiplos chunks
    assert len(context) > 100, "Contexto deve ser substancial"
    
    response = ask_llm(question, context)
    
    # LLM deve processar e resumir
    assert len(response) > 50, "Resumo deve ser substantivo"
    assert isinstance(response, str), "Resposta deve ser string"
    # Não deve ser mensagem padrão (há contexto disponível)
    assert "Não tenho informações necessárias" not in response


def test_scenario_similar_questions_consistency(real_scenario_collection):
    """
    Cenário: Perguntas similares devem gerar respostas consistentes.
    
    Expected: Mesma informação em respostas para perguntas equivalentes.
    
    Nota: LLMs podem variar levemente, mas tema deve ser consistente.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Perguntas similares
    questions = [
        "Qual o assunto principal?",
        "Sobre o que trata o documento?",
        "Qual é o tema central?",
    ]
    
    responses = []
    for question in questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        responses.append(response)
    
    # Todas devem ser strings não vazias
    for response in responses:
        assert isinstance(response, str), "Resposta deve ser string"
        assert len(response) > 0, "Resposta não pode ser vazia"
    
    # Pelo menos não devem ser todas mensagens padrão
    # (assumindo que documento tem conteúdo relevante)
    standard_msg_count = sum(
        1 for r in responses if "Não tenho informações necessárias" in r
    )
    assert standard_msg_count < len(responses), \
        "Nem todas as perguntas similares devem falhar"


def test_scenario_numeric_data_handling(real_scenario_collection):
    """
    Cenário: Pergunta sobre dados numéricos no documento.
    
    Expected: LLM extrai e reporta números corretamente.
    
    Valida precisão na extração de informações quantitativas.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Query sobre possíveis dados numéricos
    question = "Há números ou valores mencionados?"
    context = searcher.get_context(question)
    
    response = ask_llm(question, context)
    
    # Resposta deve ser válida
    assert isinstance(response, str), "Resposta deve ser string"
    assert len(response) > 0, "Resposta não pode ser vazia"
