"""
Testes de integração para regras de negócio com LLM real.

Valida comportamento end-to-end com gpt-5-nano e avaliação qualitativa.
"""
import pytest

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm, SYSTEM_PROMPT


@pytest.fixture(scope="module")
def ingested_test_doc(sample_pdf_path, shared_test_collection):
    """
    Ingere documento de teste uma vez para todos os testes do módulo.
    
    Otimiza performance evitando ingestão repetida.
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    store_in_vectorstore(chunks, shared_test_collection)
    
    yield shared_test_collection
    
    # Cleanup: Remover coleção após testes
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


def test_rn001_answer_with_context(ingested_test_doc, llm_evaluator):
    """
    RN-001: Respostas baseadas EXCLUSIVAMENTE no contexto com AVALIAÇÃO LLM.
    
    Cenário: Documento contém informação específica
    Query: Pergunta sobre informação presente no documento
    Expected: Resposta correta baseada no documento usando gpt-5-nano REAL
    
    Este teste valida que o LLM responde com base no contexto fornecido.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Buscar contexto para pergunta genérica sobre o documento
    question = "Qual é o conteúdo principal do documento?"
    context = searcher.get_context(question)
    
    # Validar que contexto foi recuperado
    assert len(context) > 0, "Contexto não recuperado"
    
    # Usar gpt-5-nano REAL para gerar resposta
    response = ask_llm(question=question, context=context)
    
    # Validações estruturais
    assert isinstance(response, str), "Resposta deve ser string"
    assert len(response) > 0, "Resposta não pode ser vazia"
    assert "Não tenho informações necessárias" not in response, \
        "Não deve retornar mensagem padrão quando há contexto"
    
    # AVALIAÇÃO QUALITATIVA
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # RN-001: Resposta deve aderir ao contexto
    assert evaluation.criteria_scores["adherence_to_context"] >= 70, \
        "Resposta deve ser baseada no contexto (RN-001)"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 70, \
        "Não deve inventar informações (RN-003)"
    
    assert evaluation.overall_score >= 70, \
        f"Resposta com contexto deve ter qualidade adequada\n{evaluation.feedback}"


def test_rn002_no_context_standard_message(ingested_test_doc, llm_evaluator):
    """
    RN-002: Mensagem padrão quando informação não disponível com AVALIAÇÃO LLM.
    
    Cenário: Pergunta completamente fora do contexto do documento
    Query: "Qual é a capital da França?" (informação não presente)
    Expected: "Não tenho informações necessárias..." usando gpt-5-nano REAL
    
    Este teste valida que o LLM segue o SYSTEM_PROMPT e não inventa informações.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Pergunta claramente fora do contexto
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    
    # Usar gpt-5-nano REAL para gerar resposta
    response = ask_llm(question=question, context=context)
    
    # Validar mensagem padrão
    assert isinstance(response, str), "Resposta deve ser string"
    assert "Não tenho informações necessárias" in response, \
        "LLM deve retornar mensagem padrão para perguntas fora do contexto"
    
    # AVALIAÇÃO QUALITATIVA
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Mensagem padrão deve ter score alto
    assert evaluation.criteria_scores["rule_following"] >= 85, \
        "Deve seguir regra RN-002 corretamente"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 90, \
        "Não deve inventar resposta quando não sabe (RN-003)"
    
    assert evaluation.overall_score >= 80, \
        f"Mensagem padrão correta deve ter score alto\n{evaluation.feedback}"


def test_rn002_no_context_with_evaluation(ingested_test_doc, llm_evaluator):
    """
    RN-002: Mensagem padrão com AVALIAÇÃO LLM.
    
    Valida qualidade da resposta quando não há contexto disponível.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    question = "Qual é a receita de bolo de chocolate?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    # Validação estrutural
    assert "Não tenho informações necessárias" in response
    
    # Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Mensagem padrão deve ter score alto
    assert evaluation.criteria_scores["rule_following"] >= 90, \
        "Deve seguir regra RN-002 perfeitamente"
    
    assert evaluation.criteria_scores["hallucination_detection"] >= 95, \
        "Não deve alucinar (RN-003)"
    
    assert evaluation.overall_score >= 85, \
        f"Mensagem padrão correta deve ter score alto\n{evaluation.feedback}"


