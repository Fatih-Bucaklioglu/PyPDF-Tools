# 📖 PyPDF-Tools v2 Kullanıcı Kılavuzu

PyPDF-Tools v2'nin tüm özelliklerini nasıl kullanacağınızı öğrenin.

## 🎯 İlk Başlangıç

### Uygulamayı İlk Kez Başlatma

1. **Uygulamayı açın**: Masaüstü kısayolu, başlat menüsü veya komut satırından
2. **İlk çalıştırma sihirbazı** otomatik olarak açılacak
3. **Ayarlarınızı yapılandırın**:
   - **Tema seçimi**: Aydınlık, Karanlık, Neon, Gece Yarısı Mavisi
   - **Dil seçimi**: Türkçe, İngilizce ve diğer diller
   - **Klasör erişim izinleri**: Hangi klasörlere erişim istediğinizi belirleyin
   - **OCR dil paketleri**: İhtiyaç duyduğunuz dilleri seçin

### Arayüz Tanıtımı

```
┌─────────────────────────────────────────────────────────┐
│  📁 Dosya   🔧 Düzenle   🎨 Görünüm   🔧 Ayarlar   ❓ Yardım │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌───────────────────────────────────┐ │
│ │ 📋 İşlemler  │  │         Ana Çalışma Alanı         │ │
│ │             │  │                                   │ │
│ │ 🔗 Birleştir │  │    Dosyalarınızı buraya          │ │
│ │ ✂️  Böl      │  │    sürükleyip bırakın            │ │
│ │ 🔄 Döndür    │  │                                   │ │
│ │ 🗜️  Sıkıştır │  │         veya                      │ │
│ │ 🔒 Şifrele   │  │                                   │ │
│ │ 🔍 OCR       │  │    "Dosya Seç" butonuna          │ │
│ │ ⚙️  Diğer    │  │    tıklayın                      │ │
│ └─────────────┘  └───────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 📊 Durum: Hazır | 🚀 CPU: %12 | 💾 RAM: 2.1GB          │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Dosya İşlemleri

### Dosya Ekleme Yöntemleri

#### 1. Sürükle ve Bırak
- PDF dosyalarını doğrudan ana çalışma alanına sürükleyin
- Çoklu dosya seçimi desteklenir
- Klasörleri sürüklerseniz içindeki tüm PDF'ler eklenir

#### 2. Dosya Seçici
```
Dosya → Aç → PDF dosyalarını seçin → Aç
```

#### 3. Komut Satırı
```bash
pypdf-tools dosya1.pdf dosya2.pdf
```

### Desteklenen Formatlar

| Format | Okuma | Yazma | Notlar |
|--------|-------|-------|--------|
| **PDF** | ✅ | ✅ | Tüm PDF sürümleri |
| **DOCX** | ✅ | ✅ | LibreOffice gerekli |
| **XLSX** | ✅ | ✅ | LibreOffice gerekli |
| **PPTX** | ✅ | ✅ | LibreOffice gerekli |
| **JPG/JPEG** | ✅ | ✅ | Görüntü dönüştürme |
| **PNG** | ✅ | ✅ | Şeffaflık korunur |
| **TIFF** | ✅ | ✅ | Çoklu sayfa desteği |
| **BMP** | ✅ | ✅ | Windows Bitmap |

---

## 🔧 Temel İşlemler

### 1. PDF Birleştirme (Merge)

#### Basit Birleştirme
1. **İşlem seçin**: Sol menüden "Birleştir" seçeneğini tıklayın
2. **Dosya ekleyin**: Birleştirilecek PDF'leri ekleyin
3. **Sıralama**: Dosyaları istediğiniz sıraya sürükleyin
4. **Çıktı ayarları**: Çıktı dosya adı ve konumunu belirleyin
5. **Başlat**: "Birleştir" butonuna tıklayın

#### Gelişmiş Seçenekler
- **Sayfa aralıkları**: Her dosyadan sadece belirli sayfaları seçin
- **Bookmark koruma**: Var olan yer imlerini koru
- **Metadata birleştirme**: Tüm dosyaların metadata'sını birleştir

```
📖 Örnek:
Dosya 1: sayfa 1-5
Dosya 2: sayfa 3-7  
Dosya 3: tüm sayfalar
→ Çıktı: 5+5+10 = 20 sayfalık PDF
```

### 2. PDF Bölme (Split)

#### Sayfa Bazlı Bölme
```
Bölme Türü: Sayfa Sayısı
Her X sayfada bir böl: 5
→ 20 sayfalık PDF → 4 adet 5 sayfalık PDF
```

#### Boyut Bazlı Bölme
```
Bölme Türü: Dosya Boyutu  
Maksimum boyut: 2 MB
→ Büyük PDF → Birden fazla küçük PDF
```

#### Yer İmi Bazlı Bölme
```
Bölme Türü: Bookmark
→ Her yer iminde yeni dosya oluştur
```

### 3. Sayfa Döndürme

#### Basit Döndürme
- **90° saat yönünde**
- **90° saat yönünün tersine** 
- **180° döndürme**

#### Gelişmiş Döndürme
- **Sayfa seçimi**: Sadece belirli sayfaları döndür
- **Koşullu döndürme**: Yatay/dikey sayfalara göre otomatik döndür
- **Toplu işlem**: Birden fazla PDF'i aynı anda döndür

### 4. PDF Sıkıştırma

#### Sıkıştırma Seviyeleri
| Seviye | Kalite | Boyut Azalma | Kullanım |
|--------|--------|--------------|----------|
| **Düşük** | %95 | %10-20 | Arşivleme |
| **Orta** | %80 | %30-50 | Web paylaşımı |
| **Yüksek** | %60 | %50-70 | E-posta eki |
| **Maksimum** | %40 | %70-85 | Mobil cihazlar |

#### Sıkıştırma Seçenekleri
- **Görüntü kalitesi**: DPI ve JPEG kalite ayarı
- **Font optimizasyonu**: Kullanılmayan fontları kaldır
- **Metadata temizliği**: Gereksiz bilgileri sil
- **Renk profili**: Grayscale/RGB optimizasyonu

---

## 🔐 Güvenlik Özellikleri

### PDF Şifreleme

#### Kullanıcı Şifresi (User Password)
```
PDF'i açmak için şifre: ********
→ Dosya şifreli olarak kaydedilir
```

#### Sahip Şifresi (Owner Password)
```
İzinleri değiştirmek için şifre: ********
→ Yazdırma, kopyalama vb. izinler kontrolü
```

#### İzin Ayarları
- **Yazdırma**: İzin ver / Yasakla / Sadece düşük kalite
- **Metin kopyalama**: İzin ver / Yasakla
- **Sayfa değiştirme**: İzin ver / Yasakla  
- **Form doldurma**: İzin ver / Yasakla
- **Açıklama ekleme**: İzin ver / Yasakla

### Dijital İmzalama

#### Sertifika Oluşturma
1. **Araçlar → Dijital İmza → Yeni Sertifika**
2. **Kişisel bilgileri doldurun**
3. **Anahtar boyutunu seçin**: 2048 bit / 4096 bit
4. **Sertifikayı kaydedin**: .p12 formatında

#### İmzalama İşlemi
1. **PDF'i açın**
2. **Dijital İmza** aracını seçin
3. **İmza konumunu** işaretleyin
4. **Sertifikayı seçin** ve şifresini girin
5. **İmzalayın**

---

## 🎨 Düzenleme Araçları

### Filigran Ekleme

#### Metin Filigranı
```
Metin: "TASLAK KOPYA"
Font: Arial, 24pt
Renk: Kırmızı, %50 şeffaf
Konum: Merkez, 45° açı
```

#### Görüntü Filigranı  
```
Dosya: logo.png
Boyut: %20 ölçek
Konum: Sağ alt köşe
Şeffaflık: %30
```

### Sayfa Numaralama

#### Basit Numaralama
```
Format: "Sayfa X"
Konum: Alt merkez
Font: Times New Roman, 12pt
Başlangıç: 1
```

#### Gelişmiş Numaralama
```
Format: "X / Y sayfası"
Konum: Sağ alt
Sayfa aralığı: 3-50
Atla: İlk 2 sayfa
```

### Üstbilgi / Altbilgi

#### Üstbilgi Örneği
```
Sol: Belge başlığı
Merkez: Tarih (DD.MM.YYYY)
Sağ: Şirket adı
```

#### Altbilgi Örneği
```
Sol: "Gizli" sınıflandırması  
Merkez: Sayfa numarası
Sağ: "© 2024 Şirket Adı"
```

---

## 🔍 OCR (Optik Karakter Tanıma)

### Dil Paketi Kurulumu

#### Otomatik Kurulum
1. **Ayarlar → OCR → Dil Paketleri**
2. **İstediğiniz dilleri seçin**
3. **İndir ve Kur** butonuna tıklayın

#### Manuel Kurulum
```bash
# Türkçe dil paketi
pypdf-tools --install-ocr-lang tur

