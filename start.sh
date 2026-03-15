#!/bin/bash

# RAG_T3 Başlatma Betiği

echo "Sanal ortam (venv) aktif ediliyor..."
source venv/bin/activate

echo "FastAPI sunucusu başlatılıyor..."
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
