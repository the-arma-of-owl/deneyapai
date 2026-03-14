"""
ingest_pdfs.py — PDF'leri okur, chunk'lar ve Supabase pgvector'e yükler.
Qdrant yerine langchain-postgres PGVector kullanılmaktadır.
"""

import asyncio
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import time

load_dotenv(override=True)

PDF_DIR = "./pdfs"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "hybrid_rag_collection_gemini"


async def load_single_pdf(file_path: Path) -> List[Document]:
    """Tek bir PDF dosyasını asenkron olarak yükler ve metadata ekler."""
    def _load():
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_file"] = file_path.name
        return docs

    return await asyncio.to_thread(_load)


async def process_docs(documents: List[Document]) -> List[Document]:
    """Dokümanları anlamlı chunk'lara böler."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_documents(documents)


async def aingest_pdfs():
    """Tüm PDF'leri okur, parçalar ve ChromaDB'ye yükler."""
    pdf_path = Path(PDF_DIR)
    if not pdf_path.exists():
        pdf_path.mkdir(parents=True)
        print(f"Lütfen PDF'lerinizi '{PDF_DIR}' klasörüne koyun ve tekrar çalıştırın.")
        return

    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        print(f"'{PDF_DIR}' klasöründe PDF dosyası bulunamadı.")
        return

    print(f"Toplam {len(pdf_files)} PDF dosyası bulundu. Yükleme başlıyor...")

    # 1. Tüm PDF'leri eş zamanlı yükle
    load_tasks = [load_single_pdf(pdf) for pdf in pdf_files]
    loaded_docs_nested = await asyncio.gather(*load_tasks)
    all_docs = [doc for sublist in loaded_docs_nested for doc in sublist]
    print(f"Toplam {len(all_docs)} sayfa okundu. Chunking işlemine geçiliyor...")

    # 2. Chunk'lara böl
    chunked_docs = await process_docs(all_docs)
    print(f"Dokümanlar {len(chunked_docs)} parçaya bölündü. Supabase pgvector'e yükleniyor...")

    # 3. Model Ayarı (Yerel HuggingFace)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. ChromaDB'ye (Yerel) kaydet
    import shutil
    if os.path.exists(CHROMA_PERSIST_DIR):
        shutil.rmtree(CHROMA_PERSIST_DIR) # Eski kayıtları uçur (pre_delete mantığı)
        
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )

    batch_size = 200
    for i in range(0, len(chunked_docs), batch_size):
        batch = chunked_docs[i:i+batch_size]
        print(f"[{i}/{len(chunked_docs)}] Yükleniyor...")
        vector_store.add_documents(batch)
        
    print("Vektör veritabanı başarıyla güncellendi! ChromaDB'ye (Yerel) yüklendi!")


if __name__ == "__main__":
    asyncio.run(aingest_pdfs())
