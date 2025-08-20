# 🛠️ PyPDF-Tools v2 Sorun Giderme Rehberi

PyPDF-Tools v2 ile ilgili yaygın sorunlar ve çözüm yöntemleri.

## 📋 İçindekiler

- [Kurulum Sorunları](#kurulum-sorunları)
- [Tesseract OCR Sorunları](#tesseract-ocr-sorunları)
- [Performance Sorunları](#performance-sorunları)
- [PDF İşleme Sorunları](#pdf-işleme-sorunları)
- [UI ve Görüntü Sorunları](#ui-ve-görüntü-sorunları)
- [Ağ ve API Sorunları](#ağ-ve-api-sorunları)
- [Platform Özel Sorunlar](#platform-özel-sorunlar)
- [Log Analizi](#log-analizi)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)

---

## 🚀 Kurulum Sorunları

### Problem: "pypdf-tools komutu bulunamadı"

**Belirtiler:**
```bash
$ pypdf-tools
bash: pypdf-tools: command not found
```

**Çözümler:**

1. **PATH kontrol et:**
```bash
# Python scripts dizinini PATH'e ekle
export PATH="$HOME/.local/bin:$PATH"  # Linux/macOS
# veya Windows için:
# set PATH=%APPDATA%\Python\Python39\Scripts;%PATH%
```

2. **Tekrar kurulum yap:**
```bash
pip uninstall pypdf-tools
pip install --user pypdf-tools
```

3. **Sanal ortam kullan:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# veya Windows: venv\Scripts\activate
pip install pypdf-tools
```

### Problem: "ModuleNotFoundError: No module named 'pypdf_tools'"

**Çözüm:**
```bash
# Python yolu kontrol et
python -c "import sys; print(sys.path)"

# Pip list kontrol et
pip list | grep pypdf

# Doğru Python versiyonu ile kur
python3 -m pip install pypdf-tools
```

### Problem: "Permission denied" Hatası

**Linux/macOS:**
```bash
# Kullanıcı dizinine kur
pip install --user pypdf-tools

# veya sudo kullan (önerilmez)
sudo pip install pypdf-tools
```

**Windows:**
```powershell
# PowerShell'i yönetici olarak çalıştır
pip install pypdf-tools
```

### Problem: Dependency Çakışmaları

**Çözüm:**
```bash
# Temiz sanal ortam oluştur
python -m venv clean_env
source clean_env/bin/activate
pip install --upgrade pip
pip install pypdf-tools

# Conflict'leri çözümle
pip install --force-reinstall pypdf-tools
```

---

## 👁️ Tesseract OCR Sorunları

### Problem: "Tesseract bulunamadı" Hatası

**Belirtiler:**
```
OCRError: Tesseract binary not found
```

**Platform Özel Çözümler:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-tur tesseract-ocr-script-latn
```

**CentOS/RHEL/Fedora:**
```bash
sudo dnf install tesseract tesseract-langpack-tur
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
```powershell
# Chocolatey ile
choco install tesseract

# Manuel kurulum
# https://github.com/UB-Mannheim/tesseract/wiki adresinden indir
```

**PATH Konfigürasyonu:**
```bash
# .bashrc veya .zshrc dosyasına ekle
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Windows için Registry veya Environment Variables
```

### Problem: "Dil paketi bulunamadı" Hatası

**Çözüm:**
```bash
# Mevcut dilleri kontrol et
tesseract --list-langs

# Eksik dilleri kur
sudo apt install tesseract-ocr-tur  # Türkçe
sudo apt install tesseract-ocr-deu  # Almanca
sudo apt install tesseract-ocr-fra  # Fransızca

# Manuel dil paketi kurulumu
wget https://github.com/tesseract-ocr/tessdata/raw/main/tur.traineddata
sudo cp tur.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
```

### Problem: OCR Kalitesi Düşük

**İyileştirme Adımları:**

1. **Görüntü kalitesini artır:**
```python
ocr.process_pdf(
    'document.pdf',
    dpi=300,  # 150'den 300'e çıkar
    preprocess=True  # Ön işleme etkinleştir
)
```

2. **Doğru dil seçimi:**
```python
# Tek dil
language='tur'

# Çoklu dil
language='tur+eng'

# Otomatik dil algılama
language=ocr.detect_language('document.pdf')
```

3. **Görüntü ön işleme:**
```python
from pypdf_tools.core.ocr import ImagePreprocessor

preprocessor = ImagePreprocessor()
processed_image = preprocessor.enhance_image(
    image,
    denoise=True,
    deskew=True,
    contrast_enhance=True
)
```

---

## ⚡ Performance Sorunları

### Problem: Yavaş PDF İşleme

**Tanılama:**
```bash
# Sistem kaynaklarını izle
top -p $(pgrep -f pypdf-tools)
htop

# Disk I/O kontrol
iotop
```

**Optimizasyon:**

1. **Paralel işlemi artır:**
```python
pdf = PDFProcessor(max_workers=8)  # CPU çekirdek sayısına göre
```

2. **Bellek sınırını artır:**
```python
pdf = PDFProcessor(memory_limit=4096)  # MB cinsinden
```

3. **Geçici dosya konumunu SSD'ye taşı:**
```python
pdf = PDFProcessor(temp_dir='/tmp/pypdf_temp')  # SSD konumu
```

4. **Sıkıştırma kalitesini düşür:**
```python
pdf.compress_pdf('large.pdf', quality='low')  # Hızlı ama düşük kalite
```

### Problem: Yüksek Bellek Kullanımı

**Çözümler:**

1. **Chunk-based işleme:**
```python
# Büyük dosyalar için
pdf.process_large_file(
    'huge.pdf',
    chunk_size=50,  # Sayfa başına
    streaming=True
)
```

2. **Bellek temizliği:**
```python
import gc

def process_with_cleanup():
    # İşlem yap
    result = pdf.process_pdf('file.pdf')
    
    # Belleği temizle
    gc.collect()
    
    return result
```

### Problem: Disk Alanı Dolması

**Çözümler:**

1. **Otomatik temizlik:**
```python
pdf = PDFProcessor(auto_cleanup=True)
```

2. **Geçici dosya yönetimi:**
```bash
# Geçici dosyaları temizle
find /tmp -name "*pypdf*" -mtime +1 -delete

# Büyük geçici dosyaları bul
du -sh /tmp/pypdf_* | sort -hr
```

3. **Streaming işlem:**
```python
pdf.process_pdf(
    'input.pdf',
    streaming=True,  # Belleğe yüklemeden işle
    cleanup_on_error=True
)
```

---

## 📄 PDF İşleme Sorunları

### Problem: "Bozuk PDF" Hatası

**Belirtiler:**
```
PDFError: Invalid PDF structure
```

**Çözümler:**

1. **PDF onarımı:**
```python
from pypdf_tools.core.repair import PDFRepair

repair = PDFRepair()
fixed_pdf = repair.fix_pdf('broken.pdf', 'fixed.pdf')
```

2. **Alternatif parser:**
```python
pdf = PDFProcessor(parser='pymupdf')  # Varsayılan: pypdf2
```

3. **Manuel onarım araçları:**
```bash
# PDFtk ile onarım
pdftk broken.pdf output fixed.pdf

# qpdf ile onarım  
qpdf --qdf broken.pdf fixed.pdf
```

### Problem: "Şifreli PDF açılamıyor"

**Çözüm:**
```python
# Şifreyi sağla
pdf.decrypt_pdf('encrypted.pdf', 'decrypted.pdf', password='secret')

# veya işlem sırasında şifre ver
pdf.merge_pdfs(['encrypted.pdf'], 'output.pdf', password='secret')
```

### Problem: Font Sorunları

**Belirtiler:**
- Karakterler görünmüyor
- Font yerine kutu işaretleri

**Çözümler:**

1. **Font gömme:**
```python
pdf.merge_pdfs(
    files=['doc.pdf'],
    output='embedded.pdf',
    embed_fonts=True
)
```

2. **Sistem fontları yükle:**
```bash
# Ubuntu
sudo apt install fonts-liberation fonts-dejavu

# macOS
# Sistem fontları otomatik yüklü

# Windows
# Arial, Times New Roman otomatik mevcut
```

### Problem: Büyük Dosya İşleme

**Çözümler:**

1. **Dosyayı böl:**
```python
# Önce böl, sonra işle
parts = pdf.split_pdf('huge.pdf', method='size', max_size_mb=50)
processed_parts = [pdf.compress_pdf(part) for part in parts]
final = pdf.merge_pdfs(processed_parts, 'final.pdf')
```

2. **Streaming işlem:**
```python
pdf.process_pdf(
    'large.pdf',
    streaming=True,
    progress_callback=lambda x: print(f"İlerleme: %{x}")
)
```

---

## 🖥️ UI ve Görüntü Sorunları

### Problem: Uygulama Açılmıyor

**Tanılama:**
```bash
# Terminal'den başlat (hata mesajları için)
pypdf-tools --debug

# Log dosyasını kontrol et
tail -f ~/.config/PyPDF\ Tools\ v2/logs/app.log
```

**Çözümler:**

1. **Qt bağımlılık sorunu:**
```bash
# Linux
sudo apt install python3-pyqt6 libqt6widgets6

# Gerekirse PyQt'yi yeniden kur
pip uninstall PyQt6
pip install PyQt6
```

2. **Display sorunu (Linux):**
```bash
# X11 forwarding etkinleştir
export DISPLAY=:0.0

# Wayland sorunları için
export QT_QPA_PLATFORM=xcb
```

### Problem: Tema Sorunları

**Çözümler:**

1. **Tema sıfırlama:**
```bash
# Yapılandırmayı sıfırla
rm ~/.config/PyPDF\ Tools\ v2/config.json
```

2. **Sistem teması kullan:**
```python
from pypdf_tools.core.config import Config
config = Config()
config.set('appearance.theme', 'system')
config.set('appearance.use_system_theme', True)
```

### Problem: Yüksek DPI Sorunları

**Windows için:**
```python
# High DPI uyumluluğu
import os
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_SCALE_FACTOR'] = '1.0'
```

**macOS için:**
```bash
# Retina desteği
defaults write com.fatihbucaklioglu.pypdf-tools NSHighResolutionCapable -bool true
```

---

## 🌐 Ağ ve API Sorunları

### Problem: API Sunucusu Başlamıyor

**Port çakışması:**
```bash
# Port kullanımını kontrol et
netstat -tulpn | grep 8080
lsof -i :8080

# Farklı port kullan
pypdf-tools api --port 8888
```

**Firewall sorunları:**
```bash
# Linux
sudo ufw allow 8080

# Windows
netsh advfirewall firewall add rule name="PyPDF-Tools" dir=in action=allow protocol=TCP localport=8080
```

### Problem: WebSocket Bağlantısı Kopuyor

**Çözümler:**

1. **Connection timeout artır:**
```python
import websockets

websocket = websockets.connect(
    'ws://localhost:8080/ws',
    ping_timeout=60,
    close_timeout=30
)
```

2. **Proxy ayarları:**
```bash
# HTTP proxy atla
export NO_PROXY="localhost,127.0.0.1"
```

---

## 🔧 Platform Özel Sorunlar

### Windows Sorunları

#### Problem: "DLL load failed" Hatası

**Çözüm:**
```powershell
# Visual C++ Redistributable kur
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# Windows SDK kur (gerekirse)
winget install Microsoft.WindowsSDK
```

#### Problem: Long Path Hatası

**Çözüm:**
```powershell
# Grup İlkesi Düzenleyicisi'nde
# Computer Configuration > Administrative Templates > System > Filesystem
# "Enable Win32 long paths" -> Enabled

# Registry ile
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
```

### macOS Sorunları

#### Problem: "App can't be opened" Hatası

**Çözüm:**
```bash
# Gatekeeper'ı geçici olarak atla
sudo spctl --master-disable

# veya uygulamayı güvenilir listesine ekle
xattr -rd com.apple.quarantine "/Applications/PyPDF Tools v2.app"
```

#### Problem: Notarization Uyarısı

**Çözüm:**
```bash
# Geliştirici sertifikası kontrol et
codesign -v "/Applications/PyPDF Tools v2.app"

# Manuel onay
spctl --assess --type open --context context:primary-signature "/Applications/PyPDF Tools v2.app"
```

### Linux Sorunları

#### Problem: AppImage Çalışmıyor

**Çözüm:**
```bash
# FUSE kur
sudo apt install fuse libfuse2  # Ubuntu/Debian
sudo dnf install fuse fuse-libs  # Fedora

# Çalıştırma izni ver
chmod +x PyPDF-Tools.AppImage

# Manuel çalıştırma
./PyPDF-Tools.AppImage --appimage-extract-and-run
```

#### Problem: Desktop Integration

**Çözüm:**
```bash
# Desktop entry oluştur
./PyPDF-Tools.AppImage --appimage-integrate

# Manuel desktop entry
cat > ~/.local/share/applications/pypdf-tools.desktop << EOF
[Desktop Entry]
Name=PyPDF Tools v2
Exec=/path/to/PyPDF-Tools.AppImage
Type=Application
Categories=Office;
EOF
```

---

## 📊 Log Analizi

### Log Dosya Konumları

**Linux:**
```bash
~/.config/PyPDF\ Tools\ v2/logs/
├── app.log          # Ana uygulama logları
├── ocr.log          # OCR işlem logları  
├── api.log          # API server logları
└── error.log        # Sadece hatalar
```

**macOS:**
```bash
~/Library/Application Support/PyPDF Tools v2/logs/
```

**Windows:**
```powershell
%APPDATA%\PyPDF Tools v2\logs\
```

### Log Seviye Ayarlama

```python
from pypdf_tools.core.logging import setup_logging

# Debug seviyesi (çok detaylı)
setup_logging(level='DEBUG')

# Sadece hatalar
setup_logging(level='ERROR')

# Dosya boyutu sınırı
setup_logging(max_size_mb=10, backup_count=5)
```

### Yaygın Log Mesajları

#### Başarılı İşlem:
```
2024-01-15 14:30:15 INFO [PDFProcessor] PDF merge completed successfully
  Input files: ['doc1.pdf', 'doc2.pdf']
  Output: 'merged.pdf'
  Duration: 2.35s
  Pages: 25
```

#### Hata Durumu:
```
2024-01-15 14:32:47 ERROR [PDFProcessor] PDF merge failed
  Error: FileNotFoundError: doc1.pdf not found
  Stack trace:
    File "/src/pdf_processor.py", line 145, in merge_pdfs
    ...
```

#### Performance Uyarısı:
```
2024-01-15 14:35:12 WARNING [PDFProcessor] Large file processing
  File: large_document.pdf
  Size: 150MB
  Memory usage: 2.5GB
  Recommendation: Consider splitting file first
```

---

## ⚙️ Sistem Gereksinimleri Kontrol

### Python Sürümü

```bash
# Python sürümünü kontrol et
python --version
python3 --version

# Minimum: Python 3.8+
# Önerilen: Python 3.11+
```

### Bellek Kontrolü

```bash
# Sistem belleği
free -h  # Linux
vm_stat  # macOS
wmic memorychip get size  # Windows

# Minimum: 4GB RAM
# Önerilen: 8GB+ RAM
```

### Disk Alanı

```bash
# Disk alanı kontrolü
df -h  # Linux/macOS
dir C:  # Windows

# Minimum: 500MB boş alan
# Büyük dosyalar için: 2GB+ önerilir
```

### CPU Kontrol

```bash
# CPU bilgisi
nproc  # Linux
sysctl -n hw.ncpu  # macOS
echo %NUMBER_OF_PROCESSORS%  # Windows

# Çoklu çekirdek önerilir
```

---

## 🔧 Gelişmiş Tanılama

### Sistem Test

```bash
# Temel sistem testi
pypdf-tools --system-check

# Bağımlılık testi
pypdf-tools --check-dependencies

# Performance testi
pypdf-tools --benchmark
```

### Manuel Test

```python
#!/usr/bin/env python3
"""PyPDF-Tools sistem testi"""

import sys
import os
from pypdf_tools import PDFProcessor, OCREngine

def test_basic_functionality():
    """Temel işlevsellik testi"""
    
    try:
        # PDF işlemci testi
        pdf = PDFProcessor()
        print("✓ PDF Processor başlatıldı")
        
        # OCR testi
        ocr = OCREngine()
        print("✓ OCR Engine başlatıldı")
        
        # Tesseract testi
        if ocr.tesseract_path:
            print(f"✓ Tesseract bulundu: {ocr.tesseract_path}")
        else:
            print("✗ Tesseract bulunamadı")
            
        # Dil paketi testi
        languages = ocr.get_available_languages()
        print(f"✓ Mevcut diller: {len(languages)} adet")
        
    except Exception as e:
        print(f"✗ Test başarısız: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("PyPDF-Tools Sistem Testi")
    print("=" * 30)
    
    success = test_basic_functionality()
    
    if success:
        print("\n✓ Tüm testler başarılı!")
        sys.exit(0)
    else:
        print("\n✗ Test(ler) başarısız!")
        sys.exit(1)
```

---

## 🆘 Destek Alma

### Hata Raporu Oluşturma

```bash
# Otomatik hata raporu
pypdf-tools --generate-report

# Manuel bilgi toplama
pypdf-tools --system-info > system_info.txt
```

### GitHub Issue Şablonu

```markdown
## 🐛 Hata Raporu

**Hata Tanımı:**
Kısa ve net hata açıklaması

**Nasıl Tekrar Oluştur:**
1. Bu adımları uygula...
2. Bu komutu çalıştır...
3. Bu hatayı görü...

**Beklenen Davranış:**
Ne olması gerekiyordu?

**Gerçek Davranış:**
Ne oldu?

**Sistem Bilgisi:**
- İşletim Sistemi: [örn: Ubuntu 22.04]
- Python Sürümü: [örn: 3.11.2]
- PyPDF-Tools Sürümü: [örn: 2.0.0]
- Tesseract Sürümü: [örn: 4.1.1]

**Log Dosyası:**
```paste log content here```

**Ek Bilgi:**
Diğer önemli detaylar
```

### İletişim Kanalları

- **GitHub Issues**: [Hata bildirimi](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues)
- **GitHub Discussions**: [Genel sorular](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/discussions)  
- **Discord**: [PyPDF Tools Community](https://discord.gg/pypdf-tools)
- **Email**: support@pypdf-tools.com

---

Bu sorun giderme rehberi sürekli güncellenmektedir. Yeni sorunlar keşfettikçe bu dokümana ekleyeceğiz.
