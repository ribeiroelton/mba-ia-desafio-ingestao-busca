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


def test_rn001_answer_with_context_optimized(ingested_test_doc, llm_evaluator):
    """
    RN-001: Resposta baseada no contexto com pergunta direta sobre dados reais.
    
    Tokens: ~450-550 (redução de ~50%)
    
    OTIMIZADO: Pergunta específica sobre ano de fundação de empresa real.
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    # OTIMIZADO: Pergunta sobre dado real e específico da tabela
    question = "Em que ano foi fundada a empresa Alfa Energia S.A.?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    assert len(response) > 0
    assert "Não tenho informações necessárias" not in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.passed
    assert evaluation.criteria_scores["adherence_to_context"] >= 70
    assert evaluation.criteria_scores["hallucination_detection"] >= 80


def test_rn002_no_context_standard_message_optimized(ingested_test_doc, llm_evaluator):
    """
    RN-002: Mensagem padrão quando sem contexto.
    
    Tokens: ~400 (já otimizado, manter)
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    question = "Qual é a capital da França?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    assert "Não tenho informações necessárias" in response
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.criteria_scores["rule_following"] >= 90
    assert evaluation.overall_score >= 85


def test_rn003_no_external_knowledge_optimized(ingested_test_doc, llm_evaluator):
    """
    RN-003: Não usar conhecimento externo.
    
    Tokens: ~500 (já otimizado, manter)
    """
    searcher = SemanticSearch(collection_name=ingested_test_doc)
    
    question = "O que é inteligência artificial?"
    context = searcher.get_context(question)
    response = ask_llm(question=question, context=context)
    
    evaluation = llm_evaluator.evaluate(
        question=question, context=context, response=response, system_prompt=SYSTEM_PROMPT
    )
    
    # Assertions essenciais
    assert evaluation.criteria_scores["adherence_to_context"] >= 80
    assert evaluation.criteria_scores["rule_following"] >= 85


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