def test_rn003_no_external_knowledge(ingested_test_doc, llm_evaluator):
    """
    RN-003: Sistema nunca deve usar conhecimento externo com AVALIAÇÃO LLM.
    
    Cenário: Pergunta sobre fato conhecido mas não presente no documento
    Expected: Mensagem padrão, não resposta com conhecimento externo
    
    Valida que LLM não usa conhecimento pré-treinado.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Pergunta sobre fato conhecido (mas não no documento)
    question = "Quem descobriu o Brasil?"
    context = searcher.get_context(question)
    
    response = ask_llm(question=question, context=context)
    
    # LLM NÃO deve responder com conhecimento externo
    assert "Não tenho informações necessárias" in response, \
        "LLM não deve usar conhecimento externo (RN-003)"
    
    # AVALIAÇÃO QUALITATIVA
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve evitar conhecimento externo
    assert evaluation.criteria_scores["adherence_to_context"] >= 80, \
        "Não deve usar conhecimento externo (RN-003)"
    
    assert evaluation.criteria_scores["rule_following"] >= 85, \
        "Deve seguir regra de não usar conhecimento externo"
    
    assert evaluation.overall_score >= 80, \
        f"Mensagem padrão para evitar conhecimento externo\n{evaluation.feedback}"


def test_rn003_no_external_knowledge_with_evaluation(ingested_test_doc, llm_evaluator):
    """
    RN-003: Sistema nunca deve usar conhecimento externo com AVALIAÇÃO LLM.
    
    Valida que LLM não usa conhecimento pré-treinado mesmo com tentação.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Pergunta sobre tema comum (tentação de usar conhecimento geral)
    question = "O que é Python?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    # Avaliação qualitativa
    evaluation = llm_evaluator.evaluate(
        question=question,
        context=context,
        response=response,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Deve evitar conhecimento externo
    assert evaluation.criteria_scores["adherence_to_context"] >= 80, \
        "Não deve usar conhecimento externo (RN-003)"
    
    assert evaluation.criteria_scores["rule_following"] >= 85, \
        "Deve seguir regra de não usar conhecimento externo"
    
    # Se não há info sobre Python no doc, deve usar mensagem padrão
    if "Não tenho informações necessárias" in response:
        assert evaluation.overall_score >= 85, \
            "Mensagem padrão correta deve ter score alto"


def test_rn006_search_returns_k10(ingested_test_doc):
    """
    RN-006: Busca retorna exatamente k=10 resultados.
    
    Expected: Máximo 10 chunks retornados pela busca semântica
    
    Valida configuração fixa de k=10 para consistência.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # Query genérica
    results = searcher.search("informações gerais do documento")
    
    # Validar k=10
    assert len(results) <= 10, "Busca não deve retornar mais de 10 resultados"
    assert searcher.k == 10, "k deve ser fixo em 10 (RN-006)"


def test_rn005_chunk_size_1000(sample_pdf_path):
    """
    RN-005: Chunks devem ter 1000 caracteres com overlap 150.
    
    Expected: Chunks respeitam tamanho e overlap configurados
    
    Valida regra de chunking.
    """
    docs = load_pdf(sample_pdf_path)
    chunks = split_documents(docs)
    
    # Validar que nenhum chunk excede 1000 caracteres
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000, \
            f"Chunk excede 1000 caracteres: {len(chunk.page_content)}"
    
    # Deve ter ao menos alguns chunks se documento é grande o suficiente
    assert len(chunks) > 0, "Documento deve gerar ao menos um chunk"
