#!/bin/bash

# PyPDF-Stirling Tools v2 - AppImage Builder Script
# Linux için taşınabilir uygulama paketi oluşturur

set -e

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Unicode karakterler
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
PACKAGE="📦"

# Uygulama bilgileri
APP_NAME="PyPDF-Stirling_Tools_v2"
APP_VERSION="2.0.0"
APP_DIR="PyPDF-Stirling-Tools-v2"
APPDIR="${APP_NAME}.AppDir"
BUILD_DIR="build"
DIST_DIR="dist"

echo -e "${BLUE}${PACKAGE} PyPDF-Stirling Tools v2 AppImage Builder${NC}"
echo -e "${CYAN}Creating portable Linux application package${NC}"
echo -e "${CYAN}Version: ${APP_VERSION}${NC}"
echo ""

# Fonksiyonlar
log_info() { echo -e "${INFO} $1"; }
log_success() { echo -e "${GREEN}${CHECK} $1${NC}"; }
log_error() { echo -e "${RED}${CROSS} $1${NC}"; }
log_warning() { echo -e "${YELLOW}${WARNING} $1${NC}"; }
log_progress() { echo -e "${BLUE}${GEAR} $1${NC}"; }

# Gerekli araçları kontrol et
check_dependencies() {
    log_progress "Checking dependencies..."

    local missing_deps=()

    # Python kontrolü
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    # pip kontrolü
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("python3-pip")
    fi

    # wget kontrolü
    if ! command -v wget &> /dev/null; then
        missing_deps+=("wget")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Install with: sudo apt-get install ${missing_deps[*]}"
        exit 1
    fi

    log_success "All dependencies found"
}

# Python sanal ortamı oluştur
create_python_environment() {
    log_progress "Creating Python virtual environment..."

    # Temizlik
    rm -rf venv

    # Python venv oluştur
    python3 -m venv venv
    source venv/bin/activate

    # pip güncelle
    pip install --upgrade pip

    log_success "Python environment created"
}

# Bağımlılıkları kur
install_dependencies() {
    log_progress "Installing Python dependencies..."

    source venv/bin/activate

    # PyInstaller kur (AppImage için gerekli)
    pip install pyinstaller

    # Ana bağımlılıklar
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        log_error "requirements.txt not found!"
        exit 1
    fi

    # Ek bağımlılıklar
    pip install pillow==10.0.1  # Sabit versiyon
    pip install pyqt5 || log_warning "PyQt5 installation failed, using tkinter"

    log_success "Dependencies installed"
}

