# PyPDF-Tools Kurulum Rehberi

Bu rehber PyPDF-Tools hibrit PDF yönetim uygulamasını farklı platformlarda kurmanız için gerekli adımları açıklar.

## İçindekiler

- [Hızlı Kurulum](#hızlı-kurulum)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Platform-Specific Kurulumlar](#platform-specific-kurulumlar)
- [Kurulum Doğrulama](#kurulum-doğrulama)
- [Sorun Giderme](#sorun-giderme)
- [Güncelleme](#güncelleme)
- [Kaldırma](#kaldırma)

## Hızlı Kurulum

### PyPI'den Kurulum (Önerilen)

```bash
# Python 3.8+ gereklidir
pip install pypdf-tools

# Uygulamayı çalıştır
pypdf-tools
```

### Pre-built Binary İndirme

Platformunuz için pre-built binary'yi [GitHub Releases](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases) sayfasından indirebilirsiniz:

- **Windows**: `PyPDF-Tools-1.0.0-windows-x64.exe`
- **macOS**: `PyPDF-Tools-1.0.0-macos.dmg` 
- **Linux**: `PyPDF-Tools-1.0.0-linux-x86_64.AppImage`

## Sistem Gereksinimleri

### Minimum Gereksinimler

- **Python**: 3.8 veya üzeri
- **RAM**: 512 MB (2 GB önerilir)
- **Depolama**: 100 MB boş alan
- **Ekran**: 1024x768 çözünürlük

### Python Bağımlılıkları

Temel bağımlılıklar otomatik olarak kurulur:
- PyQt6 >= 6.4.0
- PyQt6-WebEngine >= 6.4.0  
- pypdf >= 3.0.0
- click >= 8.0.0
- Pillow >= 9.0.0

### Sistem Bağımlılıkları

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3-pip
sudo apt install libgl1-mesa-glx libegl1-mesa libxcb-xkb1
```

#### macOS
```bash
# Homebrew ile
brew install python@3.11

# Python zaten kurulu olabilir
python3 --version
```

#### Windows
- Python 3.8+ ([python.org](https://python.org)'den indirin)
- Windows 10/11 (Windows 7/8 için ek konfigürasyon gerekebilir)

## Platform-Specific Kurulumlar

### 🐧 Linux

#### Ubuntu/Debian

```bash
# 1. Sistem güncellemesi
sudo apt update && sudo apt upgrade

# 2. Python ve pip kurulumu
sudo apt install python3 python3-pip python3-venv

# 3. Qt bağımlılıkları
sudo apt install qtbase5-dev qt5-qmake
sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 libxss1

# 4. PyPDF-Tools kurulumu
pip3 install --user pypdf-tools

# 5. PATH'e ekleme (gerekiyorsa)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Fedora/CentOS/RHEL

```bash
# 1. Python ve pip
sudo dnf install python3 python3-pip python3-devel

# 2. Qt dependencies
sudo dnf install qt5-qtbase-devel mesa-libGL-devel

# 3. PyPDF-Tools
pip3 install --user pypdf-tools
```

#### Arch Linux

```bash
# 1. Python setup
sudo pacman -S python python-pip

# 2. Qt dependencies  
sudo pacman -S qt5-base mesa

# 3. PyPDF-Tools
pip install --user pypdf-tools
```

#### AppImage (Tüm Linux Dağıtımları)

```bash
# 1. AppImage indir
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/download/v1.0.0/PyPDF-Tools-1.0.0-linux-x86_64.AppImage

# 2. Çalıştırma izni ver
chmod +x PyPDF-Tools-1.0.0-linux-x86_64.AppImage

# 3. Çalıştır
./PyPDF-Tools-1.0.0-linux-x86_64.AppImage
```

### 🍎 macOS

#### Homebrew ile Kurulum

```bash
# 1. Homebrew kurulumu (yoksa)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Python kurulumu
brew install python@3.11

# 3. PyPDF-Tools kurulumu
pip3 install pypdf-tools

# 4. Uygulama başlatma
pypdf-tools
```

#### macOS Binary (.dmg)

1. [GitHub Releases](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases) sayfasından `.dmg` dosyasını indirin
2. DMG dosyasını çift tıklayarak mount edin
3. PyPDF-Tools.app'i Applications klasörüne sürükleyin
4. Launchpad'den veya Applications klasöründen başlatın

**Güvenlik Notu:** İlk çalıştırmada "Tanımlanamayan geliştirici" uyarısı alabilirsiniz:
1. System Preferences > Security & Privacy
2. "Allow apps downloaded from: App Store and identified developers" seçin
3. Veya terminalde: `xattr -dr com.apple.quarantine /Applications/PyPDF-Tools.app`

### 🪟 Windows

#### Python ile Kurulum

```cmd
# 1. Python kurulumu kontrolü
python --version

# Eğer Python yoksa python.org'dan indirip kurun

# 2. pip güncellemesi
python -m pip install --upgrade pip

# 3. PyPDF-Tools kurulumu
pip install pypdf-tools

# 4. Uygulama başlatma
pypdf-tools
```

#### Windows Installer (.exe)

1. [GitHub Releases](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases) sayfasından `PyPDF-Tools-1.0.0-windows-x64.exe` dosyasını indirin
2. İndirilen dosyayı yönetici olarak çalıştırın
3. Kurulum sihirbazını takip edin
4. Başlat menüsünden veya masaüstü kısayolundan başlatın

#### Windows Store (Gelecekte)

Windows Store'da yayınlanacak (roadmap'de).

#### Chocolatey ile Kurulum

```powershell
# 1. Chocolatey kurulumu (yoksa)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. PyPDF-Tools kurulumu
choco install pypdf-tools
```

## Kurulum Doğrulama

Kurulum başarılı olduktan sonra aşağıdaki adımları izleyerek doğrulayın:

### Komut Satırından Test

```bash
# Sürüm kontrolü
pypdf-tools --version
# Çıktı: PyPDF-Tools 1.0.0

# CLI komutları test
pypdf --help
pypdf info /path/to/sample.pdf

# GUI uygulamayı başlat
pypdf-tools
```

### Python'dan Import Test

```python
# Python interpreter'da
import pypdf_tools
print(pypdf_tools.__version__)

# PDF viewer widget test
from pypdf_tools.features.pdf_viewer import PDFViewerWidget
print("Import successful!")
```

### Fonksiyonel Test

1. Uygulamayı başlatın: `pypdf-tools`
2. Dosya > Aç menüsünden bir PDF dosyası açın
3. Zoom, rotation gibi temel fonksiyonları test edin
4. Tema değiştirmeyi deneyin (Görünüm > Tema)

## Sorun Giderme

### Yaygın Kurulum Sorunları

#### 1. PyQt6 Kurulum Hatası

**Hata:** `Failed building wheel for PyQt6`

**Çözüm:**
```bash
# Sistem bağımlılıkları kur (Linux)
sudo apt install build-essential python3-dev

# veya pre-built wheel kullan
pip install --only-binary=all pypdf-tools
```

#### 2. Qt Platform Plugin Hatası

**Hata:** `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"`

**Çözüm (Linux):**
```bash
sudo apt install libxcb-xkb1 libxcb-render-util0 libxcb-icccm4 libxcb-keysyms1 libxcb-randr0
```

#### 3. Permission Denied (macOS)

**Hata:** App açılmıyor, güvenlik uyarısı

**Çözüm:**
```bash
# Terminal'de quarantine kaldır
xattr -dr com.apple.quarantine /Applications/PyPDF-Tools.app

# veya System Preferences > Security & Privacy'den izin ver
```

#### 4. DLL Load Failed (Windows)

**Hata:** `ImportError: DLL load failed`

**Çözüm:**
```cmd
# Visual C++ Redistributable kur
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# veya conda kullan
conda install pypdf-tools
```

### Log ve Debug

#### Debug Modu

```bash
# Verbose logging ile çalıştır
pypdf-tools --verbose

# veya environment variable
export PYPDF_DEBUG=1
pypdf-tools
```

#### Log Dosyaları

**Linux/macOS:**
- `~/.local/share/PyPDF-Tools/logs/app.log`
- `~/.cache/PyPDF-Tools/`

**Windows:**
- `%APPDATA%\PyPDF-Tools\logs\app.log`
- `%LOCALAPPDATA%\PyPDF-Tools\`

### Performance Sorunları

#### Yavaş Başlangıç

```bash
# React build'i önceden hazırla
python -c "import pypdf_tools; print('Warming up...')"

# SSD kullanın, HDD'de yavaş olabilir
```

#### Memory Kullanımı

```bash
# Büyük PDF'ler için memory limit
export PYPDF_MEMORY_LIMIT=1024  # MB
pypdf-tools
```

## Virtual Environment Kurulumu

Sistem Python'unu etkilemeden kurulum için:

```bash
# 1. Virtual environment oluştur
python -m venv pypdf-env

# 2. Aktifleştir
source pypdf-env/bin/activate  # Linux/Mac
# veya
pypdf-env\Scripts\activate     # Windows

# 3. PyPDF-Tools kur
pip install pypdf-tools

# 4. Çalıştır
pypdf-tools

# 5. Deactivate (isteğe bağlı)
deactivate
```

## Docker ile Kurulum

Containerized ortam için:

```bash
# 1. Docker image çek
docker pull ghcr.io/fatih-bucaklioglu/pypdf-tools:latest

# 2. X11 forwarding ile çalıştır (Linux)
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd):/workspace \
  ghcr.io/fatih-bucaklioglu/pypdf-tools:latest

# 3. macOS için XQuartz gerekir
# Windows için WSL2 + X server
```

## Güncelleme

### PyPI'den Güncelleme

```bash
# En son sürüme güncelle
pip install --upgrade pypdf-tools

# Belirli sürüme güncelle  
pip install pypdf-tools==1.1.0

# Development version
pip install git+https://github.com/Fatih-Bucaklioglu/PyPDF-Tools.git
```

### Binary Güncelleme

1. Eski sürümü kaldırın
2. Yeni binary'yi indirin ve kurun
3. Settings/preferences korunur

### Otomatik Güncelleme

```bash
# Güncelleme kontrolü
pypdf-tools --check-update

# Auto-update (gelecekte eklenecek)
```

## Kaldırma

### pip ile Kaldırma

```bash
# PyPDF-Tools kaldır
pip uninstall pypdf-tools

# Bağımlılıkları da kaldır (dikkatli)
pip uninstall PyQt6 PyQt6-WebEngine pypdf click Pillow
```

### Sistem Dosyaları Temizleme

**Linux/macOS:**
```bash
# Kullanıcı verileri
rm -rf ~/.local/share/PyPDF-Tools
rm -rf ~/.config/PyPDF-Tools
rm -rf ~/.cache/PyPDF-Tools

# Binary (eğer manuel kurduysanız)
rm /usr/local/bin/pypdf-tools
```

**Windows:**
```cmd
# Kullanıcı verileri
rmdir /s "%APPDATA%\PyPDF-Tools"
rmdir /s "%LOCALAPPDATA%\PyPDF-Tools"

# Uninstaller çalıştır (binary kurulumda)
"%PROGRAMFILES%\PyPDF-Tools\uninstall.exe"
```

## Ek Konfigürasyonlar

### Desktop Integration (Linux)

```bash
# .desktop dosyası oluştur
cat > ~/.local/share/applications/pypdf-tools.desktop << EOF
[Desktop Entry]
Version=1.0
Name=PyPDF Tools
Comment=Hibrit PDF yönetim uygulaması
Exec=pypdf-tools %f
Icon=pypdf-tools
Terminal=false
Type=Application
Categories=Office;Graphics;
MimeType=application/pdf;
EOF

# MIME association
xdg-mime default pypdf-tools.desktop application/pdf
```

### File Association (Windows)

Registry'de PDF dosyaları için PyPDF-Tools'u varsayılan yapma:

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\.pdf]
@="PyPDFTools.Document"

[HKEY_CURRENT_USER\Software\Classes\PyPDFTools.Document\shell\open\command]
@="\"C:\\Program Files\\PyPDF-Tools\\pypdf-tools.exe\" \"%1\""
```

### Shell Integration

```bash
# Bash completion (Linux/macOS)
pypdf-tools --install-completion bash >> ~/.bashrc

# PowerShell completion (Windows)
pypdf-tools --install-completion powershell >> $PROFILE
```

## Performans Optimizasyonu

### SSD Optimizasyonu
- PyPDF-Tools'u SSD'ye kurun
- Temp dizinini SSD'ye yönlendirin

### RAM Optimizasyonu
```bash
# Memory-mapped files kullan
export PYPDF_USE_MMAP=1

# Buffer size artır
export PYPDF_BUFFER_SIZE=8192
```

### GPU Acceleration (Experimental)
```bash
# OpenGL acceleration
export QT_OPENGL=desktop

# Software rendering (problem varsa)
export QT_OPENGL=software
```

## Destek ve Yardım

### Dokümantasyon
- [Kullanıcı Rehberi](user-guide.md)
- [Developer Guide](developer-guide.md)
- [API Referansı](api-reference.md)

### Community Support
- GitHub Issues: [Bug reports ve özellik önerileri](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues)
- GitHub Discussions: [Genel sorular](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/discussions)
- Email: fatih.bucaklioglu@example.com

### Pro Support
- Enterprise support mevcuttur
- Custom feature development
- Priority bug fixes
- İletişim: pro-support@pypdf-tools.com

---

**Kurulum ile ilgili herhangi bir sorunda GitHub Issues'da yardım isteyebilirsiniz.**

Son güncelleme: 2024-01-15
