"""
Testes de cenários específicos de integração.

Valida diferentes cenários de uso do sistema RAG.
"""
import os
import pytest
from pathlib import Path

from src.ingest import load_pdf, split_documents, store_in_vectorstore
from src.search import SemanticSearch
from src.chat import ask_llm


@pytest.fixture
def ingested_collection(clean_test_collection, sample_pdf_path):
    """Fixture com coleção já populada."""
    documents = load_pdf(sample_pdf_path)
    chunks = split_documents(documents)
    store_in_vectorstore(chunks, clean_test_collection)
    return clean_test_collection


@pytest.mark.integration
def test_scenario_question_with_exact_match(ingested_collection):
    """
    Cenário: Pergunta com match exato no documento.
    
    Expected: Resposta precisa com informação do documento.
    Valida: RN-001 (respostas baseadas no contexto)
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "Qual o faturamento da Alfa Energia?"
    context = searcher.get_context(question)
    
    # Validar contexto recuperado
    assert context, "Contexto não deve estar vazio"
    assert len(context) > 0, "Contexto deve ter conteúdo"
    
    # Perguntar ao LLM
    answer = ask_llm(question, context)
    
    # Validar resposta contém informação
    assert len(answer) > 0, "Resposta não deve estar vazia"
    # Resposta deve ser substantiva (não mensagem padrão de falta de info)
    # Para PDFs com dados específicos, validar presença de números/valores


@pytest.mark.integration
def test_scenario_question_with_partial_match(ingested_collection):
    """
    Cenário: Pergunta com match parcial.
    
    Expected: Resposta com informação disponível ou admissão de limitação.
    Valida: RN-001, RN-002
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "Quantos funcionários internacionais a empresa tem?"
    context = searcher.get_context(question)
    answer = ask_llm(question, context)
    
    # Resposta deve ser coerente
    assert len(answer) > 0, "Resposta não deve estar vazia"
    assert isinstance(answer, str), "Resposta deve ser string"


@pytest.mark.integration
def test_scenario_question_completely_unrelated(ingested_collection):
    """
    Cenário: Pergunta completamente fora do contexto.
    
    Expected: Mensagem padrão de falta de informação.
    Valida: RN-002, RN-003 (não inventar informações)
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    # Pergunta sobre algo que não pode estar no documento
    question = "Qual é a fórmula química da água?"
    context = searcher.get_context(question)
    answer = ask_llm(question, context)
    
    # Deve retornar mensagem padrão
    assert "não tenho informações" in answer.lower() or \
           "não há informações" in answer.lower() or \
           "não possuo informações" in answer.lower(), \
           "Deve retornar mensagem padrão para pergunta fora do contexto"


@pytest.mark.integration
def test_scenario_empty_question(ingested_collection):
    """
    Cenário: Pergunta vazia.
    
    Expected: Tratamento adequado (erro ou resposta padrão).
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    # Deve levantar ValueError
    with pytest.raises(ValueError, match="Query não pode ser vazia"):
        searcher.get_context("")


@pytest.mark.integration
def test_scenario_multiple_relevant_chunks(ingested_collection):
    """
    Cenário: Pergunta que requer múltiplos chunks.
    
    Expected: Contexto agregado de múltiplos chunks (até k=10).
    Valida: RN-006 (k=10)
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "Me fale sobre a empresa"
    results = searcher.search(question)
    
    # Deve retornar múltiplos chunks
    assert len(results) > 0, "Deve retornar ao menos 1 chunk"
    assert len(results) <= 10, f"Deve retornar no máximo 10 chunks (RN-006), retornou {len(results)}"
    
    # Contexto deve agregar os chunks
    context = searcher.get_context(question)
    assert "[Chunk 1]" in context, "Contexto deve incluir marcador de chunks"


@pytest.mark.integration
def test_scenario_search_consistency(ingested_collection):
    """
    Cenário: Mesma busca deve retornar resultados consistentes.
    
    Expected: Resultados idênticos em múltiplas buscas.
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "empresa"
    
    # Executar busca múltiplas vezes
    results1 = searcher.search(question)
    results2 = searcher.search(question)
    results3 = searcher.search(question)
    
    # Validar consistência
    assert len(results1) == len(results2) == len(results3), \
        "Mesmo número de resultados"
    
    # Validar que os documentos são os mesmos
    contents1 = [doc.page_content for doc, _ in results1]
    contents2 = [doc.page_content for doc, _ in results2]
    contents3 = [doc.page_content for doc, _ in results3]
    
    assert contents1 == contents2 == contents3, \
        "Mesmos documentos retornados"


