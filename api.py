"""
api.py — Async Hybrid RAG System API.
Görev takibi artık in-memory dict değil, Supabase `tasks` tablosunda tutulmaktadır.
"""

import uuid
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from query_engine import query_engine
from db import create_task, update_task, get_task

app = FastAPI(
    title="Async Hybrid RAG System",
    description="Supabase pgvector + BM25 + CrossEncoder Re-ranking destekli FastAPI. Görevler Supabase'de saklanır.",
    version="2.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Chat UI arayüzünü sunar."""
    return FileResponse("index.html")


class QueryRequest(BaseModel):
    query: str


async def process_rag_task(task_id: str, query: str):
    """
    Arka planda çalışacak fonksiyon.
    Uzun süren arama (Embedding + pgvector + BM25 + CrossEncoder) ve LLM
    işlemini API'yi bloklamadan halleder. Durum güncellemeleri Supabase'e yazılır.
    """
    try:
        update_task(task_id, status="processing")

        result = await query_engine.aquery(query)

        update_task(
            task_id,
            status="completed",
            result=result
        )

    except Exception as e:
        update_task(
            task_id,
            status="failed",
            error=str(e)
        )


@app.post("/ask")
async def ask_question(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Kullanıcıdan soruyu alır, Supabase'de bir görev kaydı oluşturur
    ve hemen bir `task_id` döner. İşlem kuyrukta (BackgroundTasks) devam eder.
    """
    task_id = str(uuid.uuid4())

    # Görevi Supabase'e kaydet
    create_task(task_id=task_id, query=request.query)

    # Arka plan işine (worker) gönder
    background_tasks.add_task(process_rag_task, task_id, request.query)

    return {
        "task_id": task_id,
        "message": "Sorgunuz kuyruğa alındı. /result/{task_id} ile kontrol edebilirsiniz."
    }


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """
    Task sonucunu Supabase'den getirir.
    State: `pending`, `processing`, `completed`, `failed`
    """
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")

    if task["status"] in ["pending", "processing"]:
        return {"task_id": task_id, "status": task["status"]}

    return task


@app.get("/health")
async def health_check():
    """Sistem durumu kontrolü."""
    return {"status": "ok", "storage": "supabase", "vector_db": "pgvector"}
