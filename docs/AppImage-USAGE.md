# 📦 PyPDF-Stirling Tools v2 AppImage Guide

## 🚀 Quick Start

### 1. Download
```bash
# Latest release'dan indirin
wget https://github.com/YOUR-USERNAME/PyPDF-Tools-v2/releases/latest/download/PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

### 2. Make Executable
```bash
chmod +x PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

### 3. Run
```bash
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

## 🔧 Building AppImage

### Prerequisites
- Linux x86_64 system
- Python 3.8+
- Basic development tools

### Build Process
```bash
# Repository'i klonla
git clone https://github.com/YOUR-USERNAME/PyPDF-Tools-v2.git
cd PyPDF-Tools-v2

# Build script'i çalıştır
chmod +x build-appimage.sh
./build-appimage.sh build

# Test et
./build-appimage.sh test
```

### Build Options
```bash
./build-appimage.sh build    # Full build
./build-appimage.sh clean    # Clean artifacts
./build-appimage.sh test     # Test existing AppImage
./build-appimage.sh help     # Show help
```

## 🖥️ Desktop Integration

### Manual Integration
```bash
# AppImage'ı ~/Applications'a taşı
mkdir -p ~/Applications
mv PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage ~/Applications/

# Desktop entry oluştur
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/pypdf-tools-v2.desktop << EOF
[Desktop Entry]
Name=PyPDF-Stirling Tools v2
Exec=$HOME/Applications/PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
Icon=pypdf-tools-v2
Type=Application
Categories=Office;Graphics;
Comment=Modern PDF processing application
EOF

# Desktop entry'yi güncelle
update-desktop-database ~/.local/share/applications
```

### Automatic Integration (AppImageLauncher)
```bash
# AppImageLauncher kur (Ubuntu/Debian)
sudo apt install appimagelauncher

# AppImage'ı çift tıklayın, otomatik entegrasyon sunulur
```

## 📋 Command Line Usage

### Basic Commands
```bash
# GUI mode (default)
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Help
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --help

# Version info
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --version

# Test mode
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --test

# Console mode (no GUI)
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --console
```

### Advanced Usage
```bash
# Specific operations
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --operation=merge
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --operation=split
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --operation=ocr

# Batch processing
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --batch input_folder/ output_folder/
```

## 🔍 AppImage Information

### Extract Contents (for inspection)
```bash
# Extract AppImage contents
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --appimage-extract