# PyInstaller ile executable oluştur
create_executable() {
    log_progress "Creating executable with PyInstaller..."

    source venv/bin/activate

    # PyInstaller spec dosyası oluştur
    cat > pypdf-tools.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

block_cipher = None

# Ana uygulama
a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('ui/*.py', 'ui'),
        ('resources/*.py', 'resources'),
        ('icons/*', 'icons'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PIL.Image',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'PyPDF2',
        'fitz',
        'pytesseract',
        'cv2',
        'reportlab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.distutils',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pypdf-tools-v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon='icons/app_icon.ico' if os.path.exists('icons/app_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pypdf-tools-v2',
)
EOF

    # PyInstaller çalıştır
    pyinstaller --clean pypdf-tools.spec

    if [ ! -f "dist/pypdf-tools-v2/pypdf-tools-v2" ]; then
        log_error "Executable creation failed!"
        exit 1
    fi

    log_success "Executable created"
}

# AppDir yapısı oluştur
create_appdir_structure() {
    log_progress "Creating AppDir structure..."

    # Temizlik
    rm -rf "${APPDIR}"
    mkdir -p "${APPDIR}"

    # Ana dizinler
    mkdir -p "${APPDIR}/usr/bin"
    mkdir -p "${APPDIR}/usr/lib"
    mkdir -p "${APPDIR}/usr/share/applications"
    mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "${APPDIR}/usr/share/icons/hicolor/128x128/apps"
    mkdir -p "${APPDIR}/usr/share/icons/hicolor/64x64/apps"
    mkdir -p "${APPDIR}/usr/share/pixmaps"

    # Executable ve bağımlılıkları kopyala
    cp -r dist/pypdf-tools-v2/* "${APPDIR}/usr/bin/"

    # Ana executable'a link oluştur
    cd "${APPDIR}"
    ln -sf usr/bin/pypdf-tools-v2 AppRun
    cd ..

    log_success "AppDir structure created"
}

# Desktop entry oluştur
create_desktop_entry() {
    log_progress "Creating desktop entry..."

    cat > "${APPDIR}/pypdf-tools-v2.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PyPDF-Stirling Tools v2
GenericName=PDF Processing Application
Comment=Modern PDF processing application with OCR support
Comment[tr]=OCR destekli modern PDF işleme uygulaması
Exec=pypdf-tools-v2
Icon=pypdf-tools-v2
Terminal=false
StartupNotify=true
Categories=Office;Graphics;Photography;Publishing;
MimeType=application/pdf;
Keywords=pdf;merge;split;convert;ocr;compress;
Keywords[tr]=pdf;birleştir;böl;dönüştür;ocr;sıkıştır;
Actions=Merge;Split;Convert;OCR;

[Desktop Action Merge]
Name=Merge PDFs
Name[tr]=PDF Birleştir
Exec=pypdf-tools-v2 --operation=merge

[Desktop Action Split]
Name=Split PDF
Name[tr]=PDF Böl
Exec=pypdf-tools-v2 --operation=split

[Desktop Action Convert]
Name=Convert PDF
Name[tr]=PDF Dönüştür
Exec=pypdf-tools-v2 --operation=convert

[Desktop Action OCR]
Name=Apply OCR
Name[tr]=OCR Uygula
Exec=pypdf-tools-v2 --operation=ocr
EOF

    # Desktop entry'yi AppDir root'a da kopyala
    cp "${APPDIR}/pypdf-tools-v2.desktop" "${APPDIR}/usr/share/applications/"

    # Executable yap
    chmod +x "${APPDIR}/pypdf-tools-v2.desktop"
    chmod +x "${APPDIR}/usr/share/applications/pypdf-tools-v2.desktop"

    log_success "Desktop entry created"
}

# İkonları oluştur/kopyala
create_icons() {
    log_progress "Creating application icons..."

    # Varsayılan ikon oluştur (SVG)
    if [ ! -d "icons" ]; then
        mkdir -p icons
    fi

    # SVG ikon oluştur (eğer yoksa)
    if [ ! -f "icons/app_icon.svg" ]; then
        cat > icons/app_icon.svg << 'EOF'
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="256" height="256" rx="32" ry="32" fill="url(#grad1)"/>
  <rect x="48" y="48" width="160" height="200" rx="8" ry="8" fill="white" opacity="0.95"/>
  <rect x="64" y="80" width="128" height="4" fill="#3b82f6"/>
  <rect x="64" y="96" width="96" height="4" fill="#6b7280"/>
  <rect x="64" y="112" width="112" height="4" fill="#6b7280"/>
  <rect x="64" y="128" width="88" height="4" fill="#6b7280"/>
  <rect x="64" y="160" width="104" height="4" fill="#6b7280"/>
  <rect x="64" y="176" width="120" height="4" fill="#6b7280"/>
  <rect x="64" y="192" width="80" height="4" fill="#6b7280"/>
  <circle cx="192" cy="208" r="16" fill="#10b981"/>
  <path d="M185 208 L190 213 L199 204" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF
    fi

    # SVG'yi PNG'ye çevir (eğer ImageMagick varsa)
    if command -v convert &> /dev/null; then
        # Çeşitli boyutlarda PNG oluştur
        convert icons/app_icon.svg -resize 256x256 "${APPDIR}/usr/share/icons/hicolor/256x256/apps/pypdf-tools-v2.png"
        convert icons/app_icon.svg -resize 128x128 "${APPDIR}/usr/share/icons/hicolor/128x128/apps/pypdf-tools-v2.png"
        convert icons/app_icon.svg -resize 64x64 "${APPDIR}/usr/share/icons/hicolor/64x64/apps/pypdf-tools-v2.png"

        # Pixmaps için
        cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/pypdf-tools-v2.png" "${APPDIR}/usr/share/pixmaps/pypdf-tools-v2.png"

        # AppDir root için
        cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/pypdf-tools-v2.png" "${APPDIR}/pypdf-tools-v2.png"

        log_success "Icons created from SVG"
    else
        # ImageMagick yoksa basit renk ikon oluştur
        log_warning "ImageMagick not found, creating simple icon"

        # Python ile basit ikon oluştur
        python3 << EOF
from PIL import Image, ImageDraw
import os

def create_icon(size, path):
    img = Image.new('RGBA', (size, size), (59, 130, 246, 255))
    draw = ImageDraw.Draw(img)

    # Beyaz dikdörtgen (kağıt)
    margin = size // 8
    draw.rectangle([margin, margin, size-margin, size-margin*6//4], fill='white', outline=(29, 78, 216, 255), width=2)

    # Çizgiler
    for i in range(3):
        y = margin + size//4 + i * size//12
        draw.rectangle([margin + size//8, y, size - margin - size//8, y + size//32], fill=(107, 114, 128, 255))

    # Onay işareti
    cx, cy = size - margin - size//8, size - margin - size//6
    draw.ellipse([cx-size//16, cy-size//16, cx+size//16, cy+size//16], fill=(16, 185, 129, 255))

    img.save(path, 'PNG')

# Çeşitli boyutlarda ikon oluştur
os.makedirs('${APPDIR}/usr/share/icons/hicolor/256x256/apps', exist_ok=True)
os.makedirs('${APPDIR}/usr/share/icons/hicolor/128x128/apps', exist_ok=True)
os.makedirs('${APPDIR}/usr/share/icons/hicolor/64x64/apps', exist_ok=True)
os.makedirs('${APPDIR}/usr/share/pixmaps', exist_ok=True)

create_icon(256, '${APPDIR}/usr/share/icons/hicolor/256x256/apps/pypdf-tools-v2.png')
create_icon(128, '${APPDIR}/usr/share/icons/hicolor/128x128/apps/pypdf-tools-v2.png')
create_icon(64, '${APPDIR}/usr/share/icons/hicolor/64x64/apps/pypdf-tools-v2.png')
create_icon(256, '${APPDIR}/usr/share/pixmaps/pypdf-tools-v2.png')
create_icon(256, '${APPDIR}/pypdf-tools-v2.png')
EOF

        log_success "Simple icons created with Python"
    fi
}

# AppRun script oluştur
create_apprun() {
    log_progress "Creating AppRun script..."

    cat > "${APPDIR}/AppRun" << 'EOF'
#!/bin/bash

# PyPDF-Stirling Tools v2 AppRun Script

# AppImage için environment setup
export APPDIR="$(dirname "$(readlink -f "${0}")")"
export PATH="${APPDIR}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${APPDIR}/usr/lib/python3/dist-packages:${PYTHONPATH}"

# XDG ayarları
export XDG_DATA_DIRS="${APPDIR}/usr/share:${XDG_DATA_DIRS}"

# Tesseract OCR path (eğer AppImage içinde varsa)
if [ -d "${APPDIR}/usr/share/tessdata" ]; then
    export TESSDATA_PREFIX="${APPDIR}/usr/share"
fi

# Python executable path
PYTHON_EXEC="${APPDIR}/usr/bin/pypdf-tools-v2"

# Check if executable exists
if [ ! -f "${PYTHON_EXEC}" ]; then
    echo "Error: Application executable not found!"
    echo "Expected: ${PYTHON_EXEC}"
    exit 1
fi

# Run the application
exec "${PYTHON_EXEC}" "$@"
EOF

    chmod +x "${APPDIR}/AppRun"

    log_success "AppRun script created"
}

# Sistem kütüphanelerini kopyala
copy_system_libraries() {
    log_progress "Copying system libraries..."

    # Python kütüphaneleri zaten PyInstaller tarafından dahil edildi
    # Ek sistem kütüphaneleri gerekirse buraya eklenebilir

    # Tesseract dil dosyalarını kopyala (eğer varsa)
    if [ -d "/usr/share/tesseract-ocr/4.00/tessdata" ]; then
        mkdir -p "${APPDIR}/usr/share/tessdata"
        cp /usr/share/tesseract-ocr/4.00/tessdata/*.traineddata "${APPDIR}/usr/share/tessdata/" 2>/dev/null || true
        log_success "Tesseract language files copied"
    elif [ -d "/usr/share/tessdata" ]; then
        mkdir -p "${APPDIR}/usr/share/tessdata"
        cp /usr/share/tessdata/*.traineddata "${APPDIR}/usr/share/tessdata/" 2>/dev/null || true
        log_success "Tesseract language files copied"
    else
        log_warning "Tesseract language files not found"
    fi

    log_success "System libraries handled"
}

# AppImageTool indir ve çalıştır
download_and_run_appimagetool() {
    log_progress "Downloading AppImageTool..."

    # AppImageTool URL
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"

    # İndir
    if [ ! -f "appimagetool-x86_64.AppImage" ]; then
        wget -q --show-progress "${APPIMAGETOOL_URL}" -O appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
    fi

    log_success "AppImageTool downloaded"

    # AppImage oluştur
    log_progress "Creating AppImage..."

    ./appimagetool-x86_64.AppImage "${APPDIR}" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

    if [ -f "${APP_NAME}-${APP_VERSION}-x86_64.AppImage" ]; then
        log_success "AppImage created: ${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

        # Dosya bilgilerini göster
        echo ""
        echo -e "${CYAN}📊 AppImage Information:${NC}"
        echo -e "   File: $(basename "${APP_NAME}-${APP_VERSION}-x86_64.AppImage")"
        echo -e "   Size: $(du -h "${APP_NAME}-${APP_VERSION}-x86_64.AppImage" | cut -f1)"
        echo -e "   Type: $(file "${APP_NAME}-${APP_VERSION}-x86_64.AppImage" | cut -d: -f2-)"
        echo ""

        # Test çalıştırması
        log_info "Testing AppImage..."
        if ./"${APP_NAME}-${APP_VERSION}-x86_64.AppImage" --help &>/dev/null; then
            log_success "AppImage test passed"
        else
            log_warning "AppImage test failed (this might be normal for GUI apps)"
        fi

        return 0
    else
        log_error "AppImage creation failed!"
        return 1
    fi
}

# Temizlik
cleanup() {
    log_progress "Cleaning up..."

    # Geçici dosyaları temizle
    rm -rf build/
    rm -rf __pycache__/
    rm -rf *.pyc
    rm -rf .pytest_cache/
    rm -f pypdf-tools.spec

    # AppDir'i koru (debug için)
    if [ "$1" != "keep-appdir" ]; then
        rm -rf "${APPDIR}"
    fi

    log_success "Cleanup completed"
}

# Test fonksiyonu
test_appimage() {
    log_progress "Testing AppImage functionality..."

    local appimage_file="${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

    if [ ! -f "$appimage_file" ]; then
        log_error "AppImage file not found: $appimage_file"
        return 1
    fi

    # Executable test
    chmod +x "$appimage_file"

    # Basic tests
    echo "Testing AppImage:"
    echo "  - File permissions: $(ls -l "$appimage_file" | cut -d' ' -f1)"
    echo "  - File size: $(du -h "$appimage_file" | cut -f1)"

    # Extract and check contents
    log_info "Extracting AppImage for inspection..."
    ./"$appimage_file" --appimage-extract-and-run echo "AppImage works!" || log_warning "Could not test AppImage execution"

    log_success "AppImage testing completed"
}

# Ana build fonksiyonu
main() {
    echo -e "${ROCKET} Starting AppImage build process..."
    echo ""

    # Build adımları
    check_dependencies
    create_python_environment
    install_dependencies
    create_executable
    create_appdir_structure
    create_desktop_entry
    create_icons
    create_apprun
    copy_system_libraries
    download_and_run_appimagetool

    if [ $? -eq 0 ]; then
        test_appimage
        cleanup

        echo ""
        echo -e "${GREEN}${ROCKET} AppImage build completed successfully!${NC}"
        echo ""
        echo -e "${CYAN}📦 Output file: ${APP_NAME}-${APP_VERSION}-x86_64.AppImage${NC}"
        echo -e "${CYAN}💿 Installation: Make executable and run${NC}"
        echo ""
        echo -e "${BLUE}Usage:${NC}"
        echo -e "  chmod +x ${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
        echo -e "  ./${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
        echo ""
        echo -e "${BLUE}Distribution:${NC}"
        echo -e "  Upload to GitHub Releases or host on your server"
        echo -e "  Users can download and run directly"
        echo ""
    else
        log_error "AppImage build failed!"
        cleanup
        exit 1
    fi
}

# Komut satırı argümanları
case "${1:-build}" in
    "build")
        main
        ;;
    "clean")
        log_info "Cleaning build artifacts..."
        cleanup
        rm -f *.AppImage
        rm -f appimagetool-x86_64.AppImage
        log_success "Clean completed"
        ;;
    "test")
        if [ -f "${APP_NAME}-${APP_VERSION}-x86_64.AppImage" ]; then
            test_appimage
        else
            log_error "No AppImage found to test"
            exit 1
        fi
        ;;
    "help")
        echo "PyPDF-Stirling Tools v2 AppImage Builder"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build    Build AppImage (default)"
        echo "  clean    Clean build artifacts"
        echo "  test     Test existing AppImage"
        echo "  help     Show this help"
        echo ""
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
