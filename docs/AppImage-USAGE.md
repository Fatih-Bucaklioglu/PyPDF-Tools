# 📦 PyPDF-Tools v2 AppImage Kullanım Kılavuzu

AppImage formatında PyPDF-Tools v2 kullanımı için detaylı rehber.

## 🎯 AppImage Nedir?

AppImage, Linux sistemlerde tek dosyada taşınabilir uygulama formatıdır. Sistem yöneticisi yetkisi gerektirmeden herhangi bir Linux dağıtımında çalışır.

### ✅ Avantajları
- **Taşınabilir**: Tek dosya, her yerde çalışır
- **Bağımlılık yok**: Tüm gereksinimler dahili
- **Sistem değişikliği yok**: Kurulum gerektirmez
- **Güvenli**: Sandbox içinde çalışır
- **Güncellenebilir**: Otomatik güncelleme desteği

---

## 🚀 Hızlı Başlangıç

### 1. İndirme

```bash
# En son sürümü indir
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage

# Belirli sürümü indir (örnek v2.0.0)
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/download/v2.0.0/PyPDF-Tools.AppImage
```

### 2. Çalıştırılabilir Yapma

```bash
chmod +x PyPDF-Tools.AppImage
```

### 3. Çalıştırma

```bash
./PyPDF-Tools.AppImage
```

---

## 🔧 Kurulum ve Konfigürasyon

### Sistem Genelinde Kurulum

#### 1. Applications Dizinine Taşı

```bash
# Kullanıcı Applications dizini oluştur
mkdir -p ~/Applications

# AppImage'i taşı
mv PyPDF-Tools.AppImage ~/Applications/

# Çalıştırılabilir yap
chmod +x ~/Applications/PyPDF-Tools.AppImage
```

#### 2. Desktop Entry Oluştur

```bash
# Desktop entry dosyası oluştur
cat > ~/.local/share/applications/pypdf-tools.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PyPDF Tools v2
Comment=Modern PDF İşleme Uygulaması
Exec=/home/$USER/Applications/PyPDF-Tools.AppImage
Icon=pypdf-tools
Terminal=false
Categories=Office;Graphics;Publishing;
MimeType=application/pdf;
StartupWMClass=PyPDF-Tools
StartupNotify=true
EOF

# Desktop veritabanını güncelle
update-desktop-database ~/.local/share/applications/
```

#### 3. İkon Kurulumu

```bash
# İkonu çıkart
~/Applications/PyPDF-Tools.AppImage --appimage-extract usr/share/icons/hicolor/256x256/apps/pypdf-tools.png

# İkon dizinini oluştur
mkdir -p ~/.local/share/icons/hicolor/256x256/apps/

# İkonu kopyala
cp squashfs-root/usr/share/icons/hicolor/256x256/apps/pypdf-tools.png ~/.local/share/icons/hicolor/256x256/apps/

# İkon cache'ini güncelle
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

### PATH'e Ekleme

```bash
# Symbolic link oluştur
sudo ln -sf ~/Applications/PyPDF-Tools.AppImage /usr/local/bin/pypdf-tools

# veya .bashrc/.zshrc'ye ekle
echo 'alias pypdf-tools="~/Applications/PyPDF-Tools.AppImage"' >> ~/.bashrc
source ~/.bashrc

# Artık terminal'den çalıştırabilirsiniz:
pypdf-tools
```

---

## 🛠️ AppImage Özel Özellikler

### Komut Satırı Parametreleri

```bash
# Yardım
./PyPDF-Tools.AppImage --help

# Sürüm bilgisi
./PyPDF-Tools.AppImage --version

# AppImage bilgisi
./PyPDF-Tools.AppImage --appimage-help

# Sistem bilgisi
./PyPDF-Tools.AppImage --system-info

# Debug modu
./PyPDF-Tools.AppImage --debug --verbose
```

### AppImage Özel Komutları

```bash
# AppImage içeriğini çıkart
./PyPDF-Tools.AppImage --appimage-extract

