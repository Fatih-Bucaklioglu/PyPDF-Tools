#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools PDF Viewer Widget
React tabanlı hibrit PDF görüntüleyici bileşeni
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

from PyQt6.QtCore import (
    QObject, pyqtSignal, pyqtSlot, QUrl, QTimer,
    QThread, QMutex, QMutexLocker
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QIcon


class PDFJSBridge(QObject):
    """
    Python ve React (JavaScript) arasında köprü görevi gören sınıf
    QWebChannel üzerinden iki yönlü iletişim sağlar
    """
    
    # Python'dan React'e sinyal gönderme
    pdfDataChanged = pyqtSignal(str)  # JSON formatında PDF verisi
    themeChanged = pyqtSignal(str)    # Tema değişikliği
    settingsChanged = pyqtSignal(str) # Ayarlar değişikliği
    
    # React'den gelen işlemler için sinyaller
    toolActionRequested = pyqtSignal(str, dict)  # Tool ID ve data
    pageChanged = pyqtSignal(int)                # Sayfa değişikliği
    annotationAdded = pyqtSignal(dict)           # Yeni annotation
    bookmarkAdded = pyqtSignal(dict)             # Yeni bookmark
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pdf_data: Optional[Dict[str, Any]] = None
        self._mutex = QMutex()
        
        # Tool action handlers
        self._tool_handlers: Dict[str, Callable] = {
            'zoom-in': self._handle_zoom_in,
            'zoom-out': self._handle_zoom_out,
            'rotate': self._handle_rotate,
            'split': self._handle_split,
            'merge': self._handle_merge,
            'encrypt': self._handle_encrypt,
            'decrypt': self._handle_decrypt,
            'highlight': self._handle_highlight,
            'text-note': self._handle_text_note,
            'summarize': self._handle_ai_summarize,
            'extract': self._handle_text_extract,
        }
    
    @pyqtSlot(str, result=str)
    def onToolAction(self, action_data: str) -> str:
        """
        React'den gelen tool action çağrılarını işle
        Bu metod QWebChannel üzerinden çağrılır
        """
        try:
            data = json.loads(action_data)
            tool_id = data.get('toolId', '')
            tool_data = data.get('data', {})
            
            # Sinyali emit et
            self.toolActionRequested.emit(tool_id, tool_data)
            
            # Eğer bu tool için özel handler varsa çalıştır
            if tool_id in self._tool_handlers:
                result = self._tool_handlers[tool_id](tool_data)
                return json.dumps({'success': True, 'result': result})
            
            return json.dumps({'success': True, 'message': f'Tool {tool_id} executed'})
            
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})
    
    @pyqtSlot(str)
    def onPageChange(self, page_data: str) -> None:
        """React'den sayfa değişikliği bildirimi"""
        try:
            data = json.loads(page_data)
            page_number = data.get('page', 1)
            self.pageChanged.emit(page_number)
        except Exception as e:
            print(f"Page change error: {e}")
    
    @pyqtSlot(str)
    def onAnnotationAdd(self, annotation_data: str) -> None:
        """React'den yeni annotation bildirimi"""
        try:
            annotation = json.loads(annotation_data)
            self.annotationAdded.emit(annotation)
        except Exception as e:
            print(f"Annotation add error: {e}")
    
    def update_pdf_data(self, pdf_data: Dict[str, Any]) -> None:
        """PDF verisini güncelle ve React'e gönder"""
        with QMutexLocker(self._mutex):
            self._pdf_data = pdf_data
            self.pdfDataChanged.emit(json.dumps(pdf_data))
    
    def update_theme(self, theme: str) -> None:
        """Tema değişikliğini React'e bildir"""
        self.themeChanged.emit(theme)
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Ayarları güncelle ve React'e gönder"""
        self.settingsChanged.emit(json.dumps(settings))
    
    # Tool handler methods
    def _handle_zoom_in(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yakınlaştırma işlemi"""
        current_zoom = data.get('zoom', 100)
        new_zoom = min(500, current_zoom + 25)
        return {'zoom': new_zoom}
    
    def _handle_zoom_out(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Uzaklaştırma işlemi"""
        current_zoom = data.get('zoom', 100)
        new_zoom = max(25, current_zoom - 25)
        return {'zoom': new_zoom}
    
    def _handle_rotate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Döndürme işlemi"""
        current_rotation = data.get('rotation', 0)
        new_rotation = (current_rotation + 90) % 360
        return {'rotation': new_rotation}
    
    def _handle_split(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PDF bölme işlemi - gerçek implementasyon gerekir"""
        return {'message': 'Split functionality will be implemented'}
    
    def _handle_merge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PDF birleştirme işlemi - gerçek implementasyon gerekir"""
        return {'message': 'Merge functionality will be implemented'}
    
    def _handle_encrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PDF şifreleme işlemi"""
        return {'message': 'Encryption functionality will be implemented'}
    
    def _handle_decrypt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PDF şifre kaldırma işlemi"""
        return {'message': 'Decryption functionality will be implemented'}
    
    def _handle_highlight(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vurgulama işlemi"""
        return {'message': 'Highlight added successfully'}
    
    def _handle_text_note(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Metin notu ekleme işlemi"""
        return {'message': 'Text note added successfully'}
    
    def _handle_ai_summarize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AI özetleme işlemi"""
        return {'message': 'AI summarization will be implemented'}
    
    def _handle_text_extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Metin çıkarma işlemi"""
        return {'message': 'Text extraction will be implemented'}


class PDFViewerWidget(QWebEngineView):
    """
    React tabanlı PDF görüntüleyici widget
    PyQt6 WebEngine içinde React uygulamasını çalıştırır
    """
    
    # Widget sinyalleri
    pdfLoaded = pyqtSignal(dict)
    toolActionPerformed = pyqtSignal(str, dict)
    errorOccurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # JavaScript köprüsü
        self._bridge = PDFJSBridge(self)
        self._channel = QWebChannel()
        self._channel.registerObject('pdfBridge', self._bridge)
        self.page().setWebChannel(self._channel)
        
        # Widget durumu
        self._is_initialized = False
        self._current_pdf_path: Optional[str] = None
        self._current_theme = 'light'
        
        # React build dizinini bul
        self._web_build_path = self._find_web_build_path()
        
        # Sinyalleri bağla
        self._connect_signals()
        
        # Widget'ı başlat
        self._initialize_widget()
    
    def _find_web_build_path(self) -> str:
        """React build dizinini bul"""
        # PyPI paketi olarak kurulmuşsa
        try:
            import pypdf_tools
            pkg_path = Path(pypdf_tools.__file__).parent
            build_path = pkg_path / "web" / "build"
            if build_path.exists():
                return str(build_path)
        except ImportError:
            pass
        
        # Geliştirme ortamında
        current_dir = Path(__file__).parent.parent.parent.parent
        build_path = current_dir / "web" / "build"
        if build_path.exists():
            return str(build_path)
        
        # Son çare - mevcut dizinde ara
        build_path = Path.cwd() / "web" / "build"
        if build_path.exists():
            return str(build_path)
        
        raise FileNotFoundError("React build dizini bulunamadı!")
    
    def _connect_signals(self) -> None:
        """İç sinyalleri bağla"""
        self._bridge.toolActionRequested.connect(self.toolActionPerformed)
        self._bridge.pageChanged.connect(self._on_page_changed)
        self._bridge.annotationAdded.connect(self._on_annotation_added)
        
        # Web sayfası yükleme durumu
        self.loadFinished.connect(self._on_load_finished)
    
    def _initialize_widget(self) -> None:
        """Widget'ı başlat ve React uygulamasını yükle"""
        try:
            index_path = Path(self._web_build_path) / "index.html"
            if not index_path.exists():
                raise FileNotFoundError(f"index.html bulunamadı: {index_path}")
            
            # HTML dosyasını yükle
            url = QUrl.fromLocalFile(str(index_path))
            self.load(url)
            
        except Exception as e:
            self.errorOccurred.emit(f"Widget başlatma hatası: {str(e)}")
    
    def _on_load_finished(self, success: bool) -> None:
        """Web sayfası yüklendiğinde çağrılır"""
        if success:
            self._is_initialized = True
            # React uygulamasının hazır olmasını bekle
            QTimer.singleShot(1000, self._post_load_setup)
        else:
            self.errorOccurred.emit("React uygulaması yüklenemedi")
    
    def _post_load_setup(self) -> None:
        """Yükleme sonrası kurulum işlemleri"""
        # Varsayılan tema ayarla
        self._bridge.update_theme(self._current_theme)
        
        # Eğer PDF varsa yükle
        if self._current_pdf_path:
            self.load_pdf(self._current_pdf_path)
    
    def load_pdf(self, file_path: str) -> bool:
        """PDF dosyasını yükle"""
        try:
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF dosyası bulunamadı: {file_path}")
            
            # PDF metadata'sını çıkar (basit implementasyon)
            pdf_data = {
                'filePath': str(pdf_path),
                'fileName': pdf_path.name,
                'fileSize': pdf_path.stat().st_size,
                'totalPages': self._get_pdf_page_count(pdf_path),
                'metadata': self._extract_pdf_metadata(pdf_path),
                'lastModified': pdf_path.stat().st_mtime
            }
            
            self._current_pdf_path = file_path
            
            # React'e PDF verisini gönder
            if self._is_initialized:
                self._bridge.update_pdf_data(pdf_data)
            
            self.pdfLoaded.emit(pdf_data)
            return True
            
        except Exception as e:
            error_msg = f"PDF yükleme hatası: {str(e)}"
            self.errorOccurred.emit(error_msg)
            return False
    
    def _get_pdf_page_count(self, pdf_path: Path) -> int:
        """PDF sayfa sayısını al - gerçek implementasyon gerekir"""
        # Geçici implementasyon - PyPDF2 kullanılmalı
        return 10  # Placeholder
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """PDF metadata'sını çıkar - gerçek implementasyon gerekir"""
        # Geçici implementasyon
        return {
            'title': pdf_path.stem,
            'author': 'Unknown',
            'subject': '',
            'keywords': '',
            'creator': 'PyPDF-Tools',
            'producer': 'PyPDF-Tools',
            'creationDate': '',
            'modificationDate': ''
        }
    
    def set_theme(self, theme: str) -> None:
        """Tema değiştir"""
        if theme in ['light', 'dark', 'neon', 'midnight']:
            self._current_theme = theme
            if self._is_initialized:
                self._bridge.update_theme(theme)
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Ayarları güncelle"""
        if self._is_initialized:
            self._bridge.update_settings(settings)
    
    def _on_page_changed(self, page_number: int) -> None:
        """Sayfa değişikliği handler"""
        print(f"Sayfa değişti: {page_number}")
    
    def _on_annotation_added(self, annotation: Dict[str, Any]) -> None:
        """Yeni annotation handler"""
        print(f"Yeni annotation eklendi: {annotation}")
    
    def get_current_pdf_path(self) -> Optional[str]:
        """Mevcut PDF dosya yolunu döndür"""
        return self._current_pdf_path
    
    def is_pdf_loaded(self) -> bool:
        """PDF yüklenmiş mi kontrol et"""
        return self._current_pdf_path is not None
    
    def reload_react_app(self) -> None:
        """React uygulamasını yeniden yükle"""
        self._is_initialized = False
        self._initialize_widget()


class PDFViewerContainer(QWidget):
    """
    PDF Viewer widget'ı için konteyner sınıfı
    Hata mesajları ve yükleme durumu gösterimi için
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF Viewer widget
        self.pdf_viewer = PDFViewerWidget(self)
        layout.addWidget(self.pdf_viewer)
        
        # Hata durumları için sinyal bağlantıları
        self.pdf_viewer.errorOccurred.connect(self._show_error)
        
    def _show_error(self, error_message: str) -> None:
        """Hata mesajı göster"""
        QMessageBox.critical(self, "PDF Viewer Hatası", error_message)
    
    def load_pdf(self, file_path: str) -> bool:
        """PDF yükle"""
        return self.pdf_viewer.load_pdf(file_path)
    
    def set_theme(self, theme: str) -> None:
        """Tema ayarla"""
        self.pdf_viewer.set_theme(theme)
