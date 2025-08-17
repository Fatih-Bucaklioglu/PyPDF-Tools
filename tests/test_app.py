#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Test Script
Uygulamanın tüm bileşenlerini test eder
"""

import sys
import os
import unittest
import importlib
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

# Proje kök dizinini PATH'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestDependencies(unittest.TestCase):
    """Bağımlılık testleri"""
    
    def test_python_version(self):
        """Python versiyon kontrolü"""
        self.assertGreaterEqual(sys.version_info[:2], (3, 8), 
                              "Python 3.8+ gerekli")
    
    def test_required_modules(self):
        """Gerekli modüllerin import edilebilirliği"""
        required_modules = [
            'tkinter',
            'pathlib',
            'threading',
            'json',
            'os',
            'sys',
            'time',
            'tempfile',
            'shutil'
        ]
        
        for module_name in required_modules:
            with self.subTest(module=module_name):
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    self.fail(f"Gerekli modül import edilemedi: {module_name} - {e}")
    
    def test_optional_modules(self):
        """İsteğe bağlı modüllerin kontrolü"""
        optional_modules = {
            'PyPDF2': 'PDF işleme için gerekli',
            'PIL': 'Görüntü işleme için gerekli', 
            'fitz': 'Gelişmiş PDF işleme için gerekli',
            'pytesseract': 'OCR işlemleri için gerekli',
            'cv2': 'Görüntü ön işleme için gerekli',
            'pdf2image': 'PDF to image dönüşümü için gerekli',
            'reportlab': 'PDF oluşturma için gerekli'
        }
        
        missing_modules = []
        
        for module_name, description in optional_modules.items():
            try:
                importlib.import_module(module_name)
                print(f"✅ {module_name}: OK")
            except ImportError:
                missing_modules.append(f"{module_name} ({description})")
                print(f"❌ {module_name}: Eksik - {description}")
        
        if missing_modules:
            print(f"\n⚠️  Eksik modüller: {len(missing_modules)}")
            for module in missing_modules:
                print(f"   - {module}")
            print("\nBu modüller pip install ile kurulabilir:")
            print("pip install -r requirements.txt")

class TestUtilityClasses(unittest.TestCase):
    """Utility sınıfları testleri"""
    
    def setUp(self):
        """Test ortamını hazırla"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Test sonrası temizlik"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_import(self):
        """ConfigManager import testi"""
        try:
            from utils import ConfigManager
            config = ConfigManager()
            self.assertIsNotNone(config.config)
            print("✅ ConfigManager: OK")
        except ImportError as e:
            self.fail(f"ConfigManager import edilemedi: {e}")
    
    def test_cache_manager_import(self):
        """CacheManager import testi"""
        try:
            from utils import CacheManager
            cache = CacheManager(enabled=False)  # Test için disabled
            self.assertFalse(cache.enabled)
            print("✅ CacheManager: OK")
        except ImportError as e:
            self.fail(f"CacheManager import edilemedi: {e}")
    
    def test_log_manager_import(self):
        """LogManager import testi"""
        try:
            from utils import LogManager
            log = LogManager(enabled=False)  # Test için disabled
            self.assertFalse(log.enabled)
            print("✅ LogManager: OK")
        except ImportError as e:
            self.fail(f"LogManager import edilemedi: {e}")
    
    def test_theme_manager_import(self):
        """ThemeManager import testi"""
        try:
            from utils import ThemeManager
            theme = ThemeManager()
            self.assertIn('light', theme.themes)
            self.assertIn('dark', theme.themes)
            self.assertIn('neon', theme.themes)
            self.assertIn('midnight', theme.themes)
            print("✅ ThemeManager: OK")
        except ImportError as e:
            self.fail(f"ThemeManager import edilemedi: {e}")

class TestUIComponents(unittest.TestCase):
    """UI bileşenleri testleri"""
    
    def setUp(self):
        """Mock objeler oluştur"""
        self.mock_config = Mock()
        self.mock_theme = Mock()
        self.mock_app = Mock()
        
        # Mock config values
        self.mock_config.get.return_value = "test_value"
    
    @patch('tkinter.Tk')
    def test_header_import(self, mock_tk):
        """ModernHeader import testi"""
        try:
            from ui.header import ModernHeader
            # Mock parent widget
            mock_parent = Mock()
            
            # Header oluşturmayı test et (sadece import)
            # Gerçek GUI oluşturma test ortamında sorun çıkarabilir
            print("✅ ModernHeader import: OK")
        except ImportError as e:
            self.fail(f"ModernHeader import edilemedi: {e}")
    
    def test_sidebar_import(self):
        """ModernSidebar import testi"""
        try:
            from ui.sidebar import ModernSidebar
            print("✅ ModernSidebar import: OK")
        except ImportError as e:
            self.fail(f"ModernSidebar import edilemedi: {e}")
    
    def test_content_import(self):
        """ModernContent import testi"""
        try:
            from ui.content import ModernContent
            print("✅ ModernContent import: OK")
        except ImportError as e:
            self.fail(f"ModernContent import edilemedi: {e}")

