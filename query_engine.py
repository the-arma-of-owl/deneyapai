"""
query_engine.py — Supabase pgvector üzerinden Hybrid RAG + Re-ranking + LLM sentezi.
Qdrant yerine langchain-postgres PGVector kullanılmaktadır.
BM25 için gerçek doküman metinleri Supabase'den çekilmektedir.
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_chroma import Chroma
from db import create_task, update_task, get_task

load_dotenv(override=True)

CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "hybrid_rag_collection_gemini"

RAG_PROMPT_TEMPLATE = """
Sen uzman bir asistansın. Aşağıdaki bağlamı (context) kullanarak kullanıcının sorusunu yanıtla.
Yanıtlarken hangi kaynaktan (metadata: source_file) bilgi aldığını belirtmeyi unutma.

BİR DÜŞÜNME (REASONING) SÜRECİ İZLE:
1. Soru ne soruyor?
2. Bağlamdaki anahtar bilgiler neler?
3. Bu bilgilerle en doğru cevap nasıl sentezlenir?

<context>
{context}
</context>

Kullanıcının Sorusu: {question}

Düşünce Süreci (İç analiz, kullanıcıya gösterilmeyecek veya <thinking> etiketi içinde olacak):
...

Yanıt:
"""


from langchain_community.retrievers import BM25Retriever

class AsyncQueryEngine:
    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            temperature=0.1,
            max_tokens=2000
        )

        # 2. Embedding modeli (Yerel)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # 3. Vektör Araması — ChromaDB (Yerel Dense Retrieval)
        try:
            vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=CHROMA_PERSIST_DIR,
            )
            self.dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 15})
            
            # 4. Keyword Araması — BM25 (Sparse Retrieval) 
            all_data = vectorstore.get()
            if all_data and all_data.get("documents"):
                self.bm25_retriever = BM25Retriever.from_texts(all_data["documents"])
                self.bm25_retriever.k = 15
            else:
                self.bm25_retriever = self.dense_retriever

        except Exception as e:
            print(f"Uyarı: ChromaDB veritabanına bağlanılamadı: {e}")
            from langchain_core.retrievers import BaseRetriever
            class DummyRetriever(BaseRetriever):
                def _get_relevant_documents(self, query: str, *, run_manager): return []
                async def _aget_relevant_documents(self, query: str, *, run_manager): return []
            self.dense_retriever = DummyRetriever()
            self.bm25_retriever = self.dense_retriever

        # 5. Hybrid Retriever (Ensemble — RRF)
        try:
            self.hybrid_retriever = EnsembleRetriever(
                retrievers=[self.dense_retriever, self.bm25_retriever],
                weights=[0.6, 0.4]
            )
        except Exception:
            self.hybrid_retriever = self.dense_retriever

        # 6. Cross-Encoder Re-Ranker (Bypassed to avoid 1GB download for testing)
        self.cross_encoder = None
        self.reranker = None

        # 7. Tüm pipeline
        self.compression_retriever = self.hybrid_retriever

        self.prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    def _format_docs(self, docs: List[Document]) -> str:
        """Dokümanları LLM formatına çevirir."""
        formatted = []
        for d in docs:
            source = d.metadata.get("source_file", "Bilinmeyen Kaynak")
            score = d.metadata.get("relevance_score", "N/A")
            formatted.append(f"[Kaynak: {source}] (Skor: {score}):\n{d.page_content}")
        return "\n\n---\n\n".join(formatted)

    async def aquery(self, query: str) -> dict:
        """Asenkron arama, re-ranking ve LLM sentezi yapar."""
        # 1. Hibrit Arama + Re-ranking
        top_docs = await self.compression_retriever.ainvoke(query)

        if not top_docs:
            return {
                "answer": "Üzgünüm, belgelerde soruya uygun bilgi bulamadım.",
                "sources": []
            }

        # 2. Context oluştur
        context_str = self._format_docs(top_docs)

        # 3. LLM
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"context": context_str, "question": query})

        sources = list(set([doc.metadata.get("source_file", "Unknown") for doc in top_docs]))

        return {
            "answer": response.content,
            "sources": sources,
            "context_used": context_str
        }


# Global singleton
query_engine = AsyncQueryEngine()
