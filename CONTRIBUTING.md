# Katkıda Bulunma Rehberi 🤝

PyPDF-Tools projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu rehber size nasıl katkıda bulunabileceğinizi gösterecektir.

## 📋 İçindekiler

- [Başlamadan Önce](#başlamadan-önce)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Katkı Türleri](#katkı-türleri)
- [Pull Request Süreci](#pull-request-süreci)
- [Kod Standartları](#kod-standartları)
- [Test Yazma](#test-yazma)
- [Dokümantasyon](#dokümantasyon)
- [Issue Bildirme](#issue-bildirme)
- [İletişim](#iletişim)

## 🚀 Başlamadan Önce

### Davranış Kuralları
Bu projeye katılım gösteren herkes [Davranış Kuralları](CODE_OF_CONDUCT.md) belgesine uymayı kabul etmiş sayılır.

### Katkı Felsefesi
- **Kullanıcı Odaklı**: Her özellik kullanıcı deneyimini iyileştirmeli
- **Performans**: Hız ve bellek kullanımı her zaman önceliktir
- **Cross-Platform**: Tüm platformlarda çalışmalı
- **Güvenlik**: Kullanıcı verileri güvende olmalı
- **Açık Kaynak**: Şeffaf ve topluluk odaklı geliştirme

## 💻 Geliştirme Ortamı Kurulumu

### Ön Gereksinimler
```bash
# Python 3.8+ gerekli (3.11+ önerili)
python --version

# Git kurulu olmalı
git --version

# Platform-specific dependencies
# Ubuntu/Debian:
sudo apt install python3-dev python3-venv build-essential

# macOS:
brew install python@3.11

# Windows:
# Python.org'dan Python 3.11+ indirin
```

### Repository'yi Fork ve Clone Etme
```bash
# 1. GitHub'da repository'yi fork edin
# 2. Fork'unuzu clone edin
git clone https://github.com/KULLANICI_ADINIZ/PyPDF-Tools.git
cd PyPDF-Tools

# 3. Upstream remote ekleyin
git remote add upstream https://github.com/Fatih-Bucaklioglu/PyPDF-Tools.git

# 4. Upstream ile senkronize olun
git fetch upstream
git checkout main
git merge upstream/main
```

### Geliştirme Ortamını Kurma
```bash
# Sanal ortam oluşturun
python -m venv venv

# Aktivasyon
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Dependencies kurulumu
pip install --upgrade pip
pip install -e ".[dev]"

# Pre-commit hooks kurulumu
pre-commit install
```

### IDE Konfigürasyonu

#### Visual Studio Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm
- File → Settings → Project → Python Interpreter → venv/bin/python
- Enable "Format code on save"
- Code Style → Python → Import Black settings

## 🎯 Katkı Türleri

### 🐛 Bug Fix
- Mevcut hataları düzeltin
- Test ekleyin
- Regresyon kontrolü yapın

### ✨ Yeni Özellik
- GitHub Issues'da tartışın
- Design document oluşturun
- Performans etkisini değerlendirin

### 📝 Dokümantasyon
- README güncellemeleri
- Kod yorumları
- API dokümantasyonu
- Kullanıcı kılavuzu

### 🎨 UI/UX İyileştirmeleri
- Tasarım tutarlılığı
- Accessibility
- Responsive design
- Tema geliştirmeleri

### ⚡ Performans
- Bellek optimizasyonu
- Hız iyileştirmeleri
- Algoritma optimizasyonu

### 🧪 Test Coverage
- Unit testler
- Integration testler
- End-to-end testler

## 🔄 Pull Request Süreci

### 1. Branch Oluşturma
```bash
# Main'den yeni branch oluşturun
git checkout main
git pull upstream main
git checkout -b feature/amazing-feature

# Alternatif isimlendirmeler:
# feature/pdf-merge-improvement
# bugfix/memory-leak-fix
# docs/api-documentation
# refactor/code-cleanup
```

### 2. Değişiklik Yapma
```bash
# Kod değişikliklerini yapın
# Testleri çalıştırın
python -m pytest tests/ -v

# Linting kontrolü
flake8 src/
black src/
isort src/

# Pre-commit kontrolleri
pre-commit run --all-files
```

### 3. Commit Yapma
```bash
# Conventional Commits formatını kullanın
git add .
git commit -m "feat: add advanced PDF merge with bookmarks"

# Commit mesaj örnekleri:
# feat: add OCR language auto-detection
# fix: resolve memory leak in PDF processing
# docs: update installation guide for macOS
# style: apply black formatting to main.py
# refactor: optimize PDF compression algorithm
# test: add unit tests for merge functionality
# chore: update dependencies
```

### 4. Push ve PR
```bash
# Branch'i push edin
git push origin feature/amazing-feature

# GitHub'da Pull Request oluşturun
# PR template'i doldurun
# Reviewers atayın
```

### PR Template Kontrol Listesi
- [ ] **Açıklama**: Neyi değiştirdiğinizi ve neden açıklayın
- [ ] **Breaking Changes**: Varsa belirtin
- [ ] **Screenshots**: UI değişiklikleri için
- [ ] **Tests**: Yeni testler eklendi/güncellendi
- [ ] **Docs**: Dokümantasyon güncellendi
- [ ] **Performance**: Performans etki değerlendirmesi

## 📏 Kod Standartları

### Python Style Guide
```python
# PEP 8 + Black formatter kullanıyoruz

# ✅ İyi örnek
def process_pdf_file(
    input_path: str,
    output_path: str,
    compression_level: int = 6
) -> bool:
    """
    PDF dosyasını işler ve sıkıştırır.
    
    Args:
        input_path: Giriş PDF dosyası yolu
        output_path: Çıkış PDF dosyası yolu  
        compression_level: Sıkıştırma seviyesi (1-9)
        
    Returns:
        İşlem başarı durumu
        
    Raises:
        FileNotFoundError: Giriş dosyası bulunamadı
        ValueError: Geçersiz sıkıştırma seviyesi
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    if not 1 <= compression_level <= 9:
        raise ValueError("Compression level must be between 1-9")
        
    # İşleme kodu...
    return True

# ❌ Kötü örnek
def processPdf(inp,out,comp=6):
    # Dosya işleme
    pass
```

### Type Hints
```python
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# Her fonksiyon type hint'e sahip olmalı
def merge_pdfs(
    input_files: List[Union[str, Path]],
    output_file: Union[str, Path],
    bookmarks: Optional[Dict[str, Any]] = None
) -> bool:
    pass
```

### Error Handling
```python
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Custom exception'lar kullanın
class PDFProcessingError(Exception):
    """PDF işleme hatalarını temsil eder."""
    pass

# Context manager kullanın
@contextmanager
def pdf_processor(file_path: str):
    processor = None
    try:
        processor = PDFProcessor(file_path)
        yield processor
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise PDFProcessingError(f"Failed to process {file_path}") from e
    finally:
        if processor:
            processor.cleanup()
```

### Logging
```python
import logging

# Logger kullanımı
logger = logging.getLogger(__name__)

def process_file(file_path: str) -> None:
    logger.info(f"Processing file: {file_path}")
    
    try:
        # İşleme kodu
        logger.debug("PDF processing completed successfully")
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

## 🧪 Test Yazma

### Test Yapısı
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_pdf_utils.py        # PDF utility testleri  
├── test_ocr_module.py       # OCR modül testleri
├── test_ui_components.py    # UI component testleri
├── fixtures/                # Test dosyaları
│   ├── sample.pdf
│   ├── encrypted.pdf
│   └── scanned.pdf
└── integration/             # Entegrasyon testleri
    └── test_full_workflow.py
```

### Unit Test Örneği
```python
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from pypdf_tools.core.pdf_processor import PDFProcessor
from pypdf_tools.exceptions import PDFProcessingError


class TestPDFProcessor:
    """PDFProcessor class testleri."""
    
    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Test için geçici PDF dosyası oluşturur."""
        pdf_file = tmp_path / "sample.pdf"
        # PDF dosyası oluştur
        return str(pdf_file)
    
    @pytest.fixture
    def processor(self):
        """PDFProcessor instance'ı oluşturur."""
        return PDFProcessor()
    
    def test_merge_pdfs_success(self, processor, sample_pdf_path, tmp_path):
        """PDF birleştirme başarı senaryosu."""
        output_path = tmp_path / "merged.pdf"
        
        result = processor.merge_pdfs(
            [sample_pdf_path, sample_pdf_path],
            str(output_path)
        )
        
        assert result is True
        assert output_path.exists()
        
    def test_merge_pdfs_file_not_found(self, processor):
        """Dosya bulunamama hatası testi."""
        with pytest.raises(FileNotFoundError):
            processor.merge_pdfs(
                ["nonexistent.pdf"],
                "output.pdf"
            )
            
    @patch('pypdf_tools.core.pdf_processor.PyPDF2.PdfReader')
    def test_merge_pdfs_processing_error(self, mock_reader, processor):
        """PDF işleme hatası testi."""
        mock_reader.side_effect = Exception("PDF corrupted")
        
        with pytest.raises(PDFProcessingError):
            processor.merge_pdfs(["sample.pdf"], "output.pdf")
```

### Integration Test Örneği
```python
def test_full_pdf_workflow(tmp_path):
    """Tam PDF işleme workflow'u testi."""
    # Setup
    input_files = create_test_pdfs(tmp_path, count=3)
    output_file = tmp_path / "result.pdf"
    
    # Test workflow
    processor = PDFProcessor()
    
    # 1. Merge
    merged_file = tmp_path / "merged.pdf"
    processor.merge_pdfs(input_files, str(merged_file))
    
    # 2. Compress
    processor.compress_pdf(str(merged_file), str(output_file))
    
    # 3. Verify
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    assert output_file.stat().st_size < merged_file.stat().st_size
```

### Test Çalıştırma
```bash
# Tüm testler
python -m pytest tests/ -v

# Belirli test dosyası
python -m pytest tests/test_pdf_utils.py -v

# Coverage raporu
python -m pytest tests/ --cov=src/ --cov-report=html

# Paralel testler (daha hızlı)
python -m pytest tests/ -n auto
```

## 📚 Dokümantasyon

### Code Documentation
```python
def compress_pdf(
    self,
    input_path: str,
    output_path: str,
    quality: str = "medium"
) -> bool:
    """
    PDF dosyasını sıkıştırır.
    
    Bu method çeşitli sıkıştırma algoritmaları kullanarak PDF dosyasının
    boyutunu azaltır. Görsel kalitesini koruyarak maksimum sıkıştırma sağlar.
    
    Args:
        input_path: Sıkıştırılacak PDF dosyasının tam yolu
        output_path: Sıkıştırılmış dosyanın kaydedileceği yol
        quality: Sıkıştırma kalitesi ('low', 'medium', 'high')
        
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
        
    Raises:
        FileNotFoundError: Giriş dosyası bulunamadığında
        ValueError: Geçersiz kalite parametresi verildiğinde
        PDFProcessingError: PDF işleme sırasında hata oluştuğunda
        
    Example:
        >>> processor = PDFProcessor()
        >>> success = processor.compress_pdf(
        ...     "input.pdf",
        ...     "compressed.pdf", 
        ...     quality="high"
        ... )
        >>> print(f"Compression successful: {success}")
        Compression successful: True
        
    Note:
        - 'low' kalite: Maksimum sıkıştırma, düşük görsel kalite
        - 'medium' kalite: Dengeli sıkıştırma ve kalite (varsayılan)  
        - 'high' kalite: Minimal sıkıştırma, yüksek görsel kalite
        
    Version:
        Added in v2.0.0
    """
```

### API Documentation
API dokümantasyonu için Sphinx kullanıyoruz:

```bash
# Dokümantasyon oluştur
cd docs/
make html

# Canlı preview
sphinx-autobuild source build/html
```

## 🐛 Issue Bildirme

### Bug Report Template
Issues açarken şu bilgileri ekleyin:

```markdown
## Bug Tanımı
Hatanın kısa ve net tanımı

## Yeniden Üretme Adımları
1. '...' adımını yapın
2. '...' seçeneğine tıklayın  
3. '...' sonucunu görün

## Beklenen Davranış
Ne olmasını bekliyordunuz?

## Gerçek Davranış  
Aslında ne oldu?

## Sistem Bilgileri
- İşletim Sistemi: [e.g. Windows 11, Ubuntu 22.04, macOS 13]
- Python Sürümü: [e.g. 3.11.2]
- PyPDF-Tools Sürümü: [e.g. 2.0.0]
- Kurulum Yöntemi: [AppImage, .deb, .exe, source]

## Error Logs
```
Hata mesajlarını buraya yapıştırın
```

## Ekran Görüntüleri
Varsa hata ekran görüntülerini ekleyin
```

### Feature Request Template
```markdown
## Özellik Önerisi
Önerilen özelliğin kısa tanımı

## Motivasyon / Use Case
Bu özellik neden gerekli? Hangi problemi çözecek?

## Detaylı Açıklama
Özelliğin nasıl çalışmasını istiyorsunuz?

## Alternatifler
Başka çözümler düşündünüz mü?

## Implementasyon Önerileri
Teknik implementasyon hakkında fikirleriniz
```

## 📞 İletişim

### Online Topluluk
- **Discord**: [PyPDF Tools Community](https://discord.gg/pypdf-tools)
- **Telegram**: [@pypdf_tools](https://t.me/pypdf_tools)  
- **Reddit**: [r/PyPDFTools](https://reddit.com/r/PyPDFTools)

### Proje Maintainers
- **Fatih Bucaklıoğlu** (@Fatih-Bucaklioglu) - Lead Developer
- **Contributors**: Katkıda bulunanlar listesi için [Contributors](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/graphs/contributors) sayfasına bakın

### E-posta İletişim
- **Genel**: fatih@pypdf-tools.com
- **Güvenlik**: security@pypdf-tools.com
- **Kurumsal**: enterprise@pypdf-tools.com

## 🙏 Teşekkürler

Bu projeye katkıda bulunduğunuz için teşekkür ederiz! Her türlü katkı (kod, dokümantasyon, test, bug report, feature request) değerlidir.

### Katkıda Bulunanlar
Projeye katkıda bulunan herkesi [Contributors](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/graphs/contributors) sayfasında görebilirsiniz.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

---

**Sorularınız mı var?** [GitHub Discussions](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/discussions) kısmında soru sorabilirsiniz!
