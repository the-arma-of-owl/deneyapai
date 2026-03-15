import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "hybrid_rag_collection_gemini"

def export_data():
    print("=" * 50)
    print("ChromaDB Dışa Aktarımı Başlatılıyor...")
    print("=" * 50)

    if not os.path.exists(CHROMA_PERSIST_DIR):
        print("❌ HATA: './chroma_db' klasörü bulunamadı. Lütfen önce ingest_pdfs.py ile PDF'leri indeksleyin.")
        return

    print("🤖 Model başlatılıyor (Veritabanına girmek için)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("🔗 Veritabanına (Chroma) bağlanılıyor...")
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

    # get() fonksiyonu ile veritabanındaki tüm ham kayıtları (ve metadataları) çekeriz.
    print("📦 Veriler çekiliyor...")
    data = vector_store.get()
    
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])
    
    if not documents:
        print("❌ Veritabanında hiçbir metin bulunamadı.")
        return

    output_file = "okunan_pdf_parcalari.txt"
    
    print(f"✍️ Dosyaya yazılıyor: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("   CHROMA VEKTÖR VERİTABANINA YAZILAN PARÇALANMIŞ (CHUNKED) PDF'LER\n")
        f.write(f"   🔥 TESPİT EDİLEN TOPLAM PARÇA SAYISI: {len(documents)}\n")
        f.write("=" * 70 + "\n\n")

        for idx, (doc, meta) in enumerate(zip(documents, metadatas)):
            source_file = meta.get('source', 'Bilinmiyor')
            page_num = meta.get('page', 'Bilinmiyor')
            
            # Sadece dosya ismini almak için yolu böl
            if "/" in source_file:
                source_file = source_file.split("/")[-1]
            elif "\\" in source_file:
                source_file = source_file.split("\\")[-1]

            f.write(f"--- [ PARÇA #{idx + 1} ] ---\n")
            f.write(f"📍 Dosya: {source_file}\n")
            f.write(f"📄 Sayfa: {page_num}\n")
            f.write("📝 Parçalanan Metin:\n")
            f.write(doc)
            f.write("\n\n" + ("-" * 50) + "\n\n")
    
    print(f"✅ İŞLEM BAŞARILI! Toplam {len(documents)} adet vektör parçası geri çözüldü.")
    print(f"✅ Sonuçları şu dosyadan inceleyebilirsiniz: {output_file}")

if __name__ == "__main__":
    export_data()
