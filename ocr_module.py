#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - OCR Processing Module
Gelişmiş OCR işlemleri ve dil yönetimi
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import threading
import requests
import subprocess
import tempfile
import json

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import pdf2image
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"OCR bağımlılıkları eksik: {e}")
    DEPENDENCIES_AVAILABLE = False

class OCRProcessor:
    """
    Gelişmiş OCR işlemci sınıfı
    Çoklu dil desteği ve otomatik dil algılama
    """
    
    def __init__(self, languages: List[str] = None, cache_enabled: bool = False, log_manager=None):
        self.cache_enabled = cache_enabled
        self.log_manager = log_manager
        self.processing_lock = threading.Lock()
        
        # Varsayılan diller
        self.default_languages = languages or ['eng', 'tur']
        self.available_languages = []
        self.installed_languages = []
        
        # OCR ayarları
        self.default_config = {
            'dpi': 300,
            'preprocessing': True,
            'deskew': True,
            'noise_removal': True,
            'contrast_enhancement': True,
            'psm': 3,  # Page segmentation mode
            'oem': 3   # OCR Engine Mode
        }
        
        if DEPENDENCIES_AVAILABLE:
            self.setup_tesseract()
            self.detect_installed_languages()
        else:
            self.log("OCR bağımlılıkları mevcut değil", "warning")
    
    def setup_tesseract(self):
        """Tesseract OCR'ı ayarla"""
        try:
            # Tesseract yolunu bul
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                '/usr/bin/tesseract',  # Linux
                '/usr/local/bin/tesseract',  # macOS Homebrew
                '/opt/homebrew/bin/tesseract'  # macOS M1 Homebrew
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.log(f"Tesseract bulundu: {path}", "info")
                    break
            else:
                # Sistem PATH'inde ara
                try:
                    subprocess.run(['tesseract', '--version'], 
                                 capture_output=True, check=True)
                    self.log("Tesseract sistem PATH'inde bulundu", "info")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.log("Tesseract bulunamadı", "error")
                    raise Exception("Tesseract OCR bulunamadı")
            
            # Test çalıştır
            self.test_tesseract()
            
        except Exception as e:
            self.log(f"Tesseract kurulum hatası: {e}", "error")
            raise
    
    def test_tesseract(self):
        """Tesseract test et"""
        try:
            # Basit test resmi oluştur
            test_image = Image.new('RGB', (200, 50), color='white')
            
            # PIL ImageDraw kullanarak basit metin ekle
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(test_image)
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((10, 10), "Test", fill='black', font=font)
            
            # OCR test
            result = pytesseract.image_to_string(test_image)
            
            if 'Test' in result or 'test' in result.lower():
                self.log("Tesseract test başarılı", "info")
            else:
                self.log("Tesseract test sonucu beklenmeyen", "warning")
                
        except Exception as e:
            self.log(f"Tesseract test hatası: {e}", "error")
    
    def detect_installed_languages(self):
        """Yüklü dilleri tespit et"""
        try:
            langs = pytesseract.get_languages(config='')
            self.installed_languages = [lang for lang in langs if lang != 'osd']
            self.available_languages = self.installed_languages.copy()
            
            self.log(f"Tespit edilen diller: {self.installed_languages}", "info")
            
        except Exception as e:
            self.log(f"Dil tespit hatası: {e}", "error")
            self.installed_languages = ['eng']
            self.available_languages = ['eng']
    
    def get_available_languages(self) -> List[str]:
        """Mevcut dilleri al"""
        return self.available_languages.copy()
    
    def get_language_info(self) -> Dict[str, Dict]:
        """Dil bilgilerini al"""
        language_names = {
            'afr': 'Afrikaans',
            'amh': 'Amharic',
            'ara': 'Arabic',
            'asm': 'Assamese',
            'aze': 'Azerbaijani',
            'aze_cyrl': 'Azerbaijani - Cyrillic',
            'bel': 'Belarusian',
            'ben': 'Bengali',
            'bod': 'Tibetan',
            'bos': 'Bosnian',
            'bre': 'Breton',
            'bul': 'Bulgarian',
            'cat': 'Catalan',
            'ceb': 'Cebuano',
            'ces': 'Czech',
            'chi_sim': 'Chinese - Simplified',
            'chi_tra': 'Chinese - Traditional',
            'chr': 'Cherokee',
            'cym': 'Welsh',
            'dan': 'Danish',
            'deu': 'German',
            'dzo': 'Dzongkha',
            'ell': 'Greek',
            'eng': 'English',
            'enm': 'English, Middle',
            'epo': 'Esperanto',
            'est': 'Estonian',
            'eus': 'Basque',
            'fas': 'Persian',
            'fin': 'Finnish',
            'fra': 'French',
            'frk': 'German Fraktur',
            'frm': 'French, Middle',
            'gle': 'Irish',
            'glg': 'Galician',
            'grc': 'Greek, Ancient',
            'guj': 'Gujarati',
            'hat': 'Haitian',
            'heb': 'Hebrew',
            'hin': 'Hindi',
            'hrv': 'Croatian',
            'hun': 'Hungarian',
            'iku': 'Inuktitut',
            'ind': 'Indonesian',
            'isl': 'Icelandic',
            'ita': 'Italian',
            'ita_old': 'Italian - Old',
            'jav': 'Javanese',
            'jpn': 'Japanese',
            'kan': 'Kannada',
            'kat': 'Georgian',
            'kat_old': 'Georgian - Old',
            'kaz': 'Kazakh',
            'khm': 'Central Khmer',
            'kir': 'Kirghiz',
            'kor': 'Korean',
            'kur': 'Kurdish',
            'lao': 'Lao',
            'lat': 'Latin',
            'lav': 'Latvian',
            'lit': 'Lithuanian',
            'ltz': 'Luxembourgish',
            'mal': 'Malayalam',
            'mar': 'Marathi',
            'mkd': 'Macedonian',
            'mlt': 'Maltese',
            'mon': 'Mongolian',
            'mri': 'Maori',
            'msa': 'Malay',
            'mya': 'Burmese',
            'nep': 'Nepali',
            'nld': 'Dutch',
            'nor': 'Norwegian',
            'oci': 'Occitan',
            'ori': 'Oriya',
            'pan': 'Panjabi',
            'pol': 'Polish',
            'por': 'Portuguese',
            'pus': 'Pushto',
            'que': 'Quechua',
            'ron': 'Romanian',
            'rus': 'Russian',
            'san': 'Sanskrit',
            'sin': 'Sinhala',
            'slk': 'Slovak',
            'slv': 'Slovenian',
            'snd': 'Sindhi',
            'spa': 'Spanish',
            'spa_old': 'Spanish - Old',
            'sqi': 'Albanian',
            'srp': 'Serbian',
            'srp_latn': 'Serbian - Latin',
            'sun': 'Sundanese',
            'swa': 'Swahili',
            'swe': 'Swedish',
            'syr': 'Syriac',
            'tam': 'Tamil',
            'tat': 'Tatar',
            'tel': 'Telugu',
            'tgk': 'Tajik',
            'tgl': 'Tagalog',
            'tha': 'Thai',
            'tir': 'Tigrinya',
            'ton': 'Tonga',
            'tur': 'Turkish',
            'uig': 'Uighur',
            'ukr': 'Ukrainian',
            'urd': 'Urdu',
            'uzb': 'Uzbek',
            'uzb_cyrl': 'Uzbek - Cyrillic',
            'vie': 'Vietnamese',
            'yid': 'Yiddish',
            'yor': 'Yoruba'
        }
        
        language_info = {}
        for lang_code in self.available_languages:
            language_info[lang_code] = {
                'name': language_names.get(lang_code, lang_code.upper()),
                'installed': lang_code in self.installed_languages,
                'code': lang_code
            }
        
        return language_info
    
    def install_language(self, language_code: str) -> bool:
        """Dil paketi kur"""
        try:
            self.log(f"Dil paketi kuruluyor: {language_code}", "info")
            
            # Platform-specific kurulum
            if os.name == 'nt':  # Windows
                return self._install_language_windows(language_code)
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':  # macOS
                    return self._install_language_macos(language_code)
                else:  # Linux
                    return self._install_language_linux(language_code)
            
            return False
            
        except Exception as e:
            self.log(f"Dil paketi kurulum hatası: {e}", "error")
            return False
    
    def _install_language_windows(self, language_code: str) -> bool:
        """Windows için dil paketi kur"""
        try:
            # GitHub'dan indir
            url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{language_code}.traineddata"
            
            # Tesseract tessdata dizinini bul
            tessdata_dir = Path(pytesseract.pytesseract.tesseract_cmd).parent / 'tessdata'
            
            if not tessdata_dir.exists():
                self.log(f"Tessdata dizini bulunamadı: {tessdata_dir}", "error")
                return False
            
            # Dosyayı indir
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Kaydet
            lang_file = tessdata_dir / f"{language_code}.traineddata"
            lang_file.write_bytes(response.content)
            
            self.detect_installed_languages()
            return True
            
        except Exception as e:
            self.log(f"Manuel dil indirme hatası: {e}", "error")
            return False
    
    def auto_detect_language(self, image: Image.Image) -> str:
        """Otomatik dil algılama"""
        try:
            # OSD (Orientation and Script Detection) kullan
            osd_result = pytesseract.image_to_osd(image)
            
            # Script bilgisini çıkar
            script_line = [line for line in osd_result.split('\n') if 'Script:' in line]
            if script_line:
                script = script_line[0].split('Script:')[1].strip()
                
                # Script'e göre dil öner
                script_to_lang = {
                    'Latin': 'eng',
                    'Arabic': 'ara',
                    'Chinese': 'chi_sim',
                    'Cyrillic': 'rus',
                    'Devanagari': 'hin',
                    'Japanese': 'jpn',
                    'Korean': 'kor'
                }
                
                detected_lang = script_to_lang.get(script, 'eng')
                
                # Türkçe karakterler varsa Türkçe öner
                sample_text = pytesseract.image_to_string(image, config='--psm 3')
                turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
                if any(char in sample_text for char in turkish_chars):
                    detected_lang = 'tur'
                
                self.log(f"Algılanan dil: {detected_lang} (Script: {script})", "info")
                return detected_lang
            
        except Exception as e:
            self.log(f"Dil algılama hatası: {e}", "warning")
        
        # Varsayılan dil
        return 'tur' if 'tur' in self.installed_languages else 'eng'
    
    def preprocess_image(self, image: Image.Image, config: Dict = None) -> Image.Image:
        """Görüntü ön işleme"""
        if not config:
            config = self.default_config
        
        try:
            processed_image = image.copy()
            
            # Gri tonlamaya çevir
            if processed_image.mode != 'L':
                processed_image = processed_image.convert('L')
            
            if config.get('contrast_enhancement', True):
                # Kontrast artırma
                enhancer = ImageEnhance.Contrast(processed_image)
                processed_image = enhancer.enhance(1.5)
            
            if config.get('noise_removal', True):
                # Gürültü azaltma
                processed_image = processed_image.filter(ImageFilter.MedianFilter(size=3))
            
            if config.get('deskew', True):
                # Eğim düzeltme
                processed_image = self._deskew_image(processed_image)
            
            # Çözünürlük artırma
            target_dpi = config.get('dpi', 300)
            current_dpi = processed_image.info.get('dpi', (72, 72))
            
            if isinstance(current_dpi, tuple):
                current_dpi = current_dpi[0]
            
            if current_dpi < target_dpi:
                scale_factor = target_dpi / current_dpi
                new_size = (int(processed_image.width * scale_factor), 
                           int(processed_image.height * scale_factor))
                processed_image = processed_image.resize(new_size, Image.LANCZOS)
            
            return processed_image
            
        except Exception as e:
            self.log(f"Görüntü ön işleme hatası: {e}", "error")
            return image
    
    def _deskew_image(self, image: Image.Image) -> Image.Image:
        """Görüntü eğim düzeltme"""
        try:
            # PIL Image'ı OpenCV formatına çevir
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Kenarları tespit et
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough transform ile çizgileri bul
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Açıları hesapla
                angles = []
                for rho, theta in lines[:10]:  # İlk 10 çizgi
                    angle = theta * 180 / np.pi
                    if angle < 90:
                        angles.append(angle)
                    else:
                        angles.append(angle - 180)
                
                if angles:
                    # Ortalama açıyı hesapla
                    median_angle = np.median(angles)
                    
                    # Küçük açıları düzelt
                    if abs(median_angle) > 0.5:
                        # Döndür
                        rotated = image.rotate(-median_angle, expand=True, fillcolor='white')
                        self.log(f"Eğim düzeltme: {median_angle:.2f}°", "debug")
                        return rotated
            
            return image
            
        except Exception as e:
            self.log(f"Eğim düzeltme hatası: {e}", "warning")
            return image
    
    def process_pdf(self, pdf_path: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF OCR işleme"""
        try:
            with self.processing_lock:
                self.log(f"PDF OCR işlemi başlıyor: {pdf_path}", "info")
                
                pdf_path = Path(pdf_path)
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Ayarları hazırla
                config = self.default_config.copy()
                config.update(kwargs)
                
                language = config.get('language', 'tur')
                auto_detect = config.get('auto_detect', True)
                dpi = config.get('dpi', 300)
                
                # PDF'i sayfalara çevir
                pages = pdf2image.convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    fmt='RGB'
                )
                
                if not pages:
                    return {'success': False, 'error': 'PDF sayfaları çevrilemedi'}
                
                # Çıktı dosyası
                output_filename = f"{pdf_path.stem}_ocr.pdf"
                output_path = output_dir / output_filename
                
                # Sayfa metinleri
                page_texts = []
                processed_pages = []
                
                for i, page_image in enumerate(pages):
                    self.log(f"Sayfa işleniyor: {i+1}/{len(pages)}", "info")
                    
                    # Görüntü ön işleme
                    if config.get('preprocessing', True):
                        processed_image = self.preprocess_image(page_image, config)
                    else:
                        processed_image = page_image
                    
                    # Dil algılama
                    if auto_detect and i == 0:  # İlk sayfa için algıla
                        detected_lang = self.auto_detect_language(processed_image)
                        if detected_lang in self.installed_languages:
                            language = detected_lang
                    
                    # OCR uygula
                    ocr_config = f'--psm {config.get("psm", 3)} --oem {config.get("oem", 3)}'
                    
                    try:
                        text = pytesseract.image_to_string(
                            processed_image,
                            lang=language,
                            config=ocr_config
                        )
                        page_texts.append(text)
                        processed_pages.append(processed_image)
                        
                    except Exception as e:
                        self.log(f"Sayfa {i+1} OCR hatası: {e}", "error")
                        page_texts.append("")
                        processed_pages.append(page_image)
                
                # Aranabilir PDF oluştur
                searchable_pdf = self._create_searchable_pdf(
                    processed_pages, page_texts, str(output_path)
                )
                
                if searchable_pdf:
                    result = {
                        'success': True,
                        'output_path': str(output_path),
                        'language_used': language,
                        'pages_processed': len(pages),
                        'total_text_length': sum(len(text) for text in page_texts),
                        'output_size': output_path.stat().st_size if output_path.exists() else 0
                    }
                    
                    self.log(f"OCR işlemi tamamlandı: {output_path}", "info")
                    return result
                else:
                    return {'success': False, 'error': 'Aranabilir PDF oluşturulamadı'}
                
        except Exception as e:
            self.log(f"PDF OCR işlem hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def _create_searchable_pdf(self, images: List[Image.Image], texts: List[str], output_path: str) -> bool:
        """Aranabilir PDF oluştur"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io
            
            # PDF oluştur
            c = canvas.Canvas(output_path, pagesize=A4)
            
            for i, (image, text) in enumerate(zip(images, texts)):
                if i > 0:
                    c.showPage()  # Yeni sayfa
                
                # Görüntüyü ekle
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                img_reader = ImageReader(img_buffer)
                c.drawImage(img_reader, 0, 0, width=A4[0], height=A4[1])
                
                # Metni görünmez şekilde ekle (arama için)
                if text.strip():
                    c.setFillColorRGB(1, 1, 1, alpha=0)  # Şeffaf beyaz
                    c.setFont("Helvetica", 8)
                    
                    # Metin satırlarını ekle
                    lines = text.split('\n')
                    y_position = A4[1] - 20
                    
                    for line in lines[:50]:  # İlk 50 satır
                        if line.strip():
                            c.drawString(10, y_position, line[:100])  # İlk 100 karakter
                            y_position -= 12
                        
                        if y_position < 20:
                            break
            
            c.save()
            return True
            
        except Exception as e:
            self.log(f"Aranabilir PDF oluşturma hatası: {e}", "error")
            
            # Alternatif yöntem: img2pdf kullan
            try:
                import img2pdf
                
                # Görüntüleri geçici dosyalar olarak kaydet
                temp_images = []
                with tempfile.TemporaryDirectory() as temp_dir:
                    for i, image in enumerate(images):
                        temp_path = Path(temp_dir) / f"page_{i}.png"
                        image.save(temp_path)
                        temp_images.append(str(temp_path))
                    
                    # PDF oluştur
                    with open(output_path, "wb") as f:
                        f.write(img2pdf.convert(temp_images))
                
                return True
                
            except ImportError:
                self.log("img2pdf modülü bulunamadı", "warning")
                return False
            except Exception as e:
                self.log(f"img2pdf ile PDF oluşturma hatası: {e}", "error")
                return False
    
    def extract_text_from_image(self, image_path: str, language: str = None, config: Dict = None) -> Dict[str, Any]:
        """Görüntüden metin çıkarma"""
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                return {'success': False, 'error': 'Görüntü dosyası bulunamadı'}
            
            # Görüntüyü yükle
            image = Image.open(image_path)
            
            # Ayarları hazırla
            config = config or self.default_config
            language = language or 'tur'
            
            # Dil algılama
            if config.get('auto_detect', True):
                detected_lang = self.auto_detect_language(image)
                if detected_lang in self.installed_languages:
                    language = detected_lang
            
            # Görüntü ön işleme
            if config.get('preprocessing', True):
                processed_image = self.preprocess_image(image, config)
            else:
                processed_image = image
            
            # OCR uygula
            ocr_config = f'--psm {config.get("psm", 3)} --oem {config.get("oem", 3)}'
            
            text = pytesseract.image_to_string(
                processed_image,
                lang=language,
                config=ocr_config
            )
            
            # Güven skorunu al
            data = pytesseract.image_to_data(
                processed_image,
                lang=language,
                config=ocr_config,
                output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': text,
                'language_used': language,
                'confidence': avg_confidence,
                'word_count': len(text.split()),
                'character_count': len(text)
            }
            
        except Exception as e:
            self.log(f"Görüntü OCR hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def get_text_boxes(self, image_path: str, language: str = None) -> List[Dict]:
        """Metin kutularını al (koordinatlarla)"""
        try:
            image = Image.open(image_path)
            language = language or 'tur'
            
            # Detaylı OCR verisi al
            data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            text_boxes = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Güven skoru > 30
                    text_boxes.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': int(data['left'][i]),
                        'top': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i])
                    })
            
            return text_boxes
            
        except Exception as e:
            self.log(f"Metin kutuları alma hatası: {e}", "error")
            return []
    
    def batch_process_images(self, image_paths: List[str], output_dir: str, **kwargs) -> Dict[str, Any]:
        """Toplu görüntü OCR işleme"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = []
            
            for i, image_path in enumerate(image_paths):
                self.log(f"Görüntü işleniyor: {i+1}/{len(image_paths)}", "info")
                
                result = self.extract_text_from_image(image_path, **kwargs)
                result['image_path'] = image_path
                results.append(result)
                
                # Metin dosyasını kaydet
                if result['success']:
                    text_file = output_dir / f"{Path(image_path).stem}.txt"
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(result['text'])
                    result['text_file'] = str(text_file)
            
            # Özet rapor
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            return {
                'success': True,
                'total_processed': len(image_paths),
                'successful': len(successful),
                'failed': len(failed),
                'results': results,
                'output_directory': str(output_dir)
            }
            
        except Exception as e:
            self.log(f"Toplu OCR işlem hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def log(self, message: str, level: str = "info"):
        """Log mesajı"""
        if self.log_manager:
            getattr(self.log_manager, level, self.log_manager.info)(f"OCR: {message}")
        else:
            print(f"OCR {level.upper()}: {message}")
    
    def cleanup(self):
        """Temizlik işlemleri"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """OCR istatistikleri"""
        return {
            'installed_languages': len(self.installed_languages),
            'available_languages': len(self.available_languages),
            'tesseract_available': DEPENDENCIES_AVAILABLE,
            'default_language': self.default_languages[0] if self.default_languages else 'eng'
        }

# OCR dil kodları ve isimleri eşlemesi
OCR_LANGUAGE_NAMES = {
    'tur': 'Türkçe',
    'eng': 'English',
    'deu': 'Deutsch',
    'fra': 'Français',
    'spa': 'Español',
    'ita': 'Italiano',
    'por': 'Português',
    'rus': 'Русский',
    'chi_sim': '中文 (简体)',
    'chi_tra': '中文 (繁體)',
    'jpn': '日本語',
    'kor': '한국어',
    'ara': 'العربية',
    'hin': 'हिन्दी'
}

def get_language_display_name(lang_code: str) -> str:
    """Dil kodundan görünen isim al"""
    return OCR_LANGUAGE_NAMES.get(lang_code, lang_code.upper())
_dir / f"{language_code}.traineddata"
            lang_file.write_bytes(response.content)
            
            # Yüklü dilleri yeniden tespit et
            self.detect_installed_languages()
            
            self.log(f"Dil paketi başarıyla kuruldu: {language_code}", "info")
            return True
            
        except Exception as e:
            self.log(f"Windows dil paketi kurulum hatası: {e}", "error")
            return False
    
    def _install_language_linux(self, language_code: str) -> bool:
        """Linux için dil paketi kur"""
        try:
            # Paket yöneticisi ile kur
            commands = [
                f"sudo apt-get install -y tesseract-ocr-{language_code}",
                f"sudo yum install -y tesseract-langpack-{language_code}",
                f"sudo pacman -S tesseract-data-{language_code}"
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd.split(), capture_output=True, text=True)
                    if result.returncode == 0:
                        self.detect_installed_languages()
                        return True
                except:
                    continue
            
            # Manuel indirme
            return self._download_language_data(language_code)
            
        except Exception as e:
            self.log(f"Linux dil paketi kurulum hatası: {e}", "error")
            return False
    
    def _install_language_macos(self, language_code: str) -> bool:
        """macOS için dil paketi kur"""
        try:
            # Homebrew ile kur
            cmd = f"brew install tesseract-lang"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.detect_installed_languages()
                return True
            
            # Manuel indirme
            return self._download_language_data(language_code)
            
        except Exception as e:
            self.log(f"macOS dil paketi kurulum hatası: {e}", "error")
            return False
    
    def _download_language_data(self, language_code: str) -> bool:
        """Dil verisini manuel indir"""
        try:
            url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{language_code}.traineddata"
            
            # Sistem tessdata dizinini bul
            possible_dirs = [
                '/usr/share/tesseract-ocr/4.00/tessdata',
                '/usr/share/tesseract-ocr/tessdata',
                '/usr/local/share/tessdata',
                '/opt/homebrew/share/tessdata'
            ]
            
            tessdata_dir = None
            for dir_path in possible_dirs:
                if Path(dir_path).exists():
                    tessdata_dir = Path(dir_path)
                    break
            
            if not tessdata_dir:
                self.log("Tessdata dizini bulunamadı", "error")
                return False
            
            # İndir
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Kaydet
            lang_file = tessdata