"""
db.py — Supabase client ve Tasks tablosu için CRUD fonksiyonları.
TASKS_DB in-memory dict'in yerini alır.
"""

import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError(
        "SUPABASE_URL ve SUPABASE_SERVICE_KEY ortam değişkenleri tanımlı olmalıdır. "
        "Lütfen .env dosyasını kontrol edin."
    )

# Supabase client singleton
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ─────────────────────────────────────────────
# Task CRUD
# ─────────────────────────────────────────────

def create_task(task_id: str, query: str) -> Dict[str, Any]:
    """Yeni bir görev kaydı oluşturur, durumu 'pending' olarak ayarlar."""
    data = {
        "id": task_id,
        "status": "pending",
        "query": query,
        "result": None,
        "error": None,
    }
    response = supabase.table("tasks").insert(data).execute()
    return response.data[0] if response.data else data


def update_task(task_id: str, **kwargs) -> Dict[str, Any]:
    """
    Görev kaydını günceller.
    Örnek: update_task(task_id, status="completed", result={...})
    """
    response = (
        supabase.table("tasks")
        .update(kwargs)
        .eq("id", task_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Görev kaydını getirir. Bulunamazsa None döner."""
    response = (
        supabase.table("tasks")
        .select("*")
        .eq("id", task_id)
        .maybe_single()
        .execute()
    )
    return response.data
