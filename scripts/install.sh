#!/bin/bash

# PyPDF-Stirling Tools v2 - Otomatik Kurulum Scripti
# Linux ve macOS için tek komutla kurulum
# Kullanım: curl -sSL https://raw.githubusercontent.com/Fatih-Bucaklioglu/PyPDF-Tools-v2/main/install.sh | bash

set -e

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Unicode karakterler
CHECK_MARK="✅"
CROSS_MARK="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"

APP_NAME="PyPDF-Stirling Tools v2"
APP_VERSION="2.0.0"
REPO_URL="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools-v2"
INSTALL_DIR="$HOME/.local/share/pypdf-tools-v2"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo -e "${BLUE}${ROCKET} ${APP_NAME} Kurulum Scripti${NC}"
echo -e "${CYAN}Sürüm: ${APP_VERSION}${NC}"
echo -e "${CYAN}Repository: ${REPO_URL}${NC}"
echo ""

# Sistem bilgilerini tespit et
detect_system() {
    echo -e "${INFO} Sistem bilgileri tespit ediliyor..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v lsb_release &> /dev/null; then
            DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
            VERSION=$(lsb_release -sr)
        elif [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
            VERSION="$VERSION_ID"
        else
            DISTRO="unknown"
            VERSION="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
        VERSION=$(sw_vers -productVersion)
    else
        echo -e "${RED}${CROSS_MARK} Desteklenmeyen işletim sistemi: $OSTYPE${NC}"
        exit 1
    fi

    echo -e "${GREEN}${CHECK_MARK} Sistem: $OS ($DISTRO $VERSION)${NC}"
}

# Python kurulumu kontrolü
check_python() {
    echo -e "${INFO} Python kurulumu kontrol ediliyor..."

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}${CROSS_MARK} Python bulunamadı!${NC}"
        install_python
        return
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
    REQUIRED_VERSION="3.8"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        echo -e "${GREEN}${CHECK_MARK} Python $PYTHON_VERSION bulundu${NC}"
    else
        echo -e "${RED}${CROSS_MARK} Python $PYTHON_VERSION çok eski! (Minimum: $REQUIRED_VERSION gerekli)${NC}"
        install_python
    fi
}

# Python kurulumu
install_python() {
    echo -e "${GEAR} Python kuruluyor..."

    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-tk
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip python3-tkinter
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip python3-tkinter
        elif command -v pacman &> /dev/null; then
            sudo pacman -S python python-pip tk
        else
            echo -e "${RED}${CROSS_MARK} Paket yöneticisi bulunamadı!${NC}"
            echo "Lütfen Python 3.8+ sürümünü manuel olarak kurun."
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install python-tk
        else
            echo -e "${YELLOW}${WARNING} Homebrew bulunamadı!${NC}"
            echo "Python kurulumu için Homebrew kullanmanız önerilir:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  brew install python-tk"
            exit 1
        fi
    fi

    # Tekrar kontrol et
    check_python
}

# Sistem bağımlılıklarını kur
install_system_dependencies() {
    echo -e "${GEAR} Sistem bağımlılıkları kuruluyor..."

    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                tesseract-ocr \
                tesseract-ocr-tur \
                tesseract-ocr-eng \
                poppler-utils \
                libgl1-mesa-glx \
                libglib2.0-0 \
                libsm6 \
                libxext6 \
                libfontconfig1 \
                libxrender1 \
                curl \
                wget \
                git

        elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
            PKG_MGR="yum"
            command -v dnf &> /dev/null && PKG_MGR="dnf"

            sudo $PKG_MGR install -y \
                tesseract \
                tesseract-langpack-tur \
                tesseract-langpack-eng \
                poppler-utils \
                mesa-libGL \
                glib2 \
                libSM \
                libXext \
                fontconfig \
                libXrender \
                curl \
                wget \
                git

        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm \
                tesseract \
                tesseract-data-tur \
                tesseract-data-eng \
                poppler \
                mesa \
                glib2 \
                libsm \
                libxext \
                fontconfig \
                libxrender \
                curl \
                wget \
                git
        fi

    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install tesseract tesseract-lang poppler
        else
            echo -e "${YELLOW}${WARNING} Homebrew gerekli! Kurulum yapılacak...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            brew install tesseract tesseract-lang poppler
        fi
    fi

    echo -e "${GREEN}${CHECK_MARK} Sistem bağımlılıkları kuruldu${NC}"
}

# Uygulama dizinlerini oluştur
create_directories() {
    echo -e "${INFO} Uygulama dizinleri oluşturuluyor..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"

    echo -e "${GREEN}${CHECK_MARK} Dizinler oluşturuldu${NC}"
}

# Kaynak kodunu indir
download_source() {
    echo -e "${INFO} Kaynak kod indiriliyor..."

    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
    fi

    # Git ile indir
    if command -v git &> /dev/null; then
        git clone "$REPO_URL.git" "$INSTALL_DIR"
    else
        # Zip ile indir
        curl -L "$REPO_URL/archive/refs/heads/main.zip" -o /tmp/pypdf-tools.zip
        cd /tmp
        unzip -q pypdf-tools.zip
        mv PyPDF-Tools-v2-main "$INSTALL_DIR"
        rm pypdf-tools.zip
    fi

    echo -e "${GREEN}${CHECK_MARK} Kaynak kod indirildi${NC}"
}

# Python sanal ortamı oluştur
create_virtual_environment() {
    echo -e "${INFO} Python sanal ortamı oluşturuluyor..."

    cd "$INSTALL_DIR"
    $PYTHON_CMD -m venv venv

    # Sanal ortamı aktifleştir
    source venv/bin/activate

    # pip'i güncelle
    pip install --upgrade pip

    echo -e "${GREEN}${CHECK_MARK} Sanal ortam oluşturuldu${NC}"
}

