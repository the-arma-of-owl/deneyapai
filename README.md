# Deneyap AI RAG Projesi: Kurulum ve Kullanım Rehberi (Yeni Başlayanlar İçin)

Merhaba! Bu rehber, kod yazmayı hiç bilmesen bile projeyi bilgisayarında nasıl çalıştırabileceğini ve yapay zekayı nasıl kullanabileceğini adım adım anlatıyor. Hadi başlayalım! 🚀

---

## 1️⃣ BAŞLANGIÇ: Bilgisayara Gerekli Programları Kurmak

Bu projeyi çalıştırabilmek için bilgisayarında "Python" isimli programlama dilinin yüklü olması gerekiyor.

### 🪟 Windows Kullanıcıları İçin:
1. İnternet tarayıcını aç ve [python.org/downloads](https://www.python.org/downloads/) adresine git.
2. "Download Python" yazan sarı butona tıkla ve inen dosyayı çalıştır.
3. **ÇOK ÖNEMLİ:** Kurulum ekranı açıldığında en altta yazan **"Add Python to PATH"** (veya Add python.exe to PATH) kutucuğunu kesinlikle **işaretle.**
4. Ardından "Install Now" seçeneğine tıklayarak kurulumu bitir.

### 🐧 Linux / Pardus Kullanıcıları İçin:
1. Bilgisayardaki "Uçbirim" (Terminal) uygulamasını açın.
2. Şu komutu yazıp `Enter`'a basın: `sudo apt update`
3. Şu komutla Python'u kurun: `sudo apt install python3 python3-venv python3-pip`

---

## 2️⃣ PROJEYİ KURMAK (İlk ve Tek Seferlik İşlem)

Projeyi indirdiğin klasöre (örneğin Masaüstü'ndeki RAG_T3 klasörü) gel. 
Bu klasörün içine GİT ve orada bir Komut Satırı (Terminal) aç.
*(Windows'ta klasör içindeyken üstteki klasör yolu çubuğuna tıklayıp `cmd` yazıp enter'a basarsan terminal o klasörde açılır).*

Şimdi sırasıyla aşağıdaki 3 satırı tek tek terminale yazıp her birinin bitmesi için bekle (Linux ve Windows için kodlar hafif farklıdır):

**Eğer Windows Kullanıyorsan Şunları Yaz:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Eğer Linux/Pardus Kullanıyorsan Şunları Yaz:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(Bu işlem bilgisayarının hızına göre birkaç dakika sürebilir. İnternetten gerekli kütüphaneleri indirecektir.)*

---

## 3️⃣ ŞİFRELERİ AYARLAMAK (.env dosyası)
Proje klasörünün içinde `.env.example` isimli bir dosya göreceksin.
1. Bu dosyanın adını sağ tıklayıp İsim Değiştir diyerek sadece `.env` (başında nokta olacak şekilde) yap.
2. Dosyayı Not Defteri ile aç.
3. İçerisinde `OPENAI_API_KEY` ve `GOOGLE_API_KEY` yazan yerlere elinizdeki şifreleri (API Key'leri) boşluk bırakmadan yapıştır ve dosyayı kaydet.

---

## 4️⃣ YENİ PDF'LER (BİLGİLER) EKLEMEK

Sisteme kendi kitaplarını veya dökümanlarını yüklemek çok kolaydır. Yapay zeka senin eklediğin bu kitapları okuyup oradan cevap verecektir!

1. Proje klasöründeki **`pdfs`** isimli klasörün içine git.
2. Yapay zekanın öğrenmesini istediğin tüm PDF dosyalarını buraya kopyala. 
   *(Hangi PDF'leri biliyorsa sadece onlardan cevap verebilir.)*
3. Yeni PDF ekledikten sonra terminale gelip **önce venv aktif değilse onu açman gerekir** (Bunu sadece yeni terminal açtıysan yap, eskisinde çalışıyorsan gerek yok):
   - Windows: `venv\Scripts\activate`
   - Linux: `source venv/bin/activate`
4. Sonra şu komutu çalıştırıp bekle:
   ```cmd
   python ingest_pdfs.py
   ```
Bu komut PDF'leri okuyacak, parçalayacak ve veritabanına kaydedecektir. İşlem bitince ekranda "Başarıyla yüklendi" tarzı bir yazı göreceksin.

*(💡 Not: "Sibergüvenlik" gibi klasörler veya kategoriler arayüzde doğrudan listelenmez. Sen yapay zekaya "Siber güvenlik nedir?" diye sorduğunda o arka planda o pdf'i bulur ve sorunun altına kaynağını etiket olarak ekler.)*

---

## 5️⃣ PROJEYİ ÇALIŞTIRMAK (Sohbet Etmeye Başlamak)

Her şey hazır! Şimdi yapay zekayı ayağa kaldırıyoruz.

**Windows Kullanıcıları:**
Terminali açıp proje klasörüne gidin ve şunu yazın (her başlatmada bunu kullanacaksınız):
```cmd
venv\Scripts\activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Linux Kullanıcıları:**
Projeyi başlatmak için daha da kolay bir yönteminiz var. Sadece şunu yazın:
```bash
./start.sh
```

**🎉 BİTTİ!**
Şimdi internet tarayıcınızı (Chrome vb.) açın ve adres çubuğuna şunu yazın:
**http://localhost:8000**

Karşınıza sohbet ekranı gelecek. PDF'lerinizin içeriğiyle ilgili sorular sormaya başlayabilirsiniz!