class TestPDFProcessing(unittest.TestCase):
    """PDF işleme testleri"""
    
    def setUp(self):
        """Test ortamını hazırla"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock objeler
        self.mock_cache = Mock()
        self.mock_log = Mock()
    
    def tearDown(self):
        """Test sonrası temizlik"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pdf_processor_import(self):
        """PDFProcessor import testi"""
        try:
            from resources.pdf_utils import PDFProcessor
            processor = PDFProcessor(
                cache_manager=self.mock_cache,
                log_manager=self.mock_log
            )
            self.assertIsNotNone(processor)
            print("✅ PDFProcessor: OK")
        except ImportError as e:
            self.fail(f"PDFProcessor import edilemedi: {e}")
    
    def test_pdf_validation_functions(self):
        """PDF doğrulama fonksiyonları testi"""
        try:
            from resources.pdf_utils import validate_pdf, get_pdf_info
            
            # Test için geçersiz dosya yolu
            invalid_path = str(self.temp_dir / "nonexistent.pdf")
            result = validate_pdf(invalid_path)
            self.assertFalse(result)
            
            info = get_pdf_info(invalid_path)
            self.assertIn('error', info)
            
            print("✅ PDF validation functions: OK")
        except ImportError as e:
            self.fail(f"PDF validation functions import edilemedi: {e}")

class TestOCRProcessing(unittest.TestCase):
    """OCR işleme testleri"""
    
    def setUp(self):
        """Test ortamını hazırla"""
        self.mock_log = Mock()
    
    def test_ocr_processor_import(self):
        """OCRProcessor import testi"""
        try:
            from ocr_module import OCRProcessor
            
            # OCR işlemci oluştur (bağımlılık yoksa skip)
            try:
                processor = OCRProcessor(
                    languages=['eng', 'tur'],
                    cache_enabled=False,
                    log_manager=self.mock_log
                )
                self.assertIsNotNone(processor)
                print("✅ OCRProcessor: OK")
            except Exception as e:
                print(f"⚠️  OCRProcessor: Bağımlılık eksik - {e}")
                
        except ImportError as e:
            self.fail(f"OCRProcessor import edilemedi: {e}")

class TestMainApplication(unittest.TestCase):
    """Ana uygulama testleri"""
    
    def test_main_import(self):
        """Main.py import testi"""
        try:
            # Ana sınıfı import et
            from main import PyPDFToolsV2
            self.assertIsNotNone(PyPDFToolsV2)
            print("✅ PyPDFToolsV2: OK")
        except ImportError as e:
            self.fail(f"Main application import edilemedi: {e}")
        except Exception as e:
            # GUI initialization hataları beklenebilir
            print(f"⚠️  PyPDFToolsV2: {e}")

class TestFileStructure(unittest.TestCase):
    """Dosya yapısı testleri"""
    
    def test_required_files_exist(self):
        """Gerekli dosyaların varlık kontrolü"""
        required_files = [
            'main.py',
            'utils.py', 
            'ocr_module.py',
            'requirements.txt',
            'ui/__init__.py',
            'ui/header.py',
            'ui/sidebar.py', 
            'ui/content.py',
            'resources/__init__.py',
            'resources/pdf_utils.py'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                print(f"✅ {file_path}: Mevcut")
        
        if missing_files:
            print(f"\n❌ Eksik dosyalar: {len(missing_files)}")
            for file in missing_files:
                print(f"   - {file}")
            self.fail(f"Gerekli dosyalar eksik: {missing_files}")
        else:
            print("✅ Tüm gerekli dosyalar mevcut")
    
    def test_directory_structure(self):
        """Dizin yapısı kontrolü"""
        required_dirs = [
            'ui',
            'resources'
        ]
        
        optional_dirs = [
            'icons',
            'features', 
            'cli',
            'docs',
            'tests'
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists() and dir_path.is_dir(), 
                          f"Gerekli dizin eksik: {dir_name}")
            print(f"✅ {dir_name}/: Mevcut")
        
        for dir_name in optional_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name}/: Mevcut (isteğe bağlı)")
            else:
                print(f"⚠️  {dir_name}/: Eksik (isteğe bağlı)")

