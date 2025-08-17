# resources/pdf_utils.py
"""
PyPDF-Stirling Tools v2 - PDF Processing Utilities
Comprehensive PDF processing with modern features
"""

import os
import io
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import concurrent.futures
import tempfile
import shutil
import time

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PIL import Image, ImageDraw, ImageFont
    import fitz  # PyMuPDF
    PDF_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"PDF işleme bağımlılıkları eksik: {e}")
    PDF_DEPENDENCIES_AVAILABLE = False

class PDFProcessor:
    """
    Gelişmiş PDF işleme sınıfı
    Paralel işleme, cache ve loglama desteği
    """
    
    def __init__(self, cache_manager=None, log_manager=None, max_workers: int = 4):
        self.cache_manager = cache_manager
        self.log_manager = log_manager
        self.max_workers = max_workers
        self.processing_lock = threading.Lock()
        
        # Geçici dosya yönetimi
        self.temp_dir = Path(tempfile.gettempdir()) / "pypdf_tools_v2"
        self.temp_dir.mkdir(exist_ok=True)
        
        # İstatistikler
        self.stats = {
            'processed_files': 0,
            'total_processing_time': 0,
            'cache_hits': 0,
            'errors': 0
        }
        
        if not PDF_DEPENDENCIES_AVAILABLE:
            self.log("PDF işleme bağımlılıkları mevcut değil", "error")
    
    def merge_pdfs(self, input_files: List[str], output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF dosyalarını birleştir"""
        try:
            start_time = time.time()
            self.log(f"PDF birleştirme başlıyor: {len(input_files)} dosya", "info")
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Ayarları al
            order = kwargs.get('order', 'filename')
            add_bookmarks = kwargs.get('add_bookmarks', True)
            
            # Dosyaları sırala
            sorted_files = self._sort_files(input_files, order)
            
            # PDF birleştir
            merger = PdfWriter()
            
            for i, file_path in enumerate(sorted_files):
                try:
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PdfReader(pdf_file)
                        
                        # Sayfaları ekle
                        start_page = len(merger.pages)
                        for page in pdf_reader.pages:
                            merger.add_page(page)
                        
                        # Bookmark ekle
                        if add_bookmarks:
                            filename = Path(file_path).stem
                            merger.add_outline_item(filename, start_page)
                        
                except Exception as e:
                    self.log(f"Dosya birleştirme hatası {file_path}: {e}", "error")
                    continue
            
            # Çıktı dosyası
            output_filename = "merged_document.pdf"
            output_path = output_dir / output_filename
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            end_time = time.time()
            self.stats['processed_files'] += len(input_files)
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'pages_merged': len(merger.pages),
                'files_processed': len(sorted_files),
                'output_size': output_path.stat().st_size,
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF birleştirme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def split_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'i böl"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            split_type = kwargs.get('split_type', 'pages')
            pages_per_file = kwargs.get('pages_per_file', 1)
            
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                
                if split_type == 'pages':
                    # Her sayfa ayrı dosya
                    output_files = []
                    for i, page in enumerate(pdf_reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)
                        
                        output_filename = f"{input_path.stem}_page_{i+1}.pdf"
                        output_path = output_dir / output_filename
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        output_files.append(str(output_path))
                
                elif split_type == 'count':
                    # Belirli sayfa sayısı
                    output_files = []
                    pages = list(pdf_reader.pages)
                    
                    for i in range(0, len(pages), pages_per_file):
                        writer = PdfWriter()
                        end_idx = min(i + pages_per_file, len(pages))
                        
                        for j in range(i, end_idx):
                            writer.add_page(pages[j])
                        
                        part_num = (i // pages_per_file) + 1
                        output_filename = f"{input_path.stem}_part_{part_num}.pdf"
                        output_path = output_dir / output_filename
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        output_files.append(str(output_path))
                
                else:
                    return {'success': False, 'error': f'Desteklenmeyen bölme türü: {split_type}'}
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_files': output_files,
                'total_pages': total_pages,
                'files_created': len(output_files),
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF bölme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def compress_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF sıkıştır"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            quality = kwargs.get('quality', 'medium')
            optimize_images = kwargs.get('optimize_images', True)
            remove_metadata = kwargs.get('remove_metadata', False)
            
            # PyMuPDF ile sıkıştırma
            doc = fitz.open(input_file)
            
            # Sıkıştırma seviyeleri
            quality_settings = {
                'low': {'deflate': 9, 'jpeg': 30},
                'medium': {'deflate': 6, 'jpeg': 50},
                'high': {'deflate': 3, 'jpeg': 70}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            if optimize_images:
                # Resimleri sıkıştır
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # RGB veya GRAY
                            # JPEG olarak sıkıştır
                            img_data = pix.pil_tobytes(format="JPEG", optimize=True, quality=settings['jpeg'])
                            doc.update_object(xref, img_data)
                        
                        pix = None
            
            if remove_metadata:
                # Metadata'yı temizle
                doc.set_metadata({})
            
            # Çıktı dosyası
            output_filename = f"{input_path.stem}_compressed.pdf"
            output_path = output_dir / output_filename
            
            # Kaydet
            doc.save(str(output_path), deflate=True, garbage=4)
            doc.close()
            
            # Boyut karşılaştırması
            original_size = input_path.stat().st_size
            compressed_size = output_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF sıkıştırma hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def convert_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'i diğer formatlara dönüştür"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_format = kwargs.get('output_format', 'docx')
            dpi = kwargs.get('dpi', 300)
            
            if output_format in ['jpg', 'png', 'tiff']:
                return self._convert_pdf_to_images(input_file, output_dir, output_format, dpi)
            elif output_format in ['docx', 'txt']:
                return self._convert_pdf_to_text(input_file, output_dir, output_format)
            else:
                return {'success': False, 'error': f'Desteklenmeyen format: {output_format}'}
                
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF dönüştürme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def _convert_pdf_to_images(self, input_file: str, output_dir: Path, format: str, dpi: int) -> Dict[str, Any]:
        """PDF'i görüntülere dönüştür"""
        try:
            import pdf2image
            
            input_path = Path(input_file)
            
            # PDF'i görüntülere çevir
            pages = pdf2image.convert_from_path(
                input_file,
                dpi=dpi,
                fmt=format.upper()
            )
            
            output_files = []
            for i, page in enumerate(pages):
                output_filename = f"{input_path.stem}_page_{i+1}.{format}"
                output_path = output_dir / output_filename
                
                page.save(output_path, format.upper())
                output_files.append(str(output_path))
            
            return {
                'success': True,
                'output_files': output_files,
                'pages_converted': len(pages),
                'format': format,
                'dpi': dpi
            }
            
        except ImportError:
            return {'success': False, 'error': 'pdf2image modülü bulunamadı'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _convert_pdf_to_text(self, input_file: str, output_dir: Path, format: str) -> Dict[str, Any]:
        """PDF'i metin formatlarına dönüştür"""
        try:
            input_path = Path(input_file)
            
            # PDF'den metin çıkar
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                text_content = []
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    text_content.append(text)
            
            full_text = '\n\n'.join(text_content)
            
            if format == 'txt':
                output_filename = f"{input_path.stem}.txt"
                output_path = output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                
                return {
                    'success': True,
                    'output_path': str(output_path),
                    'text_length': len(full_text),
                    'pages_processed': len(text_content)
                }
                
            elif format == 'docx':
                try:
                    from docx import Document
                    
                    output_filename = f"{input_path.stem}.docx"
                    output_path = output_dir / output_filename
                    
                    doc = Document()
                    
                    for i, page_text in enumerate(text_content):
                        if i > 0:
                            doc.add_page_break()
                        
                        # Paragrafları ekle
                        paragraphs = page_text.split('\n\n')
                        for paragraph in paragraphs:
                            if paragraph.strip():
                                doc.add_paragraph(paragraph.strip())
                    
                    doc.save(str(output_path))
                    
                    return {
                        'success': True,
                        'output_path': str(output_path),
                        'pages_processed': len(text_content),
                        'paragraphs_created': sum(len(text.split('\n\n')) for text in text_content)
                    }
                    
                except ImportError:
                    return {'success': False, 'error': 'python-docx modülü bulunamadı'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rotate_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF sayfalarını döndür"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            angle = kwargs.get('angle', 90)
            pages = kwargs.get('pages', 'all')
            specific_pages = kwargs.get('specific_pages', '')
            
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                pdf_writer = PdfWriter()
                
                total_pages = len(pdf_reader.pages)
                rotated_pages = 0
                
                # Hangi sayfaları döndüreceğini belirle
                if pages == 'all':
                    pages_to_rotate = list(range(total_pages))
                elif pages == 'specific' and specific_pages:
                    pages_to_rotate = self._parse_page_ranges(specific_pages, total_pages)
                else:
                    pages_to_rotate = list(range(total_pages))
                
                for i, page in enumerate(pdf_reader.pages):
                    if i in pages_to_rotate:
                        rotated_page = page.rotate(angle)
                        pdf_writer.add_page(rotated_page)
                        rotated_pages += 1
                    else:
                        pdf_writer.add_page(page)
                
                # Çıktı dosyası
                output_filename = f"{input_path.stem}_rotated_{angle}deg.pdf"
                output_path = output_dir / output_filename
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'total_pages': total_pages,
                'rotated_pages': rotated_pages,
                'rotation_angle': angle,
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF döndürme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def add_watermark(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'e filigran ekle"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            watermark_type = kwargs.get('watermark_type', 'text')
            position = kwargs.get('position', 'center')
            
            if watermark_type == 'text':
                return self._add_text_watermark(input_file, output_dir, **kwargs)
            elif watermark_type == 'image':
                return self._add_image_watermark(input_file, output_dir, **kwargs)
            else:
                return {'success': False, 'error': f'Desteklenmeyen filigran türü: {watermark_type}'}
                
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"Filigran ekleme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def _add_text_watermark(self, input_file: str, output_dir: Path, **kwargs) -> Dict[str, Any]:
        """Metin filigranı ekle"""
        try:
            input_path = Path(input_file)
            
            text = kwargs.get('text', 'WATERMARK')
            font_size = kwargs.get('font_size', 50)
            opacity = kwargs.get('opacity', 0.3)
            position = kwargs.get('position', 'center')
            
            # Filigran PDF'i oluştur
            temp_watermark = self.temp_dir / "temp_watermark.pdf"
            
            c = canvas.Canvas(str(temp_watermark), pagesize=A4)
            
            # Pozisyon hesapla
            page_width, page_height = A4
            positions = {
                'center': (page_width/2, page_height/2),
                'top-left': (100, page_height-100),
                'top-right': (page_width-100, page_height-100),
                'bottom-left': (100, 100),
                'bottom-right': (page_width-100, 100)
            }
            
            x, y = positions.get(position, positions['center'])
            
            # Metin ekle
            c.setFont("Helvetica", font_size)
            c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
            c.drawCentredText(x, y, text)
            
            c.save()
            
            # Ana PDF ile birleştir
            with open(input_file, 'rb') as main_file, open(temp_watermark, 'rb') as watermark_file:
                main_pdf = PdfReader(main_file)
                watermark_pdf = PdfReader(watermark_file)
                watermark_page = watermark_pdf.pages[0]
                
                pdf_writer = PdfWriter()
                
                for page in main_pdf.pages:
                    page.merge_page(watermark_page)
                    pdf_writer.add_page(page)
                
                output_filename = f"{input_path.stem}_watermarked.pdf"
                output_path = output_dir / output_filename
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            # Geçici dosyayı temizle
            temp_watermark.unlink(missing_ok=True)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'watermark_text': text,
                'pages_processed': len(main_pdf.pages)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _add_image_watermark(self, input_file: str, output_dir: Path, **kwargs) -> Dict[str, Any]:
        """Resim filigranı ekle"""
        try:
            input_path = Path(input_file)
            image_path = kwargs.get('image_path', '')
            size = kwargs.get('size', 20)  # Yüzde
            position = kwargs.get('position', 'center')
            
            if not image_path or not Path(image_path).exists():
                return {'success': False, 'error': 'Filigran resmi bulunamadı'}
            
            # PyMuPDF ile resim filigranı
            doc = fitz.open(input_file)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Sayfa boyutları
                rect = page.rect
                
                # Pozisyon hesapla
                positions = {
                    'center': fitz.Point(rect.width/2, rect.height/2),
                    'top-left': fitz.Point(50, rect.height-50),
                    'top-right': fitz.Point(rect.width-50, rect.height-50),
                    'bottom-left': fitz.Point(50, 50),
                    'bottom-right': fitz.Point(rect.width-50, 50)
                }
                
                point = positions.get(position, positions['center'])
                
                # Resmi ekle
                page.insert_image(
                    fitz.Rect(point.x-50, point.y-50, point.x+50, point.y+50),
                    filename=image_path
                )
            
            output_filename = f"{input_path.stem}_watermarked.pdf"
            output_path = output_dir / output_filename
            
            doc.save(str(output_path))
            doc.close()
            
            return {
                'success': True,
                'output_path': str(output_path),
                'watermark_image': image_path,
                'pages_processed': len(doc)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def encrypt_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'i şifrele"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            user_password = kwargs.get('user_password', '')
            owner_password = kwargs.get('owner_password', '')
            permissions = kwargs.get('permissions', {})
            
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                pdf_writer = PdfWriter()
                
                # Sayfaları kopyala
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Şifreleme uygula
                pdf_writer.encrypt(
                    user_pwd=user_password,
                    owner_pwd=owner_password or user_password,
                    use_128bit=True,
                    permissions_flag=-1 if not permissions else self._get_permission_flags(permissions)
                )
                
                output_filename = f"{input_path.stem}_encrypted.pdf"
                output_path = output_dir / output_filename
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'encrypted': True,
                'has_user_password': bool(user_password),
                'has_owner_password': bool(owner_password),
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF şifreleme hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def extract_text(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'den metin çıkar"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                
                extracted_text = []
                for i, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    extracted_text.append(f"=== Sayfa {i+1} ===\n{text}\n")
                
                full_text = '\n'.join(extracted_text)
                
                # Metin dosyasını kaydet
                output_filename = f"{input_path.stem}_extracted_text.txt"
                output_path = output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'pages_processed': len(pdf_reader.pages),
                'text_length': len(full_text),
                'word_count': len(full_text.split()),
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"Metin çıkarma hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def extract_images(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'den resimleri çıkar"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            doc = fitz.open(input_file)
            extracted_images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # RGB veya GRAY
                            output_filename = f"{input_path.stem}_page{page_num+1}_img{img_index+1}.png"
                            output_path = output_dir / output_filename
                            
                            pix.save(str(output_path))
                            extracted_images.append(str(output_path))
                        
                        pix = None
                        
                    except Exception as e:
                        self.log(f"Resim çıkarma hatası (sayfa {page_num+1}, resim {img_index+1}): {e}", "warning")
                        continue
            
            doc.close()
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'extracted_images': extracted_images,
                'images_count': len(extracted_images),
                'pages_processed': len(doc),
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"Resim çıkarma hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    def optimize_pdf(self, input_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """PDF'i optimize et"""
        try:
            start_time = time.time()
            input_path = Path(input_file)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            doc = fitz.open(input_file)
            
            # Optimize işlemleri
            doc.scrub()  # Gereksiz objeleri temizle
            
            output_filename = f"{input_path.stem}_optimized.pdf"
            output_path = output_dir / output_filename
            
            # Kaydet
            doc.save(str(output_path), 
                    garbage=4,  # Garbage collection
                    deflate=True,  # Compression
                    clean=True)  # Clean up
            doc.close()
            
            # Boyut karşılaştırması
            original_size = input_path.stat().st_size
            optimized_size = output_path.stat().st_size
            size_reduction = (1 - optimized_size / original_size) * 100
            
            end_time = time.time()
            self.stats['processed_files'] += 1
            self.stats['total_processing_time'] += (end_time - start_time)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'original_size': original_size,
                'optimized_size': optimized_size,
                'size_reduction': size_reduction,
                'processing_time': end_time - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"PDF optimizasyon hatası: {e}", "error")
            return {'success': False, 'error': str(e)}
    
    # Utility Methods
    def _sort_files(self, files: List[str], order: str) -> List[str]:
        """Dosyaları sırala"""
        if order == 'filename':
            return sorted(files, key=lambda x: Path(x).name)
        elif order == 'date':
            return sorted(files, key=lambda x: Path(x).stat().st_mtime)
        elif order == 'manual':
            return files  # Kullanıcı sırası
        else:
            return files
    
    def _parse_page_ranges(self, ranges: str, total_pages: int) -> List[int]:
        """Sayfa aralıklarını parse et"""
        pages = []
        
        for range_str in ranges.split(','):
            range_str = range_str.strip()
            
            if '-' in range_str:
                start, end = map(int, range_str.split('-'))
                pages.extend(range(start-1, min(end, total_pages)))
            else:
                page = int(range_str)
                if 1 <= page <= total_pages:
                    pages.append(page-1)
        
        return list(set(pages))  # Duplicates'ları kaldır
    
    def _get_permission_flags(self, permissions: Dict[str, bool]) -> int:
        """İzin bayraklarını hesapla"""
        flags = 0
        
        if permissions.get('printing', True):
            flags |= 4
        if permissions.get('copying', True):
            flags |= 16
        if permissions.get('modification', False):
            flags |= 8
        
        return flags
    
    def log(self, message: str, level: str = "info"):
        """Log mesajı"""
        if self.log_manager:
            getattr(self.log_manager, level, self.log_manager.info)(f"PDF: {message}")
        else:
            print(f"PDF {level.upper()}: {message}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """İstatistikleri al"""
        return self.stats.copy()
    
    def cleanup(self):
        """Temizlik işlemleri"""
        try:
            # Geçici dosyaları temizle
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            self.log(f"Temizlik hatası: {e}", "warning")

# Global fonksiyonlar
def validate_pdf(file_path: str) -> bool:
    """PDF dosyasını doğrula"""
    try:
        with open(file_path, 'rb') as f:
            PdfReader(f)
        return True
    except:
        return False

def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """PDF bilgilerini al"""
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            
            info = {
                'pages': len(reader.pages),
                'encrypted': reader.is_encrypted,
                'title': reader.metadata.title if reader.metadata else None,
                'author': reader.metadata.author if reader.metadata else None,
                'subject': reader.metadata.subject if reader.metadata else None,
                'creator': reader.metadata.creator if reader.metadata else None,
                'producer': reader.metadata.producer if reader.metadata else None,
                'creation_date': reader.metadata.creation_date if reader.metadata else None,
                'modification_date': reader.metadata.modification_date if reader.metadata else None
            }
            
            return info
    except Exception as e:
        return {'error': str(e)}

__all__ = ['PDFProcessor', 'validate_pdf', 'get_pdf_info']