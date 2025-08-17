# 🚀 PyPDF-Tools v2 Kurulum Rehberi

PyPDF-Tools v2'yi sisteminize kurmanın en kolay yollarını bu rehberde bulabilirsiniz.

## 📋 Sistem Gereksinimleri

### Minimum Gereksinimler

| İşletim Sistemi | Minimum Sürüm | RAM | Depolama |
|---|---|---|---|
| **Windows** | Windows 10 64-bit | 4 GB | 500 MB |
| **macOS** | macOS 10.15 Catalina | 4 GB | 500 MB |
| **Linux** | Ubuntu 18.04+ (veya eşdeğeri) | 4 GB | 500 MB |

### Önerilen Gereksinimler

| İşletim Sistemi | Önerilen Sürüm | RAM | Depolama |
|---|---|---|---|
| **Windows** | Windows 11 | 8 GB+ | 2 GB+ |
| **macOS** | macOS 12+ | 8 GB+ | 2 GB+ |
| **Linux** | Ubuntu 22.04+ | 8 GB+ | 2 GB+ |

### Ek Bağımlılıklar

- **Python**: 3.8+ (kaynak koddan kurulum için)
- **Tesseract OCR**: 4.0+ (OCR özellikleri için)
- **LibreOffice**: 7.0+ (Office dosya dönüştürmeleri için)

---

## 🐧 Linux Kurulumu

### 1. AppImage Kurulumu (Önerilen)

AppImage, herhangi bir Linux dağıtımında çalışan taşınabilir uygulama formatıdır.

```bash
# 1. AppImage dosyasını indirin
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage

# 2. Çalıştırılabilir yapın
chmod +x PyPDF-Tools.AppImage

# 3. Çalıştırın
./PyPDF-Tools.AppImage
```

#### AppImage'i Sisteme Entegre Etme

```bash
# AppImages dizini oluştur
mkdir -p ~/Applications

# AppImage'i taşı
mv PyPDF-Tools.AppImage ~/Applications/

# Desktop entry oluştur
cat > ~/.local/share/applications/pypdf-tools.desktop << EOF
[Desktop Entry]
Name=PyPDF Tools v2
Comment=Modern PDF İşleme Uygulaması
Exec=$HOME/Applications/PyPDF-Tools.AppImage
Icon=pypdf-tools
Terminal=false
Type=Application
Categories=Office;Graphics;
EOF

# Menüyü güncelle
update-desktop-database ~/.local/share/applications/
```

### 2. DEB Paketi Kurulumu (Ubuntu/Debian)

```bash
# 1. DEB paketini indirin
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/pypdf-tools_2.0.0_amd64.deb

# 2. Paketi kurun
sudo dpkg -i pypdf-tools_2.0.0_amd64.deb

# 3. Eksik bağımlılıkları çözün (gerekirse)
sudo apt-get install -f

# 4. Uygulamayı başlatın
pypdf-tools
```

### 3. RPM Paketi Kurulumu (Red Hat/Fedora/openSUSE)

```bash
# Fedora/CentOS/RHEL için
sudo dnf install https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/pypdf-tools-2.0.0-1.x86_64.rpm

# openSUSE için
sudo zypper install https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/pypdf-tools-2.0.0-1.x86_64.rpm
```

### 4. AUR Paketi Kurulumu (Arch Linux)

```bash
# yay ile
yay -S pypdf-tools

# paru ile
paru -S pypdf-tools

# Manuel kurulum
git clone https://aur.archlinux.org/pypdf-tools.git
cd pypdf-tools
makepkg -si
```

### 5. Otomatik Kurulum Scripti

```bash
# Tek komutla kurulum
curl -sSL https://raw.githubusercontent.com/Fatih-Bucaklioglu/PyPDF-Tools/main/install-linux.sh | bash
```

---

## 🍎 macOS Kurulumu

### 1. DMG Kurulumu (Önerilen)

```bash
# 1. DMG dosyasını indirin
curl -L -o PyPDF-Tools.dmg https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.dmg

# 2. DMG'yi mount edin
hdiutil attach PyPDF-Tools.dmg

# 3. Uygulamayı Applications klasörüne sürükleyin
cp -R "/Volumes/PyPDF Tools v2/PyPDF Tools v2.app" /Applications/

# 4. DMG'yi çıkarın
hdiutil detach "/Volumes/PyPDF Tools v2"

# 5. Uygulamayı başlatın
open "/Applications/PyPDF Tools v2.app"
```

### 2. Homebrew Kurulumu

```bash
# 1. Homebrew tap ekleyin
brew tap fatih-bucaklioglu/pypdf-tools

# 2. Uygulamayı kurun
brew install --cask pypdf-tools

# 3. Uygulamayı başlatın
open -a "PyPDF Tools v2"
```

### 3. Otomatik Kurulum Scripti

```bash
# Tek komutla kurulum
curl -sSL https://raw.githubusercontent.com/Fatih-Bucaklioglu/PyPDF-Tools/main/install-macos.sh | bash
```

### 4. Gatekeeper Ayarları

macOS Gatekeeper uyarısı alırsanız:

```bash
# Uygulamayı güvenilir uygulamalar listesine ekleyin
sudo spctl --add "/Applications/PyPDF Tools v2.app"

# veya Gatekeeper'ı geçici olarak devre dışı bırakın
sudo spctl --master-disable
```

---

## 🪟 Windows Kurulumu