# AppImage mount et (okuma amaçlı)
./PyPDF-Tools.AppImage --appimage-mount

# AppImage signature doğrula
./PyPDF-Tools.AppImage --appimage-signature

# AppImage bilgilerini göster
./PyPDF-Tools.AppImage --appimage-offset
```

### Güncelleme

```bash
# Güncelleme kontrol et
./PyPDF-Tools.AppImage --check-update

# Otomatik güncelleme (varsa)
./PyPDF-Tools.AppImage --update

# Manuel güncelleme
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage -O PyPDF-Tools.AppImage.new
chmod +x PyPDF-Tools.AppImage.new
mv PyPDF-Tools.AppImage.new PyPDF-Tools.AppImage
```

---

## 🖥️ Desktop Entegrasyonu

### Otomatik Entegrasyon

```bash
# AppImageLauncher kullanıyorsanız
# AppImage'i çift tıklayın ve "Integrate and run" seçin

# Manuel entegrasyon
./PyPDF-Tools.AppImage --appimage-integrate

# Entegrasyonu kaldır
./PyPDF-Tools.AppImage --appimage-disintegrate
```

### MIME Type Kayıt

```bash
# PDF dosyaları için varsayılan uygulama yap
xdg-mime default pypdf-tools.desktop application/pdf

# MIME cache güncelle
update-mime-database ~/.local/share/mime/
```

### Nautilus (Dosya Yöneticisi) Entegrasyonu

```bash
# Sağ tık menüsü için script oluştur
mkdir -p ~/.local/share/nautilus/scripts/

cat > ~/.local/share/nautilus/scripts/PyPDF-Tools << 'EOF'
#!/bin/bash
# Seçili dosyaları PyPDF-Tools ile aç
~/Applications/PyPDF-Tools.AppImage "$@"
EOF

chmod +x ~/.local/share/nautilus/scripts/PyPDF-Tools
```

---

## 🐧 Dağıtım Özel Kurulum

# 📦 PyPDF-Tools v2 AppImage Kullanım Kılavuzu

AppImage formatında PyPDF-Tools v2 kullanımı için detaylı rehber.

## 🎯 AppImage Nedir?

AppImage, Linux sistemlerde tek dosyada taşınabilir uygulama formatıdır. Sistem yöneticisi yetkisi gerektirmeden herhangi bir Linux dağıtımında çalışır.

### ✅ Avantajları
- **Taşınabilir**: Tek dosya, her yerde çalışır
- **Bağımlılık yok**: Tüm gereksinimler dahili
- **Sistem değişikliği yok**: Kurulum gerektirmez
- **Güvenli**: Sandbox içinde çalışır
- **Güncellenebilir**: Otomatik güncelleme desteği

---

## 🚀 Hızlı Başlangıç

### 1. İndirme

```bash
# En son sürümü indir
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage

# Belirli sürümü indir (örnek v2.0.0)
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/download/v2.0.0/PyPDF-Tools.AppImage
```

### 2. Çalıştırılabilir Yapma

```bash
chmod +x PyPDF-Tools.AppImage
```

### 3. Çalıştırma

```bash
./PyPDF-Tools.AppImage
```

---

## 🔧 Kurulum ve Konfigürasyon

### Sistem Genelinde Kurulum

#### 1. Applications Dizinine Taşı

```bash
# Kullanıcı Applications dizini oluştur
mkdir -p ~/Applications

# AppImage'i taşı
mv PyPDF-Tools.AppImage ~/Applications/

# Çalıştırılabilir yap
chmod +x ~/Applications/PyPDF-Tools.AppImage
```

#### 2. Desktop Entry Oluştur

```bash
# Desktop entry dosyası oluştur
cat > ~/.local/share/applications/pypdf-tools.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PyPDF Tools v2
Comment=Modern PDF İşleme Uygulaması
Exec=/home/$USER/Applications/PyPDF-Tools.AppImage
Icon=pypdf-tools
Terminal=false
Categories=Office;Graphics;Publishing;
MimeType=application/pdf;
StartupWMClass=PyPDF-Tools
StartupNotify=true
EOF

