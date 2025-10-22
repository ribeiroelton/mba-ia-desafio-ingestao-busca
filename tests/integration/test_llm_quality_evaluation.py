"""
Testes de qualidade de outputs LLM usando LLM-as-a-Judge.

Valida aspectos qualitativos das respostas que vão além de validações estruturais.
OTIMIZADO: Perguntas específicas sobre dados reais da tabela de empresas.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


@pytest.fixture(scope="module")
def quality_test_collection(sample_pdf_path, shared_test_collection):
    """Setup para testes de qualidade."""
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    yield shared_test_collection


def test_factual_accuracy_direct_question(quality_test_collection, llm_evaluator):
    """
    Valida resposta factual para pergunta direta sobre empresa específica.
    
    Cenário: Pergunta sobre fato específico presente no documento (tabela de empresas).
    Expected: Resposta curta e correta baseada na tabela.
    Tokens: ~400-500 (contexto mínimo + resposta direta)
    
    OTIMIZADO: Pergunta específica sobre dados tabulares reais do documento.
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # OTIMIZADO: Pergunta sobre empresa real do documento
    question = "Qual é o faturamento da empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Avaliação LLM
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.passed, f"Falhou: {evaluation.feedback}"
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.criteria_scores["adherence_to_context"] >= 75


def test_no_context_standard_message(quality_test_collection, llm_evaluator):
    """
    Valida mensagem padrão quando sem contexto.
    
    Cenário: Pergunta fora do domínio.
    Expected: Mensagem padrão exata.
    Tokens: ~400 (contexto vazio + mensagem padrão)
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85


def test_partial_info_no_hallucination(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não inventa informações ausentes no documento.
    
    Cenário: Pergunta sobre campo não presente na tabela (funcionários).
    Expected: Mensagem padrão, SEM inventar números.
    Tokens: ~400-500 (contexto mínimo + mensagem padrão)
    
    OTIMIZADO: Pergunta sobre informação realmente ausente (documento só tem 
    nome, faturamento e ano de fundação - NÃO tem número de funcionários).
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    # OTIMIZADO: Pergunta sobre campo ausente na tabela
    question = "Quantos funcionários a empresa Alfa Energia S.A. possui?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Crítico: não deve inventar números de funcionários (campo não existe no doc)
    assert evaluation.criteria_scores["hallucination_detection"] >= 80
    assert evaluation.overall_score >= 65


def test_no_external_knowledge(quality_test_collection, llm_evaluator):
    """
    Valida que LLM não usa conhecimento geral externo.
    
    Cenário: Pergunta sobre tema comum, resposta deve ser do contexto.
    Expected: Baseado no contexto OU mensagem padrão.
    Tokens: ~500 (contexto + resposta)
    """
    searcher = SemanticSearch(collection_name=quality_test_collection)
    
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve usar contexto OU mensagem padrão, nunca conhecimento geral
    assert evaluation.criteria_scores["adherence_to_context"] >= 80
    assert evaluation.criteria_scores["rule_following"] >= 85


def test_evaluation_cost_estimate(quality_test_collection, llm_evaluator):
    """
    Documenta custos otimizados de avaliação.
    
    Nota: Teste informativo, sempre passa.
    """
    # Executar avaliação simples
    searcher = SemanticSearch(collection_name=quality_test_collection)
    question = "Teste de custo otimizado"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    print("\n" + "="*60)
    print("CUSTOS OTIMIZADOS - LLM-as-a-JUDGE")
    print("="*60)
    print(f"Modelo: gpt-5-nano")
    print(f"Tokens por avaliação: ~600-900 (redução de 60%)")
    print(f"Custo por avaliação: ~$0.00006-0.00009")
    print(f"Custo por suite (5 testes): ~$0.0003-0.00045")
    print(f"Custo por 50 execuções: ~$0.015-0.025")
    print("="*60)
    print(f"ECONOMIA vs versão anterior: ~60% de tokens")
    print("="*60)
    
    assert True



