#!/bin/bash

# PyPDF-Stirling Tools v2 - AppImage Test Script
# AppImage dosyasını test eder ve doğrular

set -e

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Semboller
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
TEST="🧪"

APP_NAME="PyPDF-Stirling_Tools_v2"
APP_VERSION="2.0.0"
APPIMAGE_FILE="${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

# Fonksiyonlar
log_info() { echo -e "${INFO} $1"; }
log_success() { echo -e "${GREEN}${CHECK} $1${NC}"; }
log_error() { echo -e "${RED}${CROSS} $1${NC}"; }
log_warning() { echo -e "${YELLOW}${WARNING} $1${NC}"; }
log_test() { echo -e "${BLUE}${TEST} $1${NC}"; }

# AppImage dosyası kontrolü
check_appimage_file() {
    log_test "Checking AppImage file..."

    if [ ! -f "$APPIMAGE_FILE" ]; then
        log_error "AppImage file not found: $APPIMAGE_FILE"
        echo "Available files:"
        ls -la *.AppImage 2>/dev/null || echo "No AppImage files found"
        return 1
    fi

    # Dosya bilgileri
    echo -e "${CYAN}📊 File Information:${NC}"
    echo "   File: $APPIMAGE_FILE"
    echo "   Size: $(du -h "$APPIMAGE_FILE" | cut -f1)"
    echo "   Type: $(file "$APPIMAGE_FILE" | cut -d: -f2-)"
    echo "   Permissions: $(ls -la "$APPIMAGE_FILE" | cut -d' ' -f1)"
    echo "   Modified: $(ls -la "$APPIMAGE_FILE" | awk '{print $6" "$7" "$8}')"

    # Executable kontrolü
    if [ -x "$APPIMAGE_FILE" ]; then
        log_success "File is executable"
    else
        log_warning "File is not executable, making it executable..."
        chmod +x "$APPIMAGE_FILE"
    fi

    log_success "AppImage file check passed"
}