# Explore extracted files
ls -la squashfs-root/
```

### AppImage Properties
```bash
# File information
file PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Size
du -h PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Dependencies (ldd won't work on AppImage)
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --appimage-extract
ldd squashfs-root/usr/bin/pypdf-tools-v2
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Problem: Permission denied error
# Solution: Make executable
chmod +x PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

#### 2. GLIBC Version Error
```bash
# Problem: GLIBC_X.XX not found
# Check your system version
ldd --version

# If your GLIBC is too old, try:
# - Update your Linux distribution
# - Use a newer Ubuntu/Debian version
# - Build from source instead
```

#### 3. Missing Libraries
```bash
# Problem: libXXX.so not found
# Install missing system packages

# Ubuntu/Debian
sudo apt install libgl1-mesa-glx libglib2.0-0 libfontconfig1 libxrender1

# Fedora/CentOS
sudo dnf install mesa-libGL glib2 fontconfig libXrender

# Arch Linux
sudo pacman -S mesa glib2 fontconfig libxrender
```

#### 4. GUI Not Starting
```bash
# Check display
echo $DISPLAY

# Test with X11 forwarding (SSH)
ssh -X user@host

# Try with virtual display
xvfb-run ./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

#### 5. OCR Not Working
```bash
# Check if Tesseract is bundled
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --appimage-extract
ls squashfs-root/usr/share/tessdata/

# If not bundled, install system Tesseract
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-tur
```

### Debug Mode
```bash
# Run with debug info
DEBUG=1 ./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Run with strace (for advanced debugging)
strace -e trace=openat ./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Linux x86_64 (GLIBC 2.17+)
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Display**: X11 or Wayland

### Supported Distributions
- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ Fedora 30+
- ✅ CentOS 8+
- ✅ Arch Linux
- ✅ openSUSE Leap 15+
- ✅ Linux Mint 19+

### Tested Environments
```
✅ Ubuntu 20.04 LTS - Primary development
✅ Ubuntu 22.04 LTS - CI/CD testing
✅ Debian 11 - Stability testing
✅ Fedora 36 - RPM-based testing
✅ Arch Linux - Rolling release testing
```

## 📦 What's Included

### Bundled Components
- **Python 3.8+** runtime
- **Tkinter** GUI framework
- **PyPDF2** - PDF processing
- **PyMuPDF** - Advanced PDF operations
- **Pillow** - Image processing
- **OpenCV** - Image preprocessing
- **Tesseract OCR** - Text recognition
- **Language packs**: English, Turkish
- **System libraries** - Required dependencies

### Features Available
- ✅ PDF merge, split, rotate
- ✅ PDF compression and optimization
- ✅ Format conversion (PDF ↔ Word, Images)
- ✅ OCR with multi-language support
- ✅ Watermarks and annotations
- ✅ Encryption and security
- ✅ Batch processing
- ✅ Modern GUI with 4 themes
- ✅ Settings and preferences
- ✅ Cross-platform compatibility

## 🚀 Performance Tips

### Optimization
```bash
# Run from SSD for better performance
mv PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage /path/to/ssd/

# Use RAM disk for temporary operations
export TMPDIR=/tmp/ramdisk

# Increase available memory
# Edit ~/.bashrc
export PYTHONPATH="$PYTHONPATH:."
export MALLOC_ARENA_MAX=2
```

### Resource Usage
- **Cold start**: ~3-5 seconds
- **Warm start**: ~1-2 seconds
- **Memory usage**: ~150-300MB
- **CPU usage**: Variable (depends on operation)
- **Disk I/O**: Minimal during normal operation

## 🔄 Updates

### Check for Updates
```bash
# Manual check
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --check-updates

# Or visit GitHub releases
# https://github.com/YOUR-USERNAME/PyPDF-Tools-v2/releases/latest
```

### Update Process
1. Download new AppImage
2. Replace old AppImage
3. Update desktop integration if needed

### Auto-Update (Future)
```bash
# AppImageUpdate tool (when available)
appimageupdate PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage
```

## 🛡️ Security

### AppImage Verification
```bash
# Check file integrity
sha256sum PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Compare with published checksums from GitHub releases
```

### Sandbox Execution
```bash
# Run in firejail (if available)
firejail ./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage

# Run with restricted permissions
./PyPDF-Stirling_Tools_v2-2.0.0-x86_64.AppImage --restricted
```

## 📞 Support

### Getting Help
1. **GitHub Issues**: Report bugs and request features
2. **Documentation**: Check README.md and wiki
3. **Community**: Join discussions in GitHub Discussions

### Reporting Issues
When reporting issues, include:
- Linux distribution and version
- AppImage file name and size
- Error messages (full output)
- Steps to reproduce
- System information (`uname -a`)

### Debug Information
```bash
# Generate debug report
./test-appimage.sh > debug-report.txt 2>&1

# Include this file with your issue report
```

---

## 📄 License

This AppImage package includes:
- PyPDF-Stirling Tools v2 (MIT License)
- Python runtime (PSF License)
- Various open-source libraries (respective licenses)

See the bundled LICENSE files for complete license information.

---

## 🎉 Conclusion

The PyPDF-Stirling Tools v2 AppImage provides a complete, portable PDF processing solution for Linux users. No installation required - just download, make executable, and run!

**Happy PDF processing! 🚀📄**
