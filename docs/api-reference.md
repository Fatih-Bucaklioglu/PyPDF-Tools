# 🔌 PyPDF-Tools v2 API Referansı

PyPDF-Tools v2'nin programatik kullanımı için kapsamlı API dokümantasyonu.

## 📋 İçindekiler

- [Kurulum](#kurulum)
- [Temel Kullanım](#temel-kullanım)
- [Core API](#core-api)
- [PDF İşleme](#pdf-işleme)
- [OCR Engine](#ocr-engine)
- [Güvenlik](#güvenlik)
- [Otomasyon](#otomasyon)
- [REST API](#rest-api)
- [CLI Interface](#cli-interface)

---

## 🚀 Kurulum

### Pip ile Kurulum

```bash
# Temel kurulum
pip install pypdf-tools

# Tüm özellikler ile
pip install pypdf-tools[all]

# Geliştirici sürümü
pip install -e git+https://github.com/Fatih-Bucaklioglu/PyPDF-Tools.git#egg=pypdf-tools
```

### İçe Aktarma

```python
# Temel modüller
from pypdf_tools import PDFProcessor, OCREngine, SecurityManager
from pypdf_tools.core import Config, EventManager
from pypdf_tools.features import ScriptEngine, AutomationEngine

# Hızlı başlangıç
import pypdf_tools as ppt
```

---

## 🎯 Temel Kullanım

### Hızlı Başlangıç

```python
from pypdf_tools import PDFProcessor

# PDF processor oluştur
pdf = PDFProcessor()

# PDF'leri birleştir
result = pdf.merge_pdfs(
    files=['document1.pdf', 'document2.pdf'],
    output='merged.pdf'
)

# PDF sıkıştır
compressed = pdf.compress_pdf(
    input_file='large_document.pdf',
    output_file='compressed.pdf',
    quality='medium'
)

print(f"Birleştirme: {'Başarılı' if result else 'Başarısız'}")
print(f"Sıkıştırılmış dosya: {compressed}")
```

### Context Manager Kullanımı

```python
from pypdf_tools import PDFProcessor

with PDFProcessor() as pdf:
    # Processor otomatik olarak yapılandırılır ve temizlenir
    result = pdf.merge_pdfs(['file1.pdf', 'file2.pdf'], 'output.pdf')
    
# Context çıkışında otomatik cleanup
```

---

## 🔧 Core API

### PDFProcessor Sınıfı

```python
class PDFProcessor:
    """Ana PDF işleme sınıfı"""
    
    def __init__(
        self,
        temp_dir: Optional[str] = None,
        max_workers: int = 4,
        memory_limit: Optional[int] = None
    ):
        """
        Args:
            temp_dir: Geçici dosyalar için dizin
            max_workers: Paralel işlem sayısı
            memory_limit: Bellek sınırı (MB)
        """
```

#### PDF Birleştirme

```python
def merge_pdfs(
    self,
    files: List[str],
    output: str,
    bookmarks: bool = True,
    metadata: bool = True,
    page_ranges: Optional[Dict[str, str]] = None
) -> bool:
    """PDF dosyalarını birleştir.
    
    Args:
        files: Birleştirilecek PDF dosyalarının yolları
        output: Çıktı dosyası yolu
        bookmarks: Yer imlerini koru (varsayılan: True)
        metadata: Metadata'yı birleştir (varsayılan: True)
        page_ranges: Dosya başına sayfa aralıkları {'file.pdf': '1-5,10-15'}
        
    Returns:
        bool: Başarılı ise True
        
    Raises:
        FileNotFoundError: Girdi dosyası bulunamadı
        PermissionError: Çıktı dosyasına yazma izni yok
        PDFError: PDF işleme hatası
        
    Example:
        >>> pdf = PDFProcessor()
        >>> success = pdf.merge_pdfs(
        ...     files=['doc1.pdf', 'doc2.pdf'],
        ...     output='merged.pdf',
        ...     page_ranges={'doc1.pdf': '1-3', 'doc2.pdf': '5-10'}
        ... )
    """
```

#### PDF Bölme

```python
def split_pdf(
    self,
    input_file: str,
    method: str = 'pages',
    **kwargs
) -> List[str]:
    """PDF dosyasını böl.
    
    Args:
        input_file: Bölünecek PDF dosyası
        method: Bölme yöntemi ('pages', 'size', 'bookmarks', 'ranges')
        **kwargs: Bölme yöntemi parametreleri
        
    Returns:
        List[str]: Oluşturulan dosyaların yolları
        
    Bölme Yöntemleri:
        pages: Her N sayfada bir böl
            - pages_per_file: int = 10
            
        size: Dosya boyutuna göre böl  
            - max_size_mb: float = 10.0
            
        bookmarks: Yer imlerine göre böl
            - level: int = 1 (hangi seviyedeki yer imleri)
            
        ranges: Sayfa aralıklarına göre böl
            - ranges: List[str] = ['1-10', '11-20']
            
    Example:
        >>> # Sayfa bazlı bölme
        >>> files = pdf.split_pdf(
        ...     'large.pdf',
        ...     method='pages',
        ...     pages_per_file=5
        ... )
        
        >>> # Boyut bazlı bölme
        >>> files = pdf.split_pdf(
        ...     'huge.pdf',
        ...     method='size',
        ...     max_size_mb=5.0
        ... )
    """
```

#### PDF Sıkıştırma

```python
def compress_pdf(
    self,
    input_file: str,
    output_file: Optional[str] = None,
    quality: str = 'medium',
    dpi: Optional[int] = None,
    jpeg_quality: Optional[int] = None,
    optimize_fonts: bool = True,
    remove_metadata: bool = False
) -> str:
    """PDF dosyasını sıkıştır.
    
    Args:
        input_file: Sıkıştırılacak dosya
        output_file: Çıktı dosyası (None ise otomatik)
        quality: Sıkıştırma kalitesi ('low'|'medium'|'high'|'maximum')
        dpi: Görüntü DPI değeri
        jpeg_quality: JPEG kalitesi (0-100)
        optimize_fonts: Font optimizasyonu
        remove_metadata: Metadata'yı kaldır
        
    Returns:
        str: Sıkıştırılmış dosya yolu
        
    Kalite Seviyeleri:
        - low: DPI=150, JPEG=95, minimal sıkıştırma
        - medium: DPI=150, JPEG=85, orta sıkıştırma  
        - high: DPI=100, JPEG=70, yüksek sıkıştırma
        - maximum: DPI=72, JPEG=50, maksimum sıkıştırma
        
    Example:
        >>> compressed = pdf.compress_pdf(
        ...     'large_document.pdf',
        ...     quality='high',
        ...     remove_metadata=True
        ... )
        >>> print(f"Sıkıştırılmış: {compressed}")
    """
```

#### Sayfa İşlemleri

```python
def rotate_pages(
    self,
    input_file: str,
    output_file: str,
    rotation: int,
    pages: Optional[List[int]] = None
) -> bool:
    """PDF sayfalarını döndür.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası
        rotation: Döndürme açısı (90, 180, 270, -90)
        pages: Döndürülecek sayfalar (None=tümü)
        
    Example:
        >>> pdf.rotate_pages('doc.pdf', 'rotated.pdf', 90, pages=[1,3,5])
    """

def reorder_pages(
    self,
    input_file: str,
    output_file: str,
    page_order: List[int]
) -> bool:
    """PDF sayfalarını yeniden sırala.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası  
        page_order: Yeni sayfa sırası [2,1,4,3]
        
    Example:
        >>> # İlk iki sayfayı yer değiştir
        >>> pdf.reorder_pages('doc.pdf', 'reordered.pdf', [2,1,3,4,5])
    """

def extract_pages(
    self,
    input_file: str,
    output_file: str,
    pages: List[int]
) -> bool:
    """Belirli sayfaları çıkart.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası
        pages: Çıkartılacak sayfa numaraları
        
    Example:
        >>> pdf.extract_pages('doc.pdf', 'pages_1_3_5.pdf', [1,3,5])
    """
```

### Metadata İşlemleri

```python
def get_metadata(self, file_path: str) -> Dict[str, Any]:
    """PDF metadata'sını al.
    
    Returns:
        Dict: Metadata bilgileri
        {
            'title': str,
            'author': str, 
            'subject': str,
            'creator': str,
            'producer': str,
            'creation_date': datetime,
            'modification_date': datetime,
            'page_count': int,
            'file_size': int,
            'is_encrypted': bool,
            'permissions': Dict[str, bool]
        }
    """

def set_metadata(
    self,
    input_file: str,
    output_file: str,
    metadata: Dict[str, Any]
) -> bool:
    """PDF metadata'sını düzenle.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası
        metadata: Yeni metadata bilgileri
        
    Example:
        >>> pdf.set_metadata('doc.pdf', 'updated.pdf', {
        ...     'title': 'Yeni Başlık',
        ...     'author': 'Yazar Adı',
        ...     'subject': 'Konu'
        ... })
    """

def remove_metadata(
    self,
    input_file: str,
    output_file: str,
    keep_fields: Optional[List[str]] = None
) -> bool:
    """PDF metadata'sını temizle.
    
    Args:
        input_file: Girdi dosyası  
        output_file: Çıktı dosyası
        keep_fields: Korunacak alanlar
        
    Example:
        >>> pdf.remove_metadata('doc.pdf', 'clean.pdf', keep_fields=['title'])
    """
```

---

## 🔍 OCR Engine

### OCREngine Sınıfı

```python
class OCREngine:
    """OCR işleme motoru"""
    
    def __init__(
        self,
        tesseract_path: Optional[str] = None,
        language_data_path: Optional[str] = None
    ):
        """
        Args:
            tesseract_path: Tesseract binary yolu
            language_data_path: Dil veri dosyaları yolu
        """

    def process_pdf(
        self,
        input_file: str,
        output_file: str,
        language: str = 'eng',
        dpi: int = 300,
        preprocess: bool = True,
        preserve_layout: bool = True
    ) -> bool:
        """PDF'e OCR uygula.
        
        Args:
            input_file: Taranmış PDF dosyası
            output_file: Aranabilir PDF dosyası
            language: OCR dili (örn: 'tur', 'eng', 'tur+eng')
            dpi: Görüntü çözünürlüğü
            preprocess: Görüntü ön işleme
            preserve_layout: Layout koruma
            
        Returns:
            bool: Başarılı ise True
            
        Example:
            >>> ocr = OCREngine()
            >>> success = ocr.process_pdf(
            ...     'scanned.pdf',
            ...     'searchable.pdf', 
            ...     language='tur+eng',
            ...     dpi=300
            ... )
        """

    def extract_text(
        self,
        input_file: str,
        language: str = 'eng',
        pages: Optional[List[int]] = None
    ) -> str:
        """PDF'den metin çıkart.
        
        Args:
            input_file: PDF dosyası
            language: OCR dili
            pages: İşlenecek sayfalar (None=tümü)
            
        Returns:
            str: Çıkartılan metin
            
        Example:
            >>> text = ocr.extract_text('document.pdf', 'tur')
            >>> print(text[:100])
        """

    def get_text_with_positions(
        self,
        input_file: str,
        language: str = 'eng',
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Metin ve konumlarını al.
        
        Returns:
            List[Dict]: Her kelime için konum bilgisi
            [
                {
                    'text': str,
                    'confidence': float,
                    'bbox': (x, y, width, height),
                    'page': int
                }
            ]
        """

    def detect_language(
        self,
        input_file: str,
        page: int = 1
    ) -> Dict[str, float]:
        """Otomatik dil algılama.
        
        Returns:
            Dict[str, float]: Dil ve güven skoru
            {'tur': 0.85, 'eng': 0.15}
        """
```

### Dil Yönetimi

```python
from pypdf_tools.features import LanguageInstaller

# Dil yöneticisi
lang_installer = LanguageInstaller()

# Mevcut diller
available = lang_installer.get_available_languages()
for lang in available:
    print(f"{lang.code}: {lang.name} ({'✓' if lang.installed else '✗'})")

# Dil kurulumu
success = lang_installer.install_language('deu')  # Almanca
if success:
    print("Almanca dil paketi kuruldu!")

# Çoklu dil kurulumu
results = lang_installer.install_multiple_languages(['fra', 'spa', 'ita'])
for lang_code, result in results.items():
    status = "✓" if result else "✗"
    print(f"{lang_code}: {status}")
```

---

## 🔐 Güvenlik

### SecurityManager Sınıfı

```python
class SecurityManager:
    """PDF güvenlik yönetimi"""
    
    def encrypt_pdf(
        self,
        input_file: str,
        output_file: str,
        user_password: Optional[str] = None,
        owner_password: Optional[str] = None,
        permissions: Optional[Dict[str, bool]] = None,
        encryption_algorithm: str = 'AES-256'
    ) -> bool:
        """PDF dosyasını şifrele.
        
        Args:
            input_file: Girdi dosyası
            output_file: Şifreli çıktı dosyası
            user_password: Kullanıcı şifresi (açmak için)
            owner_password: Sahip şifresi (izinler için)
            permissions: İzin ayarları
            encryption_algorithm: Şifreleme algoritması
            
        Permissions:
            {
                'print': bool,           # Yazdırma
                'modify': bool,          # Değiştirme
                'copy': bool,            # Kopyalama
                'annotate': bool,        # Not ekleme
                'fill_forms': bool,      # Form doldurma
                'extract_for_accessibility': bool,
                'assemble': bool,        # Sayfa birleştirme
                'print_high_quality': bool
            }
            
        Example:
            >>> security = SecurityManager()
            >>> success = security.encrypt_pdf(
            ...     'document.pdf',
            ...     'encrypted.pdf',
            ...     user_password='user123',
            ...     owner_password='owner456',
            ...     permissions={
            ...         'print': True,
            ...         'copy': False,
            ...         'modify': False
            ...     }
            ... )
        """

    def decrypt_pdf(
        self,
        input_file: str,
        output_file: str,
        password: str
    ) -> bool:
        """PDF şifresini kaldır.
        
        Args:
            input_file: Şifreli PDF
            output_file: Şifresiz PDF
            password: PDF şifresi
        """

    def is_encrypted(self, file_path: str) -> bool:
        """PDF'in şifreli olup olmadığını kontrol et."""

    def get_permissions(self, file_path: str) -> Dict[str, bool]:
        """PDF izinlerini al."""

    def sign_pdf(
        self,
        input_file: str,
        output_file: str,
        certificate_path: str,
        certificate_password: str,
        signature_field: Optional[Tuple[int, int, int, int]] = None,
        reason: str = 'Document signing',
        location: str = 'PyPDF-Tools'
    ) -> bool:
        """PDF'i dijital olarak imzala.
        
        Args:
            input_file: İmzalanacak PDF
            output_file: İmzalı PDF  
            certificate_path: Sertifika dosyası (.p12)
            certificate_password: Sertifika şifresi
            signature_field: İmza alanı koordinatları (x, y, width, height)
            reason: İmzalama nedeni
            location: İmzalama yeri
            
        Example:
            >>> success = security.sign_pdf(
            ...     'contract.pdf',
            ...     'signed_contract.pdf',
            ...     'certificate.p12',
            ...     'cert_password',
            ...     signature_field=(100, 100, 200, 50)
            ... )
        """

    def verify_signature(
        self,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Dijital imzaları doğrula.
        
        Returns:
            List[Dict]: İmza bilgileri
            [
                {
                    'valid': bool,
                    'signer': str,
                    'date': datetime,
                    'reason': str,
                    'location': str,
                    'certificate_info': dict
                }
            ]
        """
```

---

## 🎨 PDF Düzenleme

### Filigran (Watermark) İşlemleri

```python
def add_watermark(
    self,
    input_file: str,
    output_file: str,
    watermark_text: Optional[str] = None,
    watermark_image: Optional[str] = None,
    position: str = 'center',
    opacity: float = 0.5,
    rotation: int = 0,
    font_size: int = 24,
    font_color: str = 'red'
) -> bool:
    """PDF'e filigran ekle.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası
        watermark_text: Filigran metni
        watermark_image: Filigran görüntüsü yolu
        position: Konum ('center'|'top-left'|'top-right'|'bottom-left'|'bottom-right')
        opacity: Şeffaflık (0.0-1.0)
        rotation: Döndürme açısı
        font_size: Font boyutu (sadece metin için)
        font_color: Font rengi (sadece metin için)
        
    Example:
        >>> # Metin filigranı
        >>> pdf.add_watermark(
        ...     'document.pdf',
        ...     'watermarked.pdf',
        ...     watermark_text='TASLAK',
        ...     position='center',
        ...     opacity=0.3,
        ...     rotation=45
        ... )
        
        >>> # Görüntü filigranı
        >>> pdf.add_watermark(
        ...     'document.pdf',
        ...     'watermarked.pdf',
        ...     watermark_image='logo.png',
        ...     position='top-right',
        ...     opacity=0.7
        ... )
    """
```

### Sayfa Numaralama

```python
def add_page_numbers(
    self,
    input_file: str,
    output_file: str,
    position: str = 'bottom-center',
    format_string: str = 'Page {page}',
    start_page: int = 1,
    font_size: int = 12,
    font_color: str = 'black',
    margin: int = 50
) -> bool:
    """Sayfa numarası ekle.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası
        position: Konum
        format_string: Format (örn: '{page}/{total}', 'Sayfa {page}')
        start_page: Başlangıç sayfa numarası
        font_size: Font boyutu
        font_color: Font rengi
        margin: Kenar boşluğu
        
    Example:
        >>> pdf.add_page_numbers(
        ...     'document.pdf',
        ...     'numbered.pdf',
        ...     format_string='Sayfa {page} / {total}',
        ...     position='bottom-center'
        ... )
    """
```

### Üstbilgi/Altbilgi

```python
def add_header_footer(
    self,
    input_file: str,
    output_file: str,
    header_left: Optional[str] = None,
    header_center: Optional[str] = None,
    header_right: Optional[str] = None,
    footer_left: Optional[str] = None,
    footer_center: Optional[str] = None,
    footer_right: Optional[str] = None,
    font_size: int = 10,
    margin: int = 30
) -> bool:
    """Üstbilgi ve altbilgi ekle.
    
    Format Değişkenleri:
        {page}: Mevcut sayfa
        {total}: Toplam sayfa
        {date}: Bugünün tarihi
        {time}: Şu anki saat
        {filename}: Dosya adı
        
    Example:
        >>> pdf.add_header_footer(
        ...     'document.pdf',
        ...     'with_headers.pdf',
        ...     header_left='Şirket Adı',
        ...     header_right='{date}',
        ...     footer_center='Sayfa {page} / {total}',
        ...     footer_right='© 2024'
        ... )
    """
```

---

## ⚙️ Otomasyon

### AutomationEngine Sınıfı

```python
from pypdf_tools.features import AutomationEngine

class AutomationEngine:
    """PDF işleme otomasyonu"""
    
    def __init__(self):
        self.rules = []
        self.running = False
    
    def add_folder_rule(
        self,
        folder_path: str,
        file_pattern: str = '*.pdf',
        action: str = 'compress',
        output_folder: Optional[str] = None,
        **action_params
    ) -> str:
        """Klasör izleme kuralı ekle.
        
        Args:
            folder_path: İzlenecek klasör
            file_pattern: Dosya deseni (glob)
            action: Yapılacak işlem
            output_folder: Çıktı klasörü
            **action_params: İşlem parametreleri
            
        Returns:
            str: Kural ID'si
            
        Desteklenen İşlemler:
            - compress: PDF sıkıştırma
            - ocr: OCR işlemi
            - encrypt: Şifreleme
            - split: Bölme
            - merge: Birleştirme (çoklu dosya)
            
        Example:
            >>> automation = AutomationEngine()
            >>> rule_id = automation.add_folder_rule(
            ...     folder_path='~/Downloads',
            ...     file_pattern='scan_*.pdf',
            ...     action='ocr',
            ...     output_folder='~/Documents/OCR',
            ...     language='tur+eng',
            ...     dpi=300
            ... )
        """
    
    def add_schedule_rule(
        self,
        schedule: str,
        action: str,
        target_path: str,
        **action_params
    ) -> str:
        """Zamanlanmış görev ekle.
        
        Args:
            schedule: Cron formatında zamanlama
            action: Yapılacak işlem
            target_path: Hedef yol
            **action_params: İşlem parametreleri
            
        Schedule Formatı (Cron):
            "0 2 * * *"     # Her gün saat 02:00
            "0 */6 * * *"   # Her 6 saatte bir
            "0 9 * * 1-5"   # Hafta içi her gün 09:00
            
        Example:
            >>> # Her gece klasörü temizle
            >>> automation.add_schedule_rule(
            ...     schedule='0 2 * * *',
            ...     action='cleanup',
            ...     target_path='~/temp_pdfs',
            ...     older_than_days=7
            ... )
        """
    
    def start(self):
        """Otomasyon motorunu başlat."""
        
    def stop(self):
        """Otomasyon motorunu durdur."""
        
    def get_rule_status(self, rule_id: str) -> Dict[str, Any]:
        """Kural durumunu al."""
```

### Toplu İşlem API'si

```python
def batch_process(
    self,
    files: List[str],
    action: str,
    output_dir: str,
    parallel: bool = True,
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable] = None,
    **action_params
) -> Dict[str, Any]:
    """Toplu dosya işleme.
    
    Args:
        files: İşlenecek dosya listesi
        action: Yapılacak işlem
        output_dir: Çıktı dizini
        parallel: Paralel işlem
        max_workers: Maksimum worker sayısı
        progress_callback: İlerleme callback'i
        **action_params: İşlem parametreleri
        
    Returns:
        Dict: İşlem sonuçları
        {
            'successful': List[str],
            'failed': List[str],
            'total_time': float,
            'results': Dict[str, Any]
        }
        
    Example:
        >>> def progress_update(current, total, file_name):
        ...     print(f"{current}/{total}: {file_name}")
        
        >>> results = pdf.batch_process(
        ...     files=['doc1.pdf', 'doc2.pdf', 'doc3.pdf'],
        ...     action='compress',
        ...     output_dir='./compressed/',
        ...     quality='medium',
        ...     progress_callback=progress_update
        ... )
        
        >>> print(f"Başarılı: {len(results['successful'])}")
        >>> print(f"Başarısız: {len(results['failed'])}")
    """
```

---

## 🌐 REST API

### API Sunucusu

```python
from pypdf_tools.api import APIServer

# API sunucusunu başlat
server = APIServer(
    host='0.0.0.0',
    port=8080,
    debug=False
)

server.run()
```

```bash
# Komut satırından
pypdf-tools api --port 8080 --host localhost
```

### Endpoint'ler

#### PDF Birleştirme

```http
POST /api/merge
Content-Type: multipart/form-data

files: file1.pdf, file2.pdf
bookmarks: true
metadata: true
```

```python
import requests

files = [
    ('files', open('file1.pdf', 'rb')),
    ('files', open('file2.pdf', 'rb'))
]

response = requests.post(
    'http://localhost:8080/api/merge',
    files=files,
    data={
        'bookmarks': 'true',
        'metadata': 'true'
    }
)

if response.status_code == 200:
    with open('merged.pdf', 'wb') as f:
        f.write(response.content)
```

#### PDF Sıkıştırma

```http
POST /api/compress
Content-Type: multipart/form-data

file: document.pdf
quality: medium
dpi: 150
```

```python
response = requests.post(
    'http://localhost:8080/api/compress',
    files={'file': open('large_document.pdf', 'rb')},
    data={
        'quality': 'medium',
        'dpi': '150',
        'optimize_fonts': 'true'
    }
)
```

#### OCR İşlemi

```http
POST /api/ocr  
Content-Type: multipart/form-data

file: scanned.pdf
language: tur+eng
dpi: 300
preprocess: true
```

#### Batch İşlem

```http
POST /api/batch
Content-Type: application/json

{
    "action": "compress",
    "files": ["file1.pdf", "file2.pdf"],
    "parameters": {
        "quality": "medium"
    },
    "parallel": true
}
```

### WebSocket API

```python
import asyncio
import websockets
import json

async def batch_process_websocket():
    uri = "ws://localhost:8080/ws/batch"
    
    async with websockets.connect(uri) as websocket:
        # İşlem başlat
        request = {
            "action": "compress",
            "files": ["file1.pdf", "file2.pdf"],
            "parameters": {"quality": "medium"}
        }
        
        await websocket.send(json.dumps(request))
        
        # İlerleme dinle
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'progress':
                print(f"İlerleme: {data['current']}/{data['total']}")
                
            elif data['type'] == 'complete':
                print("Tamamlandı!")
                break
                
            elif data['type'] == 'error':
                print(f"Hata: {data['message']}")
                break

asyncio.run(batch_process_websocket())
```

---

## 💻 CLI Interface

### Temel Komutlar

```bash
# Yardım
pypdf-tools --help
pypdf-tools merge --help

# Sürüm
pypdf-tools --version

# Sistem bilgisi
pypdf-tools --system-info
```

### PDF Birleştirme

```bash
# Basit birleştirme
pypdf-tools merge file1.pdf file2.pdf -o merged.pdf

# Yer imleri olmadan
pypdf-tools merge *.pdf -o combined.pdf --no-bookmarks

# Sayfa aralıkları ile
pypdf-tools merge doc1.pdf[1-5] doc2.pdf[10-15] -o selected.pdf
```

### PDF Bölme

```bash
# Sayfa bazlı bölme
pypdf-tools split large.pdf -p 5 -o split_

# Boyut bazlı bölme  
pypdf-tools split huge.pdf --max-size 10MB -o parts_

# Yer imi bazlı bölme
pypdf-tools split document.pdf --by-bookmarks -o chapters_
```

### Sıkıştırma

```bash
# Orta kalite sıkıştırma
pypdf-tools compress large.pdf -q medium -o compressed.pdf

# Maksimum sıkıştırma
pypdf-tools compress *.pdf -q maximum --batch --output-dir ./compressed/

# Özel ayarlar
pypdf-tools compress doc.pdf --dpi 100 --jpeg-quality 70 -o small.pdf
```

### OCR

```bash
# Temel OCR
pypdf-tools ocr scanned.pdf -l tur -o searchable.pdf

# Çoklu dil
pypdf-tools ocr document.pdf -l tur+eng --dpi 300 -o ocr.pdf

# Toplu OCR
pypdf-tools ocr scanned_*.pdf -l tur --batch --output-dir ./ocr/
```

### Güvenlik

```bash
# Şifreleme
pypdf-tools encrypt document.pdf -u userpass -o encrypted.pdf

# İzinli şifreleme
pypdf-tools encrypt doc.pdf -u user -w owner --no-print --no-copy

# Şifre kaldırma  
pypdf-tools decrypt encrypted.pdf -p password -o decrypted.pdf
```

### Toplu İşlemler

```bash
# Klasördeki tüm PDF'leri sıkıştır
pypdf-tools batch compress ./input/*.pdf --output-dir ./output/ -q medium

# OCR toplu işlem
pypdf-tools batch ocr ./scanned/*.pdf -l tur --output-dir ./searchable/

# Pipeline (birleştir → sıkıştır → OCR)
pypdf-tools pipeline \
  --merge "*.pdf" \
  --compress "quality=medium" \
  --ocr "language=tur" \
  --output final.pdf
```

---

## 📊 Olay Sistemi (Events)

```python
from pypdf_tools.core import EventManager

events = EventManager()

# Event listener kayıt
@events.on('pdf_processing_started')
def on_processing_started(event_data):
    print(f"İşlem başladı: {event_data['operation']}")
    print(f"Dosya: {event_data['file']}")

@events.on('pdf_processing_completed')  
def on_processing_completed(event_data):
    print(f"İşlem tamamlandı: {event_data['operation']}")
    print(f"Süre: {event_data['duration']:.2f}s")

@events.on('pdf_processing_progress')
def on_progress(event_data):
    progress = event_data['progress']
    print(f"İlerleme: %{progress:.1f}")

# Multiple listeners
@events.on(['pdf_encrypted', 'pdf_decrypted'])
def on_security_event(event_data):
    print(f"Güvenlik işlemi: {event_data['type']}")

# Event emit (otomatik olarak yapılır)
events.emit('pdf_processing_started', {
    'operation': 'compress',
    'file': 'document.pdf'
})

# Event listener kaldırma
events.off('pdf_processing_started', on_processing_started)

# Tüm listener'ları kaldır
events.clear('pdf_processing_completed')
```

---

## 🔧 Konfigürasyon

```python
from pypdf_tools.core import Config

config = Config()

# Ayar okuma
output_dir = config.get('processing.default_output_dir', '~/Documents')
quality = config.get('compression.default_quality', 'medium')

# Ayar yazma
config.set('ocr.default_language', 'tur')
config.set('ui.theme', 'dark')

# Nested ayarlar
config.set('automation.email_notifications', {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'port': 587
})

# Ayarları kaydet
config.save()

# Ayar dosyası yolu
print(f"Config dosyası: {config.config_file}")

# Ayar izleme
@config.watch('ui.theme')
def on_theme_changed(old_value, new_value):
    print(f"Tema değişti: {old_value} -> {new_value}")

# Tüm ayarları al
all_settings = config.all()
print(json.dumps(all_settings, indent=2))
```

---

## 🚨 Hata Yönetimi

### Custom Exception'lar

```python
from pypdf_tools.exceptions import (
    PDFError,
    OCRError,
    SecurityError,
    ValidationError,
    ProcessingError
)

try:
    pdf = PDFProcessor()
    result = pdf.merge_pdfs(['file1.pdf', 'file2.pdf'], 'output.pdf')
    
except FileNotFoundError as e:
    print(f"Dosya bulunamadı: {e}")
    
except PermissionError as e:
    print(f"Dosya izin hatası: {e}")
    
except PDFError as e:
    print(f"PDF işleme hatası: {e}")
    print(f"Hata kodu: {e.error_code}")
    print(f"Ayrıntılar: {e.details}")
    
except ProcessingError as e:
    print(f"İşlem hatası: {e}")
    if e.partial_results:
        print("Kısmi sonuçlar mevcut")
```

### Logging

```python
import logging
from pypdf_tools.core.logging import get_logger

# Logger al
logger = get_logger(__name__)

# Log seviyeleri
logger.debug("Detay bilgi")
logger.info("Genel bilgi") 
logger.warning("Uyarı")
logger.error("Hata")
logger.critical("Kritik hata")

# Structured logging
logger.info("PDF işlendi", extra={
    'file': 'document.pdf',
    'operation': 'compress',
    'duration': 2.5,
    'input_size': 1024000,
    'output_size': 512000
})
```

---

Bu API dokümantasyonu sürekli güncellenmektedir. En güncel versiyonu için [GitHub](https://github.com/Fatih-Bucaklioglu/PyPDF-Tools) sayfasını ziyaret edin.