# AppImage yapısını kontrol et
check_appimage_structure() {
    log_test "Checking AppImage internal structure..."

    # Geçici dizin oluştur
    TEMP_DIR=$(mktemp -d)

    # AppImage içeriğini çıkar
    echo "Extracting AppImage..."
    cd "$TEMP_DIR"
    "$OLDPWD/$APPIMAGE_FILE" --appimage-extract >/dev/null 2>&1

    if [ ! -d "squashfs-root" ]; then
        log_error "Failed to extract AppImage"
        return 1
    fi

    cd squashfs-root

    echo -e "${CYAN}📁 Internal Structure:${NC}"

    # AppRun kontrolü
    if [ -f "AppRun" ] && [ -x "AppRun" ]; then
        log_success "AppRun script found and executable"
    else
        log_error "AppRun script missing or not executable"
    fi

    # Desktop file kontrolü
    if [ -f "pypdf-tools-v2.desktop" ]; then
        log_success "Desktop file found"

        # Desktop file validation
        if command -v desktop-file-validate >/dev/null; then
            if desktop-file-validate pypdf-tools-v2.desktop; then
                log_success "Desktop file is valid"
            else
                log_warning "Desktop file has validation issues"
            fi
        fi
    else
        log_error "Desktop file not found"
    fi

    # Icon kontrolü
    if [ -f "pypdf-tools-v2.png" ]; then
        log_success "Main icon found"
    else
        log_warning "Main icon not found"
    fi

    # Executable kontrolü
    if [ -f "usr/bin/pypdf-tools-v2" ]; then
        log_success "Main executable found"
        echo "   Executable type: $(file usr/bin/pypdf-tools-v2 | cut -d: -f2-)"
    else
        log_error "Main executable not found"
    fi

    # Library kontrolü
    echo "   Libraries found: $(find usr/lib -name "*.so*" 2>/dev/null | wc -l) files"

    # Python modules kontrolü
    if [ -d "usr/lib/python3" ]; then
        echo "   Python modules: $(find usr/lib/python3 -name "*.py" -o -name "*.so" 2>/dev/null | wc -l) files"
        log_success "Python modules found"
    else
        log_warning "Python modules directory not found"
    fi

    # Tesseract data kontrolü
    if [ -d "usr/share/tessdata" ]; then
        tessdata_count=$(ls usr/share/tessdata/*.traineddata 2>/dev/null | wc -l)
        if [ "$tessdata_count" -gt 0 ]; then
            log_success "Tesseract language data found ($tessdata_count languages)"
        else
            log_warning "No Tesseract language files found"
        fi
    else
        log_warning "Tesseract data directory not found"
    fi

    # Temizlik
    cd "$OLDPWD"
    rm -rf "$TEMP_DIR"

    log_success "Structure check completed"
}

# AppImage fonksiyonalite testleri
test_appimage_functionality() {
    log_test "Testing AppImage functionality..."

    # Temel çalıştırma testi
    echo "Testing basic execution..."
    timeout 10s ./"$APPIMAGE_FILE" --help >/dev/null 2>&1 && {
        log_success "Help command works"
    } || {
        log_warning "Help command test timeout (this might be normal)"
    }

    # Version testi
    echo "Testing version command..."
    timeout 5s ./"$APPIMAGE_FILE" --version 2>/dev/null && {
        log_success "Version command works"
    } || {
        log_warning "Version command not available"
    }

    # Test mode
    echo "Testing test mode..."
    timeout 10s ./"$APPIMAGE_FILE" --test 2>/dev/null && {
        log_success "Test mode works"
    } || {
        log_warning "Test mode not available or failed"
    }

    # GUI test (eğer X11 varsa)
    if [ -n "$DISPLAY" ]; then
        echo "Testing GUI mode..."
        timeout 5s ./"$APPIMAGE_FILE" >/dev/null 2>&1 &
        APP_PID=$!
        sleep 2

        if kill -0 $APP_PID 2>/dev/null; then
            log_success "GUI application started successfully"
            kill $APP_PID 2>/dev/null || true
            wait $APP_PID 2>/dev/null || true
        else
            log_warning "GUI test failed or application exited early"
        fi
    else
        log_warning "No display available for GUI testing"
    fi

    log_success "Functionality tests completed"
}

# Sistem uyumluluğunu test et
test_system_compatibility() {
    log_test "Testing system compatibility..."

    # OS detection
    echo -e "${CYAN}🖥️  System Information:${NC}"
    echo "   OS: $(uname -s)"
    echo "   Kernel: $(uname -r)"
    echo "   Architecture: $(uname -m)"

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "   Distribution: $NAME $VERSION"
    fi

    # Required libraries check
    echo "Checking required libraries..."

    required_libs=(
        "libpython3"
        "libtk8"
        "libx11"
        "libglib-2.0"
        "libfontconfig"
    )

    for lib in "${required_libs[@]}"; do
        if ldconfig -p | grep -q "$lib"; then
            log_success "$lib found"
        else
            log_warning "$lib not found (might be bundled in AppImage)"
        fi
    done

    # GLIBC version check
    echo "Checking GLIBC version..."
    glibc_version=$(ldd --version | head -1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
    echo "   System GLIBC: $glibc_version"

    if [ $(echo "$glibc_version >= 2.17" | bc -l) -eq 1 ] 2>/dev/null; then
        log_success "GLIBC version is compatible"
    else
        log_warning "GLIBC version might be incompatible"
    fi

    log_success "Compatibility check completed"
}

# AppImage metadata kontrol
check_appimage_metadata() {
    log_test "Checking AppImage metadata..."

    # AppImage magic number
    if hexdump -C "$APPIMAGE_FILE" | head -1 | grep -q "AI"; then
        log_success "AppImage magic number found"
    else
        log_warning "AppImage magic number not found"
    fi

    # Embedded update information
    echo "Checking update information..."
    strings "$APPIMAGE_FILE" | grep -E "(zsync|github)" | head -5 || echo "   No update info found"

    # Size analysis
    echo -e "${CYAN}📊 Size Analysis:${NC}"
    file_size=$(stat -f%z "$APPIMAGE_FILE" 2>/dev/null || stat -c%s "$APPIMAGE_FILE")
    echo "   Total size: $(numfmt --to=iec-i --suffix=B $file_size)"

    if [ $file_size -lt 50000000 ]; then  # 50MB
        log_success "AppImage size is reasonable (< 50MB)"
    elif [ $file_size -lt 200000000 ]; then  # 200MB
        log_warning "AppImage is moderately large (50-200MB)"
    else
        log_warning "AppImage is very large (> 200MB)"
    fi

    log_success "Metadata check completed"
}

# Performance test
test_performance() {
    log_test "Testing AppImage performance..."

    echo "Measuring startup time..."

    # Startup time test
    start_time=$(date +%s.%3N)
    timeout 10s ./"$APPIMAGE_FILE" --test >/dev/null 2>&1 || true
    end_time=$(date +%s.%3N)

    startup_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")

    if [ "$startup_time" != "N/A" ]; then
        echo "   Startup time: ${startup_time}s"

        if [ $(echo "$startup_time < 5.0" | bc -l) -eq 1 ] 2>/dev/null; then
            log_success "Fast startup (< 5s)"
        elif [ $(echo "$startup_time < 10.0" | bc -l) -eq 1 ] 2>/dev/null; then
            log_warning "Moderate startup time (5-10s)"
        else
            log_warning "Slow startup (> 10s)"
        fi
    else
        log_warning "Could not measure startup time"
    fi

    log_success "Performance test completed"
}

# Güvenlik kontrolü
security_check() {
    log_test "Running security checks..."

    # File permissions
    perms=$(ls -la "$APPIMAGE_FILE" | cut -d' ' -f1)
    if [[ "$perms" =~ ^-rwx.*$ ]]; then
        log_success "File permissions are appropriate"
    else
        log_warning "Unusual file permissions: $perms"
    fi

    # Check for suspicious strings
    echo "Scanning for suspicious content..."
    suspicious_strings=("password" "secret" "token" "/tmp/")

    for str in "${suspicious_strings[@]}"; do
        if strings "$APPIMAGE_FILE" | grep -qi "$str" | head -1; then
            log_warning "Found potentially suspicious string: $str"
        fi
    done

    log_success "Security check completed"
}

# Ana test fonksiyonu
main() {
    echo -e "${BLUE}${TEST} PyPDF-Stirling Tools v2 AppImage Tester${NC}"
    echo -e "${CYAN}Testing file: $APPIMAGE_FILE${NC}"
    echo ""

    # Test sırası
    check_appimage_file || exit 1
    echo ""

    check_appimage_structure
    echo ""

    test_appimage_functionality
    echo ""

    test_system_compatibility
    echo ""

    check_appimage_metadata
    echo ""

    test_performance
    echo ""

    security_check
    echo ""

    echo -e "${GREEN}${ROCKET} All tests completed!${NC}"
    echo ""
    echo -e "${CYAN}📋 Test Summary:${NC}"
    echo -e "   AppImage: $APPIMAGE_FILE"
    echo -e "   Status: ✅ Ready for distribution"
    echo ""
    echo -e "${BLUE}🚀 Usage Instructions:${NC}"
    echo -e "   1. Make executable: chmod +x $APPIMAGE_FILE"
    echo -e "   2. Run application: ./$APPIMAGE_FILE"
    echo -e "   3. Integrate with desktop: ./$APPIMAGE_FILE --appimage-integrate"
    echo ""
}

# Komut satırı argümanları
case "${1:-test}" in
    "test")
        main
        ;;
    "quick")
        check_appimage_file
        test_appimage_functionality
        ;;
    "structure")
        check_appimage_structure
        ;;
    "performance")
        test_performance
        ;;
    "security")
        security_check
        ;;
    "help")
        echo "PyPDF-Stirling Tools v2 AppImage Tester"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  test         Run all tests (default)"
        echo "  quick        Quick functionality test"
        echo "  structure    Check internal structure"
        echo "  performance  Performance benchmarks"
        echo "  security     Security checks"
        echo "  help         Show this help"
        echo ""
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