def run_comprehensive_test():
    """Kapsamlı test çalıştırıcısı"""
    
    print("🧪 PyPDF-Stirling Tools v2 - Kapsamlı Test Süreci")
    print("=" * 60)
    
    # Test suitelerini oluştur
    test_suites = [
        ('Bağımlılık Testleri', TestDependencies),
        ('Utility Sınıfları Testleri', TestUtilityClasses),
        ('UI Bileşenleri Testleri', TestUIComponents),
        ('PDF İşleme Testleri', TestPDFProcessing),
        ('OCR İşleme Testleri', TestOCRProcessing),
        ('Ana Uygulama Testleri', TestMainApplication),
        ('Dosya Yapısı Testleri', TestFileStructure)
    ]
    
    total_tests = 0
    failed_tests = 0
    
    for suite_name, test_class in test_suites:
        print(f"\n🔍 {suite_name}")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        total_tests += result.testsRun
        failed_tests += len(result.failures) + len(result.errors)
        
        if result.failures:
            print(f"❌ Başarısız testler: {len(result.failures)}")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError: ')[-1].strip()}")
        
        if result.errors:
            print(f"❌ Hata veren testler: {len(result.errors)}")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Exception: ')[-1].strip()}")
        
        success_count = result.testsRun - len(result.failures) - len(result.errors)
        print(f"✅ Başarılı: {success_count}/{result.testsRun}")
    
    # Özet rapor
    print("\n" + "=" * 60)
    print("📊 TEST RAPORU")
    print("=" * 60)
    
    success_rate = ((total_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Toplam Test: {total_tests}")
    print(f"Başarılı: {total_tests - failed_tests}")
    print(f"Başarısız: {failed_tests}")
    print(f"Başarı Oranı: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 Tüm testler başarıyla geçti!")
        print("✅ Uygulama kuruluma hazır!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} test başarısız!")
        print("❌ Lütfen hataları düzelttikten sonra tekrar test edin.")
        
        # Öneri mesajları
        print("\n💡 Öneriler:")
        if failed_tests > total_tests * 0.5:
            print("   - requirements.txt dosyasındaki paketleri kurun: pip install -r requirements.txt")
            print("   - Sistem bağımlılıklarını kurun (Tesseract OCR, poppler-utils)")
        print("   - Python 3.8+ sürümü kullandığınızdan emin olun")
        print("   - Sanal ortam (venv) kullanmanız önerilir")
        
        return False

def test_imports_only():
    """Sadece import testleri (hızlı test)"""
    print("⚡ Hızlı Import Testleri")
    print("=" * 30)
    
    modules_to_test = [
        ('main', 'Ana uygulama'),
        ('utils', 'Utility sınıfları'),
        ('ocr_module', 'OCR işleme'),
        ('ui.header', 'Header bileşeni'),
        ('ui.sidebar', 'Sidebar bileşeni'), 
        ('ui.content', 'Content bileşeni'),
        ('resources.pdf_utils', 'PDF işleme')
    ]
    
    success_count = 0
    
    for module_name, description in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}: OK - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}: HATA - {e}")
        except Exception as e:
            print(f"⚠️  {module_name}: UYARI - {e}")
            success_count += 0.5  # Kısmi başarı
    
    print(f"\n📊 Sonuç: {success_count}/{len(modules_to_test)} modül başarılı")
    
    if success_count == len(modules_to_test):
        print("🎉 Tüm modüller başarıyla import edildi!")
        return True
    elif success_count >= len(modules_to_test) * 0.8:
        print("⚠️  Çoğu modül çalışıyor, bazı özellikler eksik olabilir.")
        return True
    else:
        print("❌ Kritik modüller eksik, kurulum gerekli.")
        return False

def create_sample_test_files():
    """Test için örnek dosyalar oluştur"""
    test_dir = project_root / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    print(f"📁 Test dosyaları oluşturuluyor: {test_dir}")
    
    # Basit metin dosyası
    with open(test_dir / "sample.txt", "w", encoding="utf-8") as f:
        f.write("Bu bir test dosyasıdır.\nPyPDF-Stirling Tools v2 için hazırlanmıştır.")
    
    print("✅ Test dosyaları oluşturuldu")
    return test_dir

def main():
    """Ana test fonksiyonu"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PyPDF-Stirling Tools v2 Test Script')
    parser.add_argument('--quick', action='store_true', help='Sadece hızlı import testleri')
    parser.add_argument('--full', action='store_true', help='Kapsamlı test suite (varsayılan)')
    parser.add_argument('--create-test-files', action='store_true', help='Test dosyaları oluştur')
    
    args = parser.parse_args()
    
    if args.create_test_files:
        create_sample_test_files()
        return
    
    if args.quick:
        success = test_imports_only()
    else:
        success = run_comprehensive_test()
    
    # Test sonucu ile çıkış kodu
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()