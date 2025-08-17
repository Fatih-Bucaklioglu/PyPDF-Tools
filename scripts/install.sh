#!/bin/bash
# PyPDF-Tools Linux/macOS Kurulum Scripti
# Modern PDF İşleme Uygulaması

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emoji support check
if [[ "$LANG" =~ "UTF-8" ]]; then
    EMOJI_SUPPORT=true
else
    EMOJI_SUPPORT=false
fi

# İkonlar/Emojiler
if [[ "$EMOJI_SUPPORT" == true ]]; then
    ICON_SUCCESS="✅"
    ICON_ERROR="❌"
    ICON_WARNING="⚠️"
    ICON_INFO="ℹ️"
    ICON_ROCKET="🚀"
    ICON_PACKAGE="📦"
    ICON_DOWNLOAD="⬇️"
    ICON_INSTALL="🔧"
    ICON_CLEAN="🧹"
else
    ICON_SUCCESS="[OK]"
    ICON_ERROR="[ERROR]"
    ICON_WARNING="[WARNING]"
    ICON_INFO="[INFO]"
    ICON_ROCKET="[LAUNCH]"
    ICON_PACKAGE="[PACKAGE]"
    ICON_DOWNLOAD="[DOWNLOAD]"
    ICON_INSTALL="[INSTALL]"
    ICON_CLEAN="[CLEAN]"
fi

# Versiyon ve URL'ler
PYPDF_VERSION="2.0.0"
GITHUB_REPO="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools"
GITHUB_API="https://api.github.com/repos/Fatih-Bucaklioglu/PyPDF-Tools"
RELEASES_URL="${GITHUB_API}/releases/latest"

# Kurulum dizinleri
INSTALL_DIR="${HOME}/.local/share/PyPDF-Tools"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons"

# Sistem bilgilerini tespit et
detect_system() {
    echo -e "${BLUE}${ICON_INFO}${NC} Sistem bilgileri tespit ediliyor..."
    
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    case "$OS" in
        Linux*)
            SYSTEM="linux"
            ;;
        Darwin*)
            SYSTEM="macos"
            ;;
        *)
            echo -e "${RED}${ICON_ERROR}${NC} Desteklenmeyen işletim sistemi: $OS"
            exit 1
            ;;
    esac
    
    case "$ARCH" in
        x86_64|amd64)
            ARCHITECTURE="x64"
            ;;
        aarch64|arm64)
            ARCHITECTURE="arm64"
            ;;
        *)
            echo -e "${RED}${ICON_ERROR}${NC} Desteklenmeyen mimari: $ARCH"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Sistem: $SYSTEM ($ARCHITECTURE)"
}

# Gereksinimler kontrolü
check_requirements() {
    echo -e "${BLUE}${ICON_INFO}${NC} Sistem gereksinimleri kontrol ediliyor..."
    
    # Python kontrolü
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ "$PYTHON_MAJOR" -eq 3 ]] && [[ "$PYTHON_MINOR" -ge 8 ]]; then
            echo -e "${GREEN}${ICON_SUCCESS}${NC} Python $PYTHON_VERSION bulundu"
        else
            echo -e "${RED}${ICON_ERROR}${NC} Python 3.8+ gerekli, mevcut: $PYTHON_VERSION"
            exit 1
        fi
    else
        echo -e "${RED}${ICON_ERROR}${NC} Python3 bulunamadı!"
        echo -e "${YELLOW}${ICON_INFO}${NC} Lütfen Python 3.8+ yükleyin:"
        echo -e "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo -e "  CentOS/RHEL: sudo yum install python3 python3-pip"
        echo -e "  macOS: brew install python3"
        exit 1
    fi
    
    # pip kontrolü
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}${ICON_WARNING}${NC} pip3 bulunamadı, yükleniyor..."
        python3 -m ensurepip --upgrade
    fi
    
    # Sistem paketleri kontrol et (Linux için)
    if [[ "$SYSTEM" == "linux" ]]; then
        check_linux_packages
    elif [[ "$SYSTEM" == "macos" ]]; then
        check_macos_packages
    fi
}