# Desktop veritabanını güncelle
update-desktop-database ~/.local/share/applications/
```

#### 3. İkon Kurulumu

```bash
# İkonu çıkart
~/Applications/PyPDF-Tools.AppImage --appimage-extract usr/share/icons/hicolor/256x256/apps/pypdf-tools.png

# İkon dizinini oluştur
mkdir -p ~/.local/share/icons/hicolor/256x256/apps/

# İkonu kopyala
cp squashfs-root/usr/share/icons/hicolor/256x256/apps/pypdf-tools.png ~/.local/share/icons/hicolor/256x256/apps/

# İkon cache'ini güncelle
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

### PATH'e Ekleme

```bash
# Symbolic link oluştur
sudo ln -sf ~/Applications/PyPDF-Tools.AppImage /usr/local/bin/pypdf-tools

# veya .bashrc/.zshrc'ye ekle
echo 'alias pypdf-tools="~/Applications/PyPDF-Tools.AppImage"' >> ~/.bashrc
source ~/.bashrc

# Artık terminal'den çalıştırabilirsiniz:
pypdf-tools
```

---

## 🛠️ AppImage Özel Özellikler

### Komut Satırı Parametreleri

```bash
# Yardım
./PyPDF-Tools.AppImage --help

# Sürüm bilgisi
./PyPDF-Tools.AppImage --version

# AppImage bilgisi
./PyPDF-Tools.AppImage --appimage-help

# Sistem bilgisi
./PyPDF-Tools.AppImage --system-info

# Debug modu
./PyPDF-Tools.AppImage --debug --verbose
```

### AppImage Özel Komutları

```bash
# AppImage içeriğini çıkart
./PyPDF-Tools.AppImage --appimage-extract

# AppImage mount et (okuma amaçlı)
./PyPDF-Tools.AppImage --appimage-mount

# AppImage signature doğrula
./PyPDF-Tools.AppImage --appimage-signature

# AppImage bilgilerini göster
./PyPDF-Tools.AppImage --appimage-offset
```

### Güncelleme

```bash
# Güncelleme kontrol et
./PyPDF-Tools.AppImage --check-update

# Otomatik güncelleme (varsa)
./PyPDF-Tools.AppImage --update

# Manuel güncelleme
wget https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/latest/download/PyPDF-Tools.AppImage -O PyPDF-Tools.AppImage.new
chmod +x PyPDF-Tools.AppImage.new
mv PyPDF-Tools.AppImage.new PyPDF-Tools.AppImage
```

---

## 🖥️ Desktop Entegrasyonu

### Otomatik Entegrasyon

```bash
# AppImageLauncher kullanıyorsanız
# AppImage'i çift tıklayın ve "Integrate and run" seçin

# Manuel entegrasyon
./PyPDF-Tools.AppImage --appimage-integrate

# Entegrasyonu kaldır
./PyPDF-Tools.AppImage --appimage-disintegrate
```

### MIME Type Kayıt

```bash
# PDF dosyaları için varsayılan uygulama yap
xdg-mime default pypdf-tools.desktop application/pdf

# MIME cache güncelle
update-mime-database ~/.local/share/mime/
```

### Nautilus (Dosya Yöneticisi) Entegrasyonu

```bash
# Sağ tık menüsü için script oluştur
mkdir -p ~/.local/share/nautilus/scripts/

cat > ~/.local/share/nautilus/scripts/PyPDF-Tools << 'EOF'
#!/bin/bash
# Seçili dosyaları PyPDF-Tools ile aç
~/Applications/PyPDF-Tools.AppImage "$@"
EOF

chmod +x ~/.local/share/nautilus/scripts/PyPDF-Tools
```