### 1. MSI Kurulumu (Önerilen)

1. **[PyPDF-Tools-Setup.msi](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools-Setup.msi)** dosyasını indirin
2. Dosyaya çift tıklayın
3. Kurulum sihirbazını takip edin
4. Başlat menüsünden "PyPDF Tools v2" uygulamasını başlatın

### 2. Portable Sürüm

1. **[PyPDF-Tools-Portable.zip](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools-Portable.zip)** dosyasını indirin
2. Herhangi bir klasöre çıkartın
3. `PyPDF-Tools.exe` dosyasını çalıştırın

### 3. PowerShell Otomatik Kurulum

PowerShell'i **yönetici olarak** açın ve çalıştırın:

```powershell
irm https://raw.githubusercontent.com/Fatih-Bucaklioglu/PyPDF-Tools/main/install-windows.ps1 | iex
```

### 4. Chocolatey Kurulumu

```powershell
# Chocolatey ile kurulum
choco install pypdf-tools

# Güncelleme
choco upgrade pypdf-tools
```

### 5. Winget Kurulumu

```powershell
# Winget ile kurulum
winget install FatihBucaklioglu.PyPDFTools

# Güncelleme
winget upgrade FatihBucaklioglu.PyPDFTools
```

---

## 🔧 Kaynak Koddan Kurulum

Geliştirici sürümü veya özelleştirmeler için:

### Gereksinimler

```bash
# Python 3.8+
python --version

# Git
git --version

# Node.js 16+ (UI için)
node --version
```

### Kurulum Adımları

```bash
# 1. Repository'i klonlayın
git clone https://github.com/Fatih-Bucaklioglu/PyPDF-Tools.git
cd PyPDF-Tools

# 2. Python sanal ortamı oluşturun
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Python bağımlılıklarını kurun
pip install -r requirements.txt

# 4. Geliştirme bağımlılıklarını kurun (opsiyonel)
pip install -r requirements-dev.txt

# 5. Node.js bağımlılıklarını kurun
npm install

# 6. Uygulamayı çalıştırın
python main.py
```

### Build İşlemi

```bash
# Tüm platformlar için build
python build.py --all

# Belirli platform için
python build.py --platform windows
python build.py --platform macos
python build.py --platform linux

# AppImage build
python build.py --appimage

# Portable build
python build.py --portable
```

---

## ✅ Kurulum Doğrulama

### 1. Uygulama Başlatma Testi

```bash
# Komut satırından başlatma
pypdf-tools --version

# GUI başlatma
pypdf-tools
```

### 2. OCR Testi

```bash
# OCR dil paketlerini kontrol et
pypdf-tools --list-ocr-languages

# OCR test dosyası
pypdf-tools --test-ocr
```

### 3. Sistem Bilgileri

```bash
# Sistem bilgilerini görüntüle
pypdf-tools --system-info
```

---

## 🆙 Güncelleme

### Otomatik Güncelleme

Uygulama içinden **Ayarlar → Güncellemeler** menüsünden otomatik güncelleme etkinleştirilebilir.

### Manuel Güncelleme

#### Linux (AppImage)
```bash
# Yeni AppImage'i indirin ve eskisini değiştirin
wget -O ~/Applications/PyPDF-Tools.AppImage https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage
chmod +x ~/Applications/PyPDF-Tools.AppImage
```

#### macOS (Homebrew)
```bash
brew upgrade pypdf-tools
```

#### Windows (Chocolatey)
```powershell
choco upgrade pypdf-tools
```

---

## 🗑️ Kaldırma

### Linux

#### AppImage
```bash
rm ~/Applications/PyPDF-Tools.AppImage
rm ~/.local/share/applications/pypdf-tools.desktop
```

#### DEB Paketi
```bash
sudo apt remove pypdf-tools
```

#### RPM Paketi
```bash
sudo dnf remove pypdf-tools  # Fedora
sudo zypper remove pypdf-tools  # openSUSE
```

### macOS

#### DMG Kurulumu
```bash
rm -rf "/Applications/PyPDF Tools v2.app"
```

#### Homebrew
```bash
brew uninstall --cask pypdf-tools
```

### Windows

#### MSI Kurulumu
- **Denetim Masası → Programlar ve Özellikler** → "PyPDF Tools v2" → Kaldır

#### Portable Sürüm
- Uygulama klasörünü silin

#### Chocolatey
```powershell
choco uninstall pypdf-tools
```

### Kullanıcı Verilerini Temizle

```bash
# Linux
rm -rf ~/.config/PyPDF\ Tools\ v2/
rm -rf ~/.cache/PyPDF\ Tools\ v2/

# macOS
rm -rf ~/Library/Application\ Support/PyPDF\ Tools\ v2/
rm -rf ~/Library/Caches/PyPDF\ Tools\ v2/

# Windows
rmdir /s "%APPDATA%\PyPDF Tools v2"
rmdir /s "%LOCALAPPDATA%\PyPDF Tools v2"
```

---

## 🆘 Kurulum Sorunları

Kurulum sorunları yaşıyorsanız [Troubleshooting](troubleshooting.md) belgesine bakın veya [GitHub Issues](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues) sayfasında yardım isteyin.

---

## 📞 Destek

- **GitHub Issues**: [https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues)
- **Discord**: [PyPDF Tools Community](https://discord.gg/pypdf-tools)
- **Email**: support@pypdf-tools.com