check_linux_packages() {
    echo -e "${BLUE}${ICON_INFO}${NC} Linux sistem paketleri kontrol ediliyor..."
    
    # Distro tespiti
    if command -v apt &> /dev/null; then
        PACKAGE_MANAGER="apt"
        INSTALL_CMD="sudo apt update && sudo apt install -y"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        INSTALL_CMD="sudo yum install -y"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        INSTALL_CMD="sudo dnf install -y"
    elif command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
    else
        echo -e "${YELLOW}${ICON_WARNING}${NC} Bilinmeyen paket yöneticisi"
    fi
    
    # Tesseract OCR
    if ! command -v tesseract &> /dev/null; then
        echo -e "${YELLOW}${ICON_WARNING}${NC} Tesseract OCR bulunamadı"
        if [[ -n "$PACKAGE_MANAGER" ]]; then
            echo -e "${BLUE}${ICON_INSTALL}${NC} Tesseract OCR yükleniyor..."
            case "$PACKAGE_MANAGER" in
                apt)
                    $INSTALL_CMD tesseract-ocr tesseract-ocr-tur tesseract-ocr-eng
                    ;;
                yum|dnf)
                    $INSTALL_CMD tesseract tesseract-langpack-tur tesseract-langpack-eng
                    ;;
                pacman)
                    $INSTALL_CMD tesseract tesseract-data-tur tesseract-data-eng
                    ;;
            esac
        fi
    else
        echo -e "${GREEN}${ICON_SUCCESS}${NC} Tesseract OCR bulundu"
    fi
    
    # Qt6 bağımlılıkları
    case "$PACKAGE_MANAGER" in
        apt)
            REQUIRED_PACKAGES="python3-dev python3-venv libqt6gui6 libgl1-mesa-glx"
            ;;
        yum|dnf)
    # Qt6 bağımlılıkları
    case "$PACKAGE_MANAGER" in
        apt)
            REQUIRED_PACKAGES="python3-dev python3-venv libqt6gui6 libgl1-mesa-glx"
            ;;
        yum|dnf)
            REQUIRED_PACKAGES="python3-devel qt6-qtbase mesa-libGL"
            ;;
        pacman)
            REQUIRED_PACKAGES="python python-pip qt6-base mesa"
            ;;
    esac
    
    echo -e "${BLUE}${ICON_INSTALL}${NC} Sistem bağımlılıkları yükleniyor..."
    $INSTALL_CMD $REQUIRED_PACKAGES || echo -e "${YELLOW}${ICON_WARNING}${NC} Bazı paketler yüklenemedi, devam ediliyor..."
}

check_macos_packages() {
    echo -e "${BLUE}${ICON_INFO}${NC} macOS sistem paketleri kontrol ediliyor..."
    
    # Homebrew kontrolü
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}${ICON_WARNING}${NC} Homebrew bulunamadı"
        echo -e "${BLUE}${ICON_INFO}${NC} Homebrew yükleme bağlantısı: https://brew.sh"
        read -p "Homebrew olmadan devam edilsin mi? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}${ICON_SUCCESS}${NC} Homebrew bulundu"
        
        # Tesseract OCR
        if ! brew list tesseract &> /dev/null; then
            echo -e "${BLUE}${ICON_INSTALL}${NC} Tesseract OCR yükleniyor..."
            brew install tesseract tesseract-lang
        fi
        
        # Qt6
        if ! brew list qt6 &> /dev/null; then
            echo -e "${BLUE}${ICON_INSTALL}${NC} Qt6 yükleniyor..."
            brew install qt6
        fi
    fi
}

# En son sürümü indir
download_latest_release() {
    echo -e "${BLUE}${ICON_DOWNLOAD}${NC} En son sürüm bilgileri alınıyor..."
    
    # GitHub API'den en son release bilgisini al
    if command -v curl &> /dev/null; then
        LATEST_RELEASE=$(curl -s "$RELEASES_URL" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | head -1)
    elif command -v wget &> /dev/null; then
        LATEST_RELEASE=$(wget -qO- "$RELEASES_URL" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | head -1)
    else
        echo -e "${YELLOW}${ICON_WARNING}${NC} curl veya wget bulunamadı, varsayılan sürüm kullanılıyor"
        LATEST_RELEASE="v$PYPDF_VERSION"
    fi
    
    if [[ -z "$LATEST_RELEASE" ]]; then
        LATEST_RELEASE="v$PYPDF_VERSION"
    fi
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} En son sürüm: $LATEST_RELEASE"
    
    # Kurulum yöntemini belirle
    if [[ "$SYSTEM" == "linux" ]]; then
        download_appimage
    elif [[ "$SYSTEM" == "macos" ]]; then
        download_dmg
    fi
}