---

## 🐧 Dağıtım Özel Kurulum

### Ubuntu/Debian

```bash
# Gerekli bağımlılıklar
sudo apt install libfuse2 libnss3 libatk-bridge2.0-0 libdrm2 libgtk-3-0

# AppImage çalıştır
./PyPDF-Tools.AppImage
```

### Fedora/CentOS/RHEL

```bash
# FUSE kurulumu
sudo dnf install fuse fuse-libs

# Eski sistemlerde
sudo yum install fuse fuse-libs

# AppImage çalıştır
./PyPDF-Tools.AppImage
```

### openSUSE

```bash
# FUSE kurulumu
sudo zypper install fuse libfuse2

# AppImage çalıştır
./PyPDF-Tools.AppImage
```

### Arch Linux

```bash
# FUSE kurulumu
sudo pacman -S fuse2

# AUR'dan AppImageLauncher (opsiyonel)
yay -S appimagelauncher

# AppImage çalıştır
./PyPDF-Tools.AppImage
```

---

## 🔧 Sorun Giderme

### Problem: "FUSE not available" Hatası

**Çözüm:**
```bash
# FUSE kurulumu
# Ubuntu/Debian:
sudo apt install fuse libfuse2

# Fedora:
sudo dnf install fuse fuse-libs

# Arch:
sudo pacman -S fuse2

# FUSE modülünü yükle
sudo modprobe fuse

# Kullanıcıyı fuse grubuna ekle
sudo usermod -a -G fuse $USER
# Oturumu kapatıp yeniden açın
```

### Problem: "Permission denied" Hatası

**Çözüm:**
```bash
# Çalıştırma izni ver
chmod +x PyPDF-Tools.AppImage

# Dosya sahipliğini kontrol et
ls -la PyPDF-Tools.AppImage

# Gerekirse sahipliği değiştir
chown $USER:$USER PyPDF-Tools.AppImage
```

### Problem: "No such file or directory" (32-bit sistem)

**Çözüm:**
```bash
# 64-bit sistemde 32-bit uyumluluk
# Ubuntu/Debian:
sudo apt install libc6-i386

# Fedora:
sudo dnf install glibc.i686

# Bu AppImage sadece 64-bit sistemlerde çalışır
uname -m  # x86_64 olmalı
```

### Problem: AppImage Çalışmıyor

**Tanılama:**
```bash
# FUSE kontrol
which fusermount
lsmod | grep fuse

# Bağımlılık kontrol
ldd PyPDF-Tools.AppImage

# Verbose çalıştırma
./PyPDF-Tools.AppImage --appimage-verbose

# Manuel çıkartma ve çalıştırma
./PyPDF-Tools.AppImage --appimage-extract-and-run
```

### Problem: Desktop Entegrasyonu Çalışmıyor

**Çözüm:**
```bash
# Desktop dosyasını kontrol et
desktop-file-validate ~/.local/share/applications/pypdf-tools.desktop

# İzinleri düzelt
chmod 644 ~/.local/share/applications/pypdf-tools.desktop

# Cache'i temizle ve yenile
update-desktop-database ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor/

# DE restart (veya relogin)
```

---

## 🚀 İleri Düzey Kullanım

### Komut Satırı Entegrasyonu

```bash
# Batch işlemler için wrapper script
cat > ~/bin/pypdf-batch << 'EOF'
#!/bin/bash
# PyPDF-Tools batch wrapper

APPIMAGE="$HOME/Applications/PyPDF-Tools.AppImage"

case "$1" in
    merge)
        shift
        $APPIMAGE merge "$@"
        ;;
    split)
        shift  
        $APPIMAGE split "$@"
        ;;
    compress)
        shift
        $APPIMAGE compress "$@"
        ;;
    ocr)
        shift
        $APPIMAGE ocr "$@"
        ;;
    *)
        echo "Usage: pypdf-batch {merge|split|compress|ocr} [args...]"
        exit 1
        ;;
esac
EOF

chmod +x ~/bin/pypdf-batch

# Kullanım
pypdf-batch merge file1.pdf file2.pdf -o merged.pdf
pypdf-batch compress large.pdf -q medium
```