# Çoklu dil
pypdf-tools --install-ocr-lang eng,deu,fra
```

### OCR İşlemi

#### Basit OCR
1. **Taranmış PDF'i açın**
2. **İşlemler → OCR** seçin
3. **Dili seçin**: Otomatik algılama veya manuel seçim
4. **İşlemi başlatın**

#### Gelişmiş OCR Ayarları
```
Dil: Türkçe + İngilizce (karma metin için)
DPI: 300 (yüksek kalite)
Ön işleme: Aktif (gürültü azaltma)
Sayfa aralığı: 1-10
Çıktı: Aranabilir PDF (orijinal + metin katmanı)
```

#### OCR Kalite İpuçları
- **DPI**: 300+ önerilen, 600+ ideal
- **Kontrast**: Siyah metin, beyaz arka plan
- **Döndürme**: Metni düz hizala
- **Gürültü**: Ön işleme ile azalt
- **Font**: 12pt+ boyutlar daha iyi sonuç

---

## 🛠️ Gelişmiş Özellikler

### PDF Okuyucu Modu

#### Okuma Araçları
- **Zoom**: %25-%800 arası
- **Döndürme**: 90°, 180°, 270°  
- **Tam ekran**: F11 tuşu
- **Gece modu**: Göz koruma filtresi
- **Sayfa küçük resimleri**: Yan panel

#### Metin Araçları
- **Arama**: Ctrl+F ile gelişmiş arama
- **Vurgulama**: Renkli vurgulama araçları
- **Notlar**: Sayfalara not ekleme
- **Çizim**: Kalem ile işaretleme

### Otomasyon Sistemi

#### Klasör İzleme
```
İzlenen klasör: ~/Downloads
Dosya kalıbı: *.pdf
İşlem: Sıkıştırma
Çıktı klasörü: ~/Documents/Compressed
Tetikleyici: Yeni dosya eklendiğinde
```

#### Zamanlı İşlemler
```
Zamanlama: Her gün 02:00
İşlem: Backup klasörünü sıkıştır
Koşul: Dosya boyutu > 10MB
E-posta bildirimi: Aktif
```

### Toplu İşlem

#### Çoklu Dosya İşleme
1. **Dosya → Toplu İşlem**
2. **İşlem türünü seçin**: Sıkıştır, Döndür, OCR vb.
3. **Dosyaları ekleyin**: Drag & drop veya klasör seçimi
4. **Ayarları yapın**: Tüm dosyalar için ortak ayarlar
5. **İşlemi başlatın**: İlerleme çubuğu ile takip

#### İşlem Kuyrukları
```
Kuyruk 1: PDF'leri sıkıştır (15 dosya)
Kuyruk 2: OCR işlemi uygula (8 dosya)  
Kuyruk 3: Filigran ekle (25 dosya)
→ Sırayla ve otomatik olarak işler
```

---

## 🎛️ Kişiselleştirme

### Tema Ayarları

#### Hazır Temalar
- **Aydınlık**: Modern beyaz tasarım
- **Karanlık**: Göz dostu koyu tema  
- **Neon**: Canlı renkler ve gradient efektler
- **Gece Yarısı Mavisi**: Derin mavi profesyonel görünüm

#### Özel Tema Oluşturma
```json
{
  "name": "Özel Tema",
  "colors": {
    "primary": "#007ACC",
    "secondary": "#00BCF2", 
    "background": "#1E1E1E",
    "text": "#FFFFFF",
    "accent": "#FF6B35"
  },
  "fonts": {
    "interface": "