# Python paketlerini kur
install_python_packages() {
    echo -e "${INFO} Python paketleri kuruluyor..."

    cd "$INSTALL_DIR"
    source venv/bin/activate

    # Ana gereksinimleri kur
    pip install -r requirements.txt

    # Platform-specific paketler
    if [[ "$OS" == "linux" ]]; then
        pip install python3-tk || true
    fi

    echo -e "${GREEN}${CHECK_MARK} Python paketleri kuruldu${NC}"
}

# Başlatma scriptini oluştur
create_launcher() {
    echo -e "${INFO} Başlatma scripti oluşturuluyor..."

    cat > "$BIN_DIR/pypdf-tools-v2" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python main.py "\$@"
EOF

    chmod +x "$BIN_DIR/pypdf-tools-v2"

    echo -e "${GREEN}${CHECK_MARK} Başlatma scripti oluşturuldu${NC}"
}

# Desktop entry oluştur
create_desktop_entry() {
    echo -e "${INFO} Masaüstü kısayolu oluşturuluyor..."

    cat > "$DESKTOP_DIR/pypdf-tools-v2.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PyPDF-Stirling Tools v2
Comment=Modern PDF İşleme Uygulaması
Exec=$BIN_DIR/pypdf-tools-v2
Icon=$INSTALL_DIR/icons/app_icon.png
Terminal=false
StartupNotify=true
Categories=Office;Graphics;Photography;
MimeType=application/pdf;
Keywords=pdf;merge;split;convert;ocr;
EOF

    # Desktop dosyasını çalıştırılabilir yap
    chmod +x "$DESKTOP_DIR/pypdf-tools-v2.desktop"

    echo -e "${GREEN}${CHECK_MARK} Masaüstü kısayolu oluşturuldu${NC}"
}

# PATH'e ekle
add_to_path() {
    echo -e "${INFO} PATH yapılandırması..."

    SHELL_RC=""

    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi

    # PATH'e ekle
    if ! echo "$PATH" | grep -q "$BIN_DIR"; then
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
        echo -e "${GREEN}${CHECK_MARK} $BIN_DIR PATH'e eklendi${NC}"
        echo -e "${YELLOW}${WARNING} Değişikliklerin geçerli olması için yeni terminal açın veya şu komutu çalıştırın:${NC}"
        echo -e "${CYAN}source $SHELL_RC${NC}"
    else
        echo -e "${GREEN}${CHECK_MARK} PATH zaten yapılandırılmış${NC}"
    fi
}

# Kurulum sonrası test
test_installation() {
    echo -e "${INFO} Kurulum test ediliyor..."

    cd "$INSTALL_DIR"
    source venv/bin/activate

    # Import testleri
    python -c "
import sys
print('Python version:', sys.version)

try:
    import tkinter
    print('✅ Tkinter: OK')
except ImportError as e:
    print('❌ Tkinter:', e)
    sys.exit(1)

try:
    import PyPDF2
    print('✅ PyPDF2: OK')
except ImportError as e:
    print('❌ PyPDF2:', e)
    sys.exit(1)

try:
    import PIL
    print('✅ Pillow: OK')
except ImportError as e:
    print('❌ Pillow:', e)
    sys.exit(1)

try:
    import fitz
    print('✅ PyMuPDF: OK')
except ImportError as e:
    print('❌ PyMuPDF:', e)
    sys.exit(1)

try:
    import pytesseract
    print('✅ Pytesseract: OK')
except ImportError as e:
    print('❌ Pytesseract:', e)
    sys.exit(1)

print('🎉 Tüm bağımlılıklar başarıyla yüklendi!')
"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}${CHECK_MARK} Kurulum başarıyla tamamlandı!${NC}"
        return 0
    else
        echo -e "${RED}${CROSS_MARK} Kurulum testinde hata!${NC}"
        return 1
    fi
}

# Temizlik fonksiyonu
cleanup() {
    echo -e "${INFO} Geçici dosyalar temizleniyor..."
    rm -f /tmp/pypdf-tools.zip
    echo -e "${GREEN}${CHECK_MARK} Temizlik tamamlandı${NC}"
}

# Ana kurulum fonksiyonu
main() {
    echo -e "${ROCKET} ${GREEN}PyPDF-Stirling Tools v2 kurulumu başlıyor...${NC}"
    echo ""

    # Kurulum adımları
    detect_system
    check_python
    install_system_dependencies
    create_directories
    download_source
    create_virtual_environment
    install_python_packages
    create_launcher
    create_desktop_entry
    add_to_path

    echo ""
    echo -e "${ROCKET} ${GREEN}Kurulum test ediliyor...${NC}"

    if test_installation; then
        cleanup

        echo ""
        echo -e "${GREEN}🎉 ${APP_NAME} başarıyla kuruldu!${NC}"
        echo ""
        echo -e "${CYAN}Nasıl başlatılır:${NC}"
        echo -e "  Terminal: ${YELLOW}pypdf-tools-v2${NC}"
        echo -e "  Masaüstü: Uygulamalar menüsünden 'PyPDF-Stirling Tools v2'"
        echo ""
        echo -e "${CYAN}Kurulum konumu:${NC} $INSTALL_DIR"
        echo -e "${CYAN}Executable:${NC} $BIN_DIR/pypdf-tools-v2"
        echo ""
        echo -e "${BLUE}İyi kullanımlar! 🚀${NC}"

    else
        echo -e "${RED}${CROSS_MARK} Kurulum başarısız!${NC}"
        echo "Yardım için: $REPO_URL/issues"
        exit 1
    fi
}

# Hata yakalama
trap cleanup EXIT

# Scripti çalıştır
main "$@"