### Otomasyon Scriptleri

```bash
# Klasör izleme scripti
cat > ~/.local/bin/pypdf-watch << 'EOF'
#!/bin/bash
# PyPDF-Tools ile klasör izleme

WATCH_DIR="${1:-$HOME/Downloads}"
APPIMAGE="$HOME/Applications/PyPDF-Tools.AppImage"

echo "Watching $WATCH_DIR for PDF files..."

inotifywait -m -e create --format '%f' "$WATCH_DIR" | while read filename; do
    if [[ "$filename" == *.pdf ]]; then
        echo "Processing new PDF: $filename"
        $APPIMAGE compress "$WATCH_DIR/$filename" -q medium
        echo "Compression completed: $filename"
    fi
done
EOF

chmod +x ~/.local/bin/pypdf-watch

# Kullanım
pypdf-watch ~/Downloads
```

### Cron ile Otomatik İşlem

```bash
# Crontab'a ekle
crontab -e

# Her gece saat 02:00'da Downloads klasörünü temizle ve sıkıştır
0 2 * * * /home/$USER/Applications/PyPDF-Tools.AppImage batch compress ~/Downloads/*.pdf --output-dir ~/Documents/Compressed/
```

---

## 🔒 Güvenlik

### AppImage Doğrulama

```bash
# SHA256 hash kontrol et
sha256sum PyPDF-Tools.AppImage

# GPG imzası kontrol et (varsa)
gpg --verify PyPDF-Tools.AppImage.sig PyPDF-Tools.AppImage

# VirusTotal kontrol et
curl -s -X POST 'https://www.virustotal.com/vtapi/v2/file/scan' \
  --form apikey=YOUR_API_KEY \
  --form file=@PyPDF-Tools.AppImage
```

### Sandboxing

```bash
# Firejail ile sandboxed çalıştırma
firejail --apparmor PyPDF-Tools.AppImage

# Bubblewrap ile izolasyon
bwrap --ro-bind / / --dev /dev --proc /proc --tmpfs /tmp \
  --unshare-all --share-net \
  PyPDF-Tools.AppImage
```

---

## 📦 AppImage Yönetimi

### Çoklu Sürüm

```bash
# Sürüm klasörü oluştur
mkdir -p ~/Applications/PyPDF-Tools/

# Sürümleri ayrı saklama
mv PyPDF-Tools.AppImage ~/Applications/PyPDF-Tools/PyPDF-Tools-v2.0.0.AppImage
ln -sf ~/Applications/PyPDF-Tools/PyPDF-Tools-v2.0.0.AppImage ~/Applications/PyPDF-Tools.AppImage

# Sürüm değiştirme scripti
cat > ~/.local/bin/pypdf-version << 'EOF'
#!/bin/bash
# PyPDF-Tools sürüm değiştirici

VERSION_DIR="$HOME/Applications/PyPDF-Tools"
CURRENT_LINK="$HOME/Applications/PyPDF-Tools.AppImage"

case "$1" in
    list)
        echo "Available versions:"
        ls -1 "$VERSION_DIR"/PyPDF-Tools-v*.AppImage | sed 's/.*PyPDF-Tools-v\(.*\)\.AppImage/\1/'
        ;;
    switch)
        if [[ -f "$VERSION_DIR/PyPDF-Tools-v$2.AppImage" ]]; then
            ln -sf "$VERSION_DIR/PyPDF-Tools-v$2.AppImage" "$CURRENT_LINK"
            echo "Switched to version $2"
        else
            echo "Version $2 not found"
            exit 1
        fi
        ;;
    current)
        if [[ -L "$CURRENT_LINK" ]]; then
            readlink "$CURRENT_LINK" | sed 's/.*PyPDF-Tools-v\(.*\)\.AppImage/\1/'
        else
            echo "No version symlink found"
        fi
        ;;
    *)
        echo "Usage: pypdf-version {list|switch VERSION|current}"
        exit 1
        ;;
esac
EOF

chmod +x ~/.local/bin/pypdf-version
```

