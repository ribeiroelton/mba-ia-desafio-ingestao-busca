-- Inicialização do Banco de Dados RAG
-- Habilita a extensão pgVector para armazenamento de embeddings vetoriais

-- Criar extensão pgVector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalação da extensão
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE 'Extensão pgVector habilitada com sucesso';
    RAISE NOTICE 'Banco de dados RAG inicializado';
END $$;