download_appimage() {
    echo -e "${BLUE}${ICON_DOWNLOAD}${NC} AppImage indiriliyor..."
    
    APPIMAGE_URL="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/download/$LATEST_RELEASE/PyPDF-Tools-$ARCHITECTURE.AppImage"
    APPIMAGE_FILE="$INSTALL_DIR/PyPDF-Tools.AppImage"
    
    # Kurulum dizinini oluştur
    mkdir -p "$INSTALL_DIR"
    
    # AppImage'ı indir
    if command -v curl &> /dev/null; then
        curl -L "$APPIMAGE_URL" -o "$APPIMAGE_FILE" || download_fallback
    elif command -v wget &> /dev/null; then
        wget "$APPIMAGE_URL" -O "$APPIMAGE_FILE" || download_fallback
    else
        download_fallback
    fi
    
    # AppImage'ı çalıştırılabilir yap
    chmod +x "$APPIMAGE_FILE"
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} AppImage indirildi: $APPIMAGE_FILE"
}

download_dmg() {
    echo -e "${BLUE}${ICON_DOWNLOAD}${NC} macOS DMG indiriliyor..."
    
    DMG_URL="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/releases/download/$LATEST_RELEASE/PyPDF-Tools.dmg"
    DMG_FILE="/tmp/PyPDF-Tools.dmg"
    
    # DMG'yi indir
    if command -v curl &> /dev/null; then
        curl -L "$DMG_URL" -o "$DMG_FILE" || download_fallback
    elif command -v wget &> /dev/null; then
        wget "$DMG_URL" -O "$DMG_FILE" || download_fallback
    else
        download_fallback
    fi
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} DMG indirildi: $DMG_FILE"
    
    # DMG'yi mount et ve kopyala
    echo -e "${BLUE}${ICON_INSTALL}${NC} Uygulama kuruluyor..."
    
    hdiutil attach "$DMG_FILE" -quiet
    
    # Applications klasörüne kopyala
    cp -R "/Volumes/PyPDF Tools/PyPDF Tools.app" "/Applications/"
    
    # DMG'yi çıkar
    hdiutil detach "/Volumes/PyPDF Tools" -quiet
    
    # Geçici dosyayı sil
    rm "$DMG_FILE"
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Uygulama /Applications/ klasörüne kuruldu"
}

download_fallback() {
    echo -e "${YELLOW}${ICON_WARNING}${NC} Binary indirilemedi, kaynak koddan kurulum yapılıyor..."
    install_from_source
}

# Kaynak koddan kurulum
install_from_source() {
    echo -e "${BLUE}${ICON_INSTALL}${NC} Kaynak koddan kurulum yapılıyor..."
    
    # Git kontrolü
    if ! command -v git &> /dev/null; then
        echo -e "${RED}${ICON_ERROR}${NC} Git bulunamadı!"
        case "$PACKAGE_MANAGER" in
            apt) sudo apt install -y git ;;
            yum|dnf) sudo $PACKAGE_MANAGER install -y git ;;
            pacman) sudo pacman -S --noconfirm git ;;
        esac
    fi
    
    # Repository'yi clone et
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
    fi
    
    git clone --depth 1 "$GITHUB_REPO.git" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Virtual environment oluştur
    echo -e "${BLUE}${ICON_INSTALL}${NC} Python virtual environment oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Bağımlılıkları yükle
    echo -e "${BLUE}${ICON_INSTALL}${NC} Python bağımlılıkları yükleniyor..."
    pip install --upgrade pip
    pip install -e .
    
    # Desktop entry oluştur
    create_desktop_entry_source
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Kaynak koddan kurulum tamamlandı"
}

# Desktop entry oluştur (AppImage için)
create_desktop_entry() {
    echo -e "${BLUE}${ICON_INSTALL}${NC} Masaüstü entegrasyonu yapılıyor..."
    
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICON_DIR"
    mkdir -p "$BIN_DIR"
    
    # İkonu kopyala
    ICON_PATH="$ICON_DIR/pypdf-tools.png"
    if [[ -f "$INSTALL_DIR/icons/app_icon.png" ]]; then
        cp "$INSTALL_DIR/icons/app_icon.png" "$ICON_PATH"
    fi
    
    # Desktop entry dosyası
    cat > "$DESKTOP_DIR/pypdf-tools.desktop" << EOF
[Desktop Entry]
Type=Application
Name=PyPDF-Tools
Comment=Modern PDF Processing Application
Exec=$INSTALL_DIR/PyPDF-Tools.AppImage %F
Icon=$ICON_PATH
StartupWMClass=PyPDF-Tools
MimeType=application/pdf;
Categories=Office;Graphics;
Keywords=PDF;merge;split;compress;OCR;convert;
StartupNotify=true
EOF
    
    # Masaüstü dosyasını çalıştırılabilir yap
    chmod +x "$DESKTOP_DIR/pypdf-tools.desktop"
    
    # Komut satırı link'i oluştur
    cat > "$BIN_DIR/pypdf-tools" << EOF
#!/bin/bash
exec "$INSTALL_DIR/PyPDF-Tools.AppImage" "\$@"
EOF
    chmod +x "$BIN_DIR/pypdf-tools"
    
    # CLI link'i
    cat > "$BIN_DIR/pypdf-cli" << EOF
#!/bin/bash
exec "$INSTALL_DIR/PyPDF-Tools.AppImage" --cli "\$@"
EOF
    chmod +x "$BIN_DIR/pypdf-cli"
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Masaüstü entegrasyonu tamamlandı"
}