@pytest.mark.integration
def test_scenario_context_format_validation(ingested_collection):
    """
    Cenário: Validar formato do contexto retornado.
    
    Expected: Contexto formatado com marcadores [Chunk X].
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "informação"
    context = searcher.get_context(question)
    
    if context:  # Se houver resultados
        # Validar formato
        assert "[Chunk 1]" in context, "Deve ter marcador de primeiro chunk"
        
        # Contar chunks no contexto
        chunk_count = context.count("[Chunk")
        assert chunk_count <= 10, f"Não deve ter mais que 10 chunks, encontrado {chunk_count}"
        assert chunk_count > 0, "Deve ter ao menos 1 chunk"


@pytest.mark.integration
def test_scenario_llm_response_format(ingested_collection):
    """
    Cenário: Validar formato da resposta do LLM.
    
    Expected: Resposta em texto, não vazia, coerente.
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    question = "Qual informação está disponível?"
    context = searcher.get_context(question)
    answer = ask_llm(question, context)
    
    # Validar formato
    assert isinstance(answer, str), "Resposta deve ser string"
    assert len(answer) > 0, "Resposta não deve estar vazia"
    assert len(answer) < 10000, "Resposta não deve ser excessivamente longa"


@pytest.mark.integration
def test_scenario_special_characters_handling(ingested_collection):
    """
    Cenário: Busca e resposta com caracteres especiais.
    
    Expected: Sistema lida corretamente com caracteres especiais.
    """
    searcher = SemanticSearch(collection_name=ingested_collection)
    
    # Perguntas com caracteres especiais
    questions = [
        "Qual o valor em R$?",
        "Crescimento de 25%?",
        "Nome da empresa (razão social)?",
    ]
    
    for question in questions:
        context = searcher.get_context(question)
        answer = ask_llm(question, context)
        
        # Deve processar sem erro
        assert isinstance(answer, str)
        assert len(answer) > 0


@pytest.mark.integration
@pytest.mark.slow
def test_scenario_large_document_ingestion(clean_test_collection):
    """
    Cenário: Ingestão de documento grande.
    
    Expected: Sistema processa e divide corretamente em chunks.
    Valida: RN-005 (chunk_size=1000, overlap=150)
    """
    # Criar documento grande (simulado)
    from langchain_core.documents import Document
    
    # 20 páginas de ~2000 caracteres cada = 40k caracteres
    large_text = "A" * 40000
    large_doc = [Document(page_content=large_text)]
    
    # Split
    chunks = split_documents(large_doc)
    
    # Validar chunks
    assert len(chunks) > 30, "Documento grande deve gerar muitos chunks"
    
    # Validar tamanho dos chunks (RN-005)
    for chunk in chunks:
        assert len(chunk.page_content) <= 1000, \
            f"Chunk com {len(chunk.page_content)} caracteres excede limite de 1000"
    
    # Armazenar
    store_in_vectorstore(chunks, collection_name=clean_test_collection)
    
    # Buscar
    searcher = SemanticSearch(collection_name=clean_test_collection)
    results = searcher.search("teste")
    
    # Deve retornar até k=10
    assert len(results) <= 10, f"Deve retornar no máximo 10 chunks, retornou {len(results)}"
