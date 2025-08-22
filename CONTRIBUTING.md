# Katkı Sağlama Rehberi

PyPDF-Tools projesine katkıda bulunduğunuz için teşekkür ederiz! Bu rehber, projeye nasıl katkı sağlayabileceğiniz konusunda size yol gösterecektir.

## İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Katkı Türleri](#katkı-türleri)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Pull Request Süreci](#pull-request-süreci)
- [Kodlama Standartları](#kodlama-standartları)
- [Test Yazma](#test-yazma)
- [Dokümantasyon](#dokümantasyon)
- [Issue Raporlama](#issue-raporlama)

## Davranış Kuralları

Bu proje [Contributor Covenant](CODE_OF_CONDUCT.md) davranış kurallarını benimser. Katkıda bulunarak bu kuralları takip etmeyi kabul edersiniz.

## Katkı Türleri

### 🐛 Bug Raporları
- Beklenmeyen davranışları rapor edin
- Hata mesajlarını ve log'ları paylaşın
- Tekrarlanabilir adımlar sağlayın

### 🚀 Özellik Önerileri
- Yeni özellik fikirlerinizi paylaşın
- Kullanım senaryolarını açıklayın
- Mockup veya örnek görseller ekleyin

### 📝 Dokümantasyon
- README dosyasını geliştirin
- API dokümantasyonu ekleyin
- Tutorial ve rehberler yazın

### 💻 Kod Katkıları
- Bug düzeltmeleri
- Yeni özellik implementasyonları
- Performans iyileştirmeleri
- Test coverage artırımı

### 🌍 Çeviri
- Arayüz metinlerini çevirin
- Dokümantasyonu farklı dillere çevirin

## Geliştirme Ortamı Kurulumu

### Gereksinimler

**Python Tarafı:**
- Python 3.8 veya üzeri
- pip veya poetry
- PyQt6 ve bağımlılıkları

**React Tarafı:**
- Node.js 16 veya üzeri
- npm veya yarn

### Kurulum Adımları

1. **Repository'yi fork edin ve clone edin:**
```bash
git clone https://github.com/YOUR_USERNAME/PyPDF-Tools.git
cd PyPDF-Tools
```

2. **Python virtual environment oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

3. **Python bağımlılıklarını yükleyin:**
```bash
pip install -e ".[dev]"
```

4. **React bağımlılıklarını yükleyin:**
```bash
cd web
npm install
```

5. **React uygulamasını build edin:**
```bash
npm run build
cd ..
```

6. **Testleri çalıştırın:**
```bash
pytest
```

### Geliştirme Modu

**Python kısmı için:**
```bash
python -m pypdf_tools.main
```

**React kısmı için (development server):**
```bash
cd web
npm start
```

## Pull Request Süreci

### 1. Branch Oluşturma

```bash
git checkout -b feature/your-feature-name
# veya
git checkout -b fix/bug-description
```

**Branch adlandırma kuralları:**
- `feature/` - Yeni özellikler için
- `fix/` - Bug düzeltmeleri için
- `docs/` - Dokümantasyon için
- `refactor/` - Kod refaktörü için
- `test/` - Test ekleme/düzeltme için

### 2. Değişiklikleri Yapma

- Küçük, odaklanmış commit'ler yapın
- Açıklayıcı commit mesajları yazın
- [Conventional Commits](https://www.conventionalcommits.org/) formatını kullanın

**Commit mesaj örnekleri:**
```
feat: PDF birleştirme özelliği eklendi
fix: zoom fonksiyonundaki hata düzeltildi
docs: kurulum rehberi güncellendi
test: PDF viewer için unit testler eklendi
```

### 3. Test Etme

```bash
# Python testlerini çalıştır
pytest

# React testlerini çalıştır
cd web && npm test

# Code quality kontrolü
flake8 src/
black src/ --check
mypy src/
```

### 4. Pull Request Oluşturma

**PR şablonu:**
```markdown
## Açıklama
Bu PR'da yapılan değişikliklerin kısa açıklaması.

## Değişiklik Türü
- [ ] Bug fix
- [ ] Yeni özellik
- [ ] Breaking change
- [ ] Dokümantasyon

## Nasıl Test Edilir
1. Adım bir
2. Adım iki
3. Beklenen sonuç

## Ekran Görüntüleri
Varsa ekran görüntülerini ekleyin.

## Checklist
- [ ] Kod self-review yapıldı
- [ ] Testler eklendi/güncellendi
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md güncellendi
```

## Kodlama Standartları

### Python

**Style Guide:**
- [PEP 8](https://peps.python.org/pep-0008/) kurallarını takip edin
- [Black](https://black.readthedocs.io/) formatter kullanın
- Maximum line length: 88 karakter

**Linting:**
```bash
flake8 src/
black src/
isort src/
mypy src/
```

**Dokümantasyon:**
```python
def merge_pdfs(input_files: List[str], output: str) -> Dict[str, Any]:
    """
    Birden fazla PDF dosyasını birleştir.
    
    Args:
        input_files: Birleştirilecek PDF dosyalarının yolları
        output: Çıktı dosyasının yolu
        
    Returns:
        İşlem sonucu ve meta bilgileri içeren dictionary
        
    Raises:
        FileNotFoundError: Input dosyalarından biri bulunamazsa
        PDFMergeError: Birleştirme işleminde hata oluşursa
    """
```

### JavaScript/React

**Style Guide:**
- [Airbnb JavaScript Style Guide](https://airbnb.io/javascript/)
- [React Hook'ları](https://reactjs.org/docs/hooks-intro.html) tercih edin
- Functional component'lar kullanın

**Naming Conventions:**
```javascript
// Bileşenler PascalCase
const PDFViewer = () => {}

// Hook'lar "use" prefix ile camelCase
const useZoomControl = () => {}

// Fonksiyonlar camelCase
const handleToolAction = () => {}

// Sabitler UPPER_SNAKE_CASE
const MAX_ZOOM_LEVEL = 500
```

**PropTypes/TypeScript:**
```javascript
const PDFViewer = ({ 
  pdfData, 
  onToolAction, 
  theme = 'light',
  ...props 
}) => {
  // Component implementation
}

// PropTypes tanımlaması
PDFViewer.propTypes = {
  pdfData: PropTypes.object,
  onToolAction: PropTypes.func.isRequired,
  theme: PropTypes.oneOf(['light', 'dark', 'neon', 'midnight']),
}
```

## Test Yazma

### Python Testleri

**pytest** kullanıyoruz. Test dosyaları `tests/` dizininde.

```python
import pytest
from pypdf_tools.features.pdf_viewer import PDFViewerWidget

class TestPDFViewer:
    @pytest.fixture
    def pdf_viewer(self):
        return PDFViewerWidget()
    
    def test_initialization(self, pdf_viewer):
        assert pdf_viewer is not None
    
    def test_load_pdf_success(self, pdf_viewer):
        result = pdf_viewer.load_pdf("test_files/sample.pdf")
        assert result is True
```

**Test kategorileri:**
- Unit testler: `test_*.py`
- Integration testler: `test_*_integration.py` 
- E2E testler: `test_e2e_*.py`

### React Testleri

**Jest** ve **React Testing Library** kullanıyoruz.

```javascript
import { render, screen, fireEvent } from '@testing-library/react'
import PDFViewer from '../PDFViewer'

test('renders PDF viewer component', () => {
  render(<PDFViewer pdfData={mockPdfData} />)
  expect(screen.getByText('PDF Viewer')).toBeInTheDocument()
})

test('handles tool actions', () => {
  const mockToolAction = jest.fn()
  render(
    <PDFViewer 
      pdfData={mockPdfData} 
      onToolAction={mockToolAction} 
    />
  )
  
  fireEvent.click(screen.getByRole('button', { name: 'Zoom In' }))
  expect(mockToolAction).toHaveBeenCalledWith('zoom-in', expect.any(Object))
})
```

### Test Coverage

Minimum %80 test coverage hedefliyoruz:

```bash
# Python coverage
pytest --cov=src/pypdf_tools --cov-report=html

# JavaScript coverage  
cd web && npm test -- --coverage
```

## Dokümantasyon

### README Güncellemeleri

- Kurulum talimatları
- Kullanım örnekleri
- Screenshot'lar
- API referansı

### Code Dokümantasyonu

**Python:**
```python
class PDFProcessor:
    """PDF işleme operasyonları için ana sınıf.
    
    Bu sınıf PDF dosyalarını yükleme, işleme ve kaydetme
    operasyonlarını yönetir.
    
    Attributes:
        current_pdf: Şu anda açık olan PDF dosyası
        settings: Kullanıcı ayarları
        
    Example:
        >>> processor = PDFProcessor()
        >>> processor.load_pdf('document.pdf')
        >>> processor.merge_with('other.pdf')
    """
```

**JavaScript:**
```javascript
/**
 * PDF görüntüleme ve manipülasyon bileşeni
 * 
 * @param {Object} props - Bileşen props'ları
 * @param {Object} props.pdfData - PDF verisi
 * @param {Function} props.onToolAction - Tool action handler
 * @param {string} props.theme - UI teması
 * @returns {JSX.Element} PDF viewer bileşeni
 */
const PDFViewer = ({ pdfData, onToolAction, theme }) => {
  // Bileşen implementasyonu
}
```

## Issue Raporlama

### Bug Raporu Şablonu

```markdown
**Bug Açıklaması**
Kısa ve net bug açıklaması.

**Tekrarlama Adımları**
1. Şunu yap
2. Şunu tıkla  
3. Şunu gör
4. Hatayı gör

**Beklenen Davranış**
Ne olmasını bekliyordunuz?

**Gerçek Davranış**  
Ne oldu?

**Ekran Görüntüleri**
Varsa ekran görüntüleri ekleyin.

**Ortam Bilgileri**
- İşletim Sistemi: [Windows 11, macOS 13, Ubuntu 22.04]
- Python Sürümü: [3.9.0]
- PyQt6 Sürümü: [6.4.0]
- Node.js Sürümü: [18.0.0]
- Tarayıcı: [Chrome 108, Firefox 107, Safari 16]

**Ek Bilgi**
İlave context, log dosyaları, vb.
```

### Özellik Önerisi Şablonu

```markdown
**Özellik Özeti**
Önerilen özelliğin kısa açıklaması.

**Problem/İhtiyaç**
Hangi problemi çözüyor? Neden gerekli?

**Çözüm Önerisi**
Özelliğin nasıl çalışmasını istiyorsunuz?

**Alternatifler**
Düşündüğünüz başka çözümler var mı?

**Ek Bilgi**
Mockup'lar, benzer örnekler, referanslar.
```

## Code Review Süreci

### Reviewer İçin Checklist

- [ ] Kod style guide'a uygun mu?
- [ ] Testler eklenmiş/güncellenmiş mi?
- [ ] Dokümantasyon güncellenmiş mi?
- [ ] Performans etkisi düşünülmüş mü?
- [ ] Security açısından güvenli mi?
- [ ] Breaking change var mı?

### PR Author İçin Checklist

- [ ] Self-review yapıldı
- [ ] Tüm testler geçiyor
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md'ye eklendi
- [ ] Commit mesajları anlaşılır
- [ ] PR açıklaması yeterli detayda

## Release Süreci

1. **Version Bump**: Semantic versioning kurallarına göre
2. **CHANGELOG Update**: Yeni sürüm için changelog güncelleme  
3. **Testing**: Comprehensive test suite çalıştırma
4. **Documentation**: Release notes ve dokümantasyon
5. **Tagging**: Git tag oluşturma
6. **PyPI Release**: Package yayınlama
7. **GitHub Release**: GitHub release sayfası

## Yardım Alma

### İletişim Kanalları

- **GitHub Issues**: Teknik sorular ve bug raporları
- **GitHub Discussions**: Genel tartışmalar ve sorular  
- **Email**: fatih.bucaklioglu@example.com (maintainer)

### Faydalı Kaynaklar

**Python/PyQt:**
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

**React/JavaScript:**
- [React Documentation](https://reactjs.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Jest Testing](https://jestjs.io/docs/getting-started)

**PDF Processing:**
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [ReportLab Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

## Teşekkürler

PyPDF-Tools'a katkıda bulunan herkese teşekkür ederiz! 

Sizin katkılarınız bu projeyi daha iyi hale getiriyor. 🚀

---

> **Not**: Bu rehber sürekli güncellenir. Sorularınız veya önerileriniz için issue açmaktan çekinmeyin!