# Desktop entry oluştur (kaynak kod için)
create_desktop_entry_source() {
    echo -e "${BLUE}${ICON_INSTALL}${NC} Masaüstü entegrasyonu yapılıyor..."
    
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICON_DIR"
    mkdir -p "$BIN_DIR"
    
    # İkonu kopyala
    ICON_PATH="$ICON_DIR/pypdf-tools.png"
    if [[ -f "$INSTALL_DIR/icons/app_icon.png" ]]; then
        cp "$INSTALL_DIR/icons/app_icon.png" "$ICON_PATH"
    fi
    
    # Desktop entry dosyası
    cat > "$DESKTOP_DIR/pypdf-tools.desktop" << EOF
[Desktop Entry]
Type=Application
Name=PyPDF-Tools
Comment=Modern PDF Processing Application
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/src/pypdf_tools/main.py %F
Icon=$ICON_PATH
StartupWMClass=PyPDF-Tools
MimeType=application/pdf;
Categories=Office;Graphics;
Keywords=PDF;merge;split;compress;OCR;convert;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_DIR/pypdf-tools.desktop"
    
    # Komut satırı link'leri
    cat > "$BIN_DIR/pypdf-tools" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
exec ./venv/bin/python -m pypdf_tools.main "\$@"
EOF
    chmod +x "$BIN_DIR/pypdf-tools"
    
    cat > "$BIN_DIR/pypdf-cli" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
exec ./venv/bin/python -m pypdf_tools.cli.cli_handler "\$@"
EOF
    chmod +x "$BIN_DIR/pypdf-cli"
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Masaüstü entegrasyonu tamamlandı"
}

