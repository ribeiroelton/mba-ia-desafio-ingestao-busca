"""
Testes de cenários reais com gpt-5-nano.

Valida casos de uso práticos e edge cases com avaliação LLM qualitativa.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


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


def test_scenario_ambiguous_question_with_evaluation(
    real_scenario_collection,
    llm_evaluator
):
    """
    Cenário: Pergunta ambígua com AVALIAÇÃO LLM.
    
    Valida que LLM interpreta adequadamente ou admite necessidade de clareza.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Me fale sobre isso"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para pergunta ambígua, esperamos:
    # - Alta aderência ao contexto
    # - Clareza pode ser menor (pergunta é ambígua)
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        f"Mesmo com pergunta ambígua, deve aderir ao contexto"
    
    # Score geral pode ser mais baixo (clareza prejudicada)
    # mas não deve alucinar
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        f"Não deve alucinar mesmo com pergunta ambígua"


def test_scenario_llm_follows_system_prompt_with_evaluation(
    real_scenario_collection, 
    llm_evaluator
):
    """
    Cenário: Validar que LLM segue SYSTEM_PROMPT rigorosamente com AVALIAÇÃO LLM.
    
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
        
        # Validação estrutural
        assert "Não tenho informações necessárias" in response, \
            f"LLM não seguiu SYSTEM_PROMPT para: {question}"
        
        # Avaliação qualitativa
        evaluation = llm_evaluator.evaluate(
            question=question,
            context=context,
            response=response,
            system_prompt=SYSTEM_PROMPT
        )
        
        # Para perguntas fora do contexto com mensagem padrão correta:
        assert evaluation.criteria_scores["rule_following"] >= 90, \
            f"Deve seguir SYSTEM_PROMPT perfeitamente para: {question}"
        
        assert evaluation.criteria_scores["hallucination_detection"] >= 95, \
            f"Não deve alucinar para: {question}"
        
        assert evaluation.overall_score >= 85, \
            f"Mensagem padrão correta deve ter score alto para: {question}\n{evaluation.feedback}"


def test_scenario_context_length_handling_with_evaluation(
    real_scenario_collection,
    llm_evaluator
):
    """
    Cenário: Query que retorna múltiplos chunks com AVALIAÇÃO LLM.
    
    Valida capacidade de processar contexto extenso com qualidade.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Faça um resumo completo do conteúdo"
    context = searcher.get_context(question)
    
    # Contexto deve ser substancial
    assert len(context) > 100
    
    response = ask_llm(question, context)
    
    # Validação estrutural
    assert len(response) > 50
    assert "Não tenho informações necessárias" not in response
    
    # Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para resumo de contexto extenso:
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        "Resumo deve aderir ao contexto mesmo sendo extenso"
    
    assert evaluation.criteria_scores["clarity_objectivity"] >= 70, \
        "Resumo deve ser razoavelmente claro"
    
    assert evaluation.overall_score >= 70, \
        f"Resumo de contexto extenso deve passar threshold\n{evaluation.feedback}"


def test_scenario_similar_questions_consistency_with_evaluation(
    real_scenario_collection,
    llm_evaluator
):
    """
    Cenário: Perguntas similares com AVALIAÇÃO LLM.
    
    Expected: Respostas consistentes em qualidade para perguntas equivalentes.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    # Perguntas similares
    questions = [
        "Qual o assunto principal?",
        "Sobre o que trata o documento?",
        "Qual é o tema central?",
    ]
    
    evaluations = []
    for question in questions:
        context = searcher.get_context(question)
        response = ask_llm(question, context)
        
        # Validação estrutural
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Avaliação qualitativa
        evaluation = llm_evaluator.evaluate(
            question=question,
            context=context,
            response=response,
            system_prompt=SYSTEM_PROMPT
        )
        evaluations.append(evaluation)
    
    # Todas devem passar
    for i, evaluation in enumerate(evaluations):
        assert evaluation.passed, \
            f"Pergunta {i+1} falhou: {evaluation.feedback}"
    
    # Scores devem ser consistentes (variação < 20 pontos)
    scores = [e.overall_score for e in evaluations]
    score_variance = max(scores) - min(scores)
    
    assert score_variance < 20, \
        f"Scores muito inconsistentes entre perguntas similares: {scores}"


def test_scenario_numeric_data_handling_with_evaluation(
    real_scenario_collection,
    llm_evaluator
):
    """
    Cenário: Pergunta sobre dados numéricos com AVALIAÇÃO LLM.
    
    Expected: LLM extrai e reporta números corretamente, baseado no contexto.
    """
    searcher = SemanticSearch(collection_name=real_scenario_collection)
    
    question = "Há números ou valores mencionados?"
    context = searcher.get_context(question)
    response = ask_llm(question, context)
    
    # Validação estrutural
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Para extração de dados numéricos:
    assert evaluation.criteria_scores["adherence_to_context"] >= 75, \
        "Deve extrair números apenas do contexto"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 80, \
        "Não deve inventar números não presentes"
    
    assert evaluation.overall_score >= 70, \
        f"Extração de dados deve passar threshold\n{evaluation.feedback}"

