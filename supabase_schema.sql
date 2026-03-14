-- ============================================================
-- RAG_T3 Supabase SQL Schema
-- Supabase Dashboard > SQL Editor'de bu dosyayı çalıştırın.
-- ============================================================

-- 1. pgvector extension (embedding araması için)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Görev takibi tablosu (api.py TASKS_DB yerine)
CREATE TABLE IF NOT EXISTS tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status      TEXT NOT NULL DEFAULT 'pending',  -- pending | processing | completed | failed
    query       TEXT,
    result      JSONB,
    error       TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Doküman embedding tablosu (langchain-postgres PGVector otomatik oluşturur,
--    ancak manuel olarak da aşağıdaki gibi tanımlanabilir)
--
-- NOT: langchain-postgres kendi tablolarını (langchain_pg_collection, langchain_pg_embedding)
--      otomatik oluşturur. Aşağıdaki blok yalnızca referans içindir.
--
-- CREATE TABLE IF NOT EXISTS documents (
--     id        BIGSERIAL PRIMARY KEY,
--     content   TEXT,
--     metadata  JSONB,
--     embedding VECTOR(1536)   -- text-embedding-3-small boyutu
-- );
--
-- CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 4. tasks tablosu için index
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

-- ============================================================
-- Kontrol: Tabloların oluştuğunu doğrula
-- ============================================================
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