# PATH'i güncelle
update_path() {
    echo -e "${BLUE}${ICON_INFO}${NC} PATH yapılandırması kontrol ediliyor..."
    
    SHELL_RC=""
    if [[ "$SHELL" =~ bash ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ "$SHELL" =~ zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" =~ fish ]]; then
        SHELL_RC="$HOME/.config/fish/config.fish"
        echo 'set -gx PATH '"$BIN_DIR"' $PATH' >> "$SHELL_RC"
        echo -e "${GREEN}${ICON_SUCCESS}${NC} Fish shell PATH güncellendi"
        return
    fi
    
    if [[ -n "$SHELL_RC" ]] && [[ -f "$SHELL_RC" ]]; then
        if ! grep -q "$BIN_DIR" "$SHELL_RC"; then
            echo '' >> "$SHELL_RC"
            echo '# PyPDF-Tools PATH' >> "$SHELL_RC"
            echo 'export PATH="'"$BIN_DIR"':$PATH"' >> "$SHELL_RC"
            echo -e "${GREEN}${ICON_SUCCESS}${NC} PATH güncellendi ($SHELL_RC)"
            echo -e "${YELLOW}${ICON_INFO}${NC} Değişikliklerin geçerli olması için shell'i yeniden başlatın veya:"
            echo -e "  source $SHELL_RC"
        else
            echo -e "${GREEN}${ICON_SUCCESS}${NC} PATH zaten yapılandırılmış"
        fi
    fi
}

# Kurulum sonrası temizlik
cleanup() {
    echo -e "${BLUE}${ICON_CLEAN}${NC} Kurulum sonrası temizlik yapılıyor..."
    
    # Geçici dosyaları sil
    if [[ -f "/tmp/PyPDF-Tools.dmg" ]]; then
        rm "/tmp/PyPDF-Tools.dmg"
    fi
    
    # Desktop veritabanını güncelle (Linux)
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} Temizlik tamamlandı"
}

# Başarı mesajı
show_success() {
    echo
    echo -e "${GREEN}${ICON_SUCCESS}${NC} ${WHITE}PyPDF-Tools v$LATEST_RELEASE başarıyla kuruldu!${NC}"
    echo
    echo -e "${CYAN}${ICON_ROCKET}${NC} ${WHITE}Nasıl Başlatılır:${NC}"
    echo -e "  GUI Modu     : ${YELLOW}pypdf-tools${NC}"
    echo -e "  CLI Modu     : ${YELLOW}pypdf-cli --help${NC}"
    echo -e "  Uygulama Menüsü: Ofis > PyPDF-Tools"
    echo
    echo -e "${PURPLE}${ICON_INFO}${NC} ${WHITE}Bağlantılar:${NC}"
    echo -e "  GitHub       : $GITHUB_REPO"
    echo -e "  Dokümantasyon: https://pypdf-tools.readthedocs.io/"
    echo -e "  Discord      : https://discord.gg/pypdf-tools"
    echo
    echo -e "${BLUE}${ICON_INFO}${NC} ${WHITE}İlk kez kullanıyorsanız kurulum sihirbazı otomatik açılacak.${NC}"
    echo
}

# Hata yakalama
trap 'echo -e "\n${RED}${ICON_ERROR}${NC} Kurulum iptal edildi"; exit 1' INT TERM

# Ana kurulum fonksiyonu
main() {
    echo -e "${PURPLE}${ICON_ROCKET}${NC} ${WHITE}PyPDF-Tools v$PYPDF_VERSION Kurulum${NC}"
    echo -e "${CYAN}Modern, Güçlü ve Kullanıcı Dostu PDF İşleme Uygulaması${NC}"
    echo "=================================================="
    echo
    
    # Sistem tespiti
    detect_system
    
    # Gereksinimler kontrolü
    check_requirements
    
    # En son sürümü indir ve kur
    download_latest_release
    
    # Desktop entegrasyonu (sadece AppImage veya kaynak kod için)
    if [[ "$SYSTEM" == "linux" ]]; then
        if [[ -f "$INSTALL_DIR/PyPDF-Tools.AppImage" ]]; then
            create_desktop_entry
        fi
    fi
    
    # PATH'i güncelle
    update_path
    
    # Temizlik
    cleanup
    
    # Başarı mesajı
    show_success
}

# Kaldırma fonksiyonu
uninstall() {
    echo -e "${YELLOW}${ICON_WARNING}${NC} PyPDF-Tools kaldırılıyor..."
    
    # Kurulum dizinini sil
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}${ICON_SUCCESS}${NC} Kurulum dizini silindi"
    fi
    
    # Desktop entry'yi sil
    if [[ -f "$DESKTOP_DIR/pypdf-tools.desktop" ]]; then
        rm "$DESKTOP_DIR/pypdf-tools.desktop"
        echo -e "${GREEN}${ICON_SUCCESS}${NC} Masaüstü kısayolu silindi"
    fi
    
    # İkonu sil
    if [[ -f "$ICON_DIR/pypdf-tools.png" ]]; then
        rm "$ICON_DIR/pypdf-tools.png"
        echo -e "${GREEN}${ICON_SUCCESS}${NC} İkon silindi"
    fi
    
    # Komut satırı link'lerini sil
    [[ -f "$BIN_DIR/pypdf-tools" ]] && rm "$BIN_DIR/pypdf-tools"
    [[ -f "$BIN_DIR/pypdf-cli" ]] && rm "$BIN_DIR/pypdf-cli"
    
    # macOS Application'ı sil
    if [[ -d "/Applications/PyPDF Tools.app" ]]; then
        rm -rf "/Applications/PyPDF Tools.app"
        echo -e "${GREEN}${ICON_SUCCESS}${NC} macOS uygulaması silindi"
    fi
    
    echo -e "${GREEN}${ICON_SUCCESS}${NC} PyPDF-Tools başarıyla kaldırıldı"
}

# Komut satırı argümanları
case "${1:-}" in
    --uninstall|-u)
        uninstall
        ;;
    --help|-h)
        echo "PyPDF-Tools Kurulum Scripti"
        echo
        echo "Kullanım:"
        echo "  $0           # Normal kurulum"
        echo "  $0 --uninstall   # Kaldır"
        echo "  $0 --help        # Bu yardımı göster"
        ;;
    *)
        main
        ;;
esac