### Temizlik ve Bakım

```bash
# AppImage cache temizleme
rm -rf ~/.cache/PyPDF-Tools/
rm -rf /tmp/appimage_*

# Eski sürümleri temizle
find ~/Applications/PyPDF-Tools/ -name "PyPDF-Tools-v*.AppImage" -type f -mtime +30 -delete

# Desktop integration temizleme
./PyPDF-Tools.AppImage --appimage-disintegrate
```

---

## 📊 Performans Optimizasyonu

### RAM Disk Kullanımı

```bash
# RAM disk oluştur (geçici dosyalar için)
sudo mkdir -p /mnt/ramdisk
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk

# PyPDF-Tools'u RAM disk ile çalıştır
TMPDIR=/mnt/ramdisk ./PyPDF-Tools.AppImage
```

### Parallel İşlem

```bash
# Çoklu dosya işleme
find ~/Documents -name "*.pdf" -print0 | \
  xargs -0 -n1 -P$(nproc) -I{} \
  ~/Applications/PyPDF-Tools.AppImage compress {} -q medium
```

---

## 🌐 Network Kurulumu

### Merkezi Dağıtım

```bash
# Web sunucusundan AppImage indir
wget https://your-domain.com/apps/PyPDF-Tools.AppImage

# NFS paylaşımından kullan
sudo mount -t nfs server:/path/to/apps /mnt/apps
/mnt/apps/PyPDF-Tools.AppImage

# Network drive'dan çalıştır (dikkat: yavaş olabilir)
```

### Corporate Environment

```bash
# Proxy ayarları
export http_proxy=http://proxy.company.com:8080
export https_proxy=https://proxy.company.com:8080

# SSL sertifika ayarları
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# AppImage çalıştır
./PyPDF-Tools.AppImage
```

---

## 🆘 Acil Durum ve Kurtarma

### Manual Extraction

```bash
# AppImage bozulduğunda içeriği çıkart
./PyPDF-Tools.AppImage --appimage-extract

# Direkt Python ile çalıştır
cd squashfs-root/
python3 usr/bin/pypdf-tools
```

### Backup ve Restore

```bash
# Konfigürasyonu yedekle
tar czf pypdf-backup-$(date +%Y%m%d).tar.gz \
  ~/.config/PyPDF\ Tools\ v2/ \
  ~/.local/share/applications/pypdf-tools.desktop \
  ~/Applications/PyPDF-Tools.AppImage

# Restore
tar xzf pypdf-backup-20240115.tar.gz -C ~/
```

---

## 🔍 Debugging ve Log Analizi

### Debug Modu

```bash
# Verbose logging ile çalıştır
DEBUG=1 ./PyPDF-Tools.AppImage --verbose

# Strace ile sistem çağrılarını izle
strace -e trace=file ./PyPDF-Tools.AppImage

# Log dosyalarını takip et
tail -f ~/.config/PyPDF\ Tools\ v2/logs/app.log
```

### Performance Profiling

```bash
# Zaman ölçümü
time ./PyPDF-Tools.AppImage compress large.pdf -q medium

# Memory usage
/usr/bin/time -v ./PyPDF-Tools.AppImage compress large.pdf -q medium

# CPU profiling
perf record -g ./PyPDF-Tools.AppImage compress large.pdf
perf report
```

---

Bu AppImage kılavuzu, PyPDF-Tools v2'yi Linux sistemlerde verimli bir şekilde kullanmanız için hazırlanmıştır. Sorularınız için GitHub Issues sayfasını kullanabilirsiniz.
