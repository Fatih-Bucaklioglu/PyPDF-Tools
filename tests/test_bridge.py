#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools QWebChannel Bridge Test Modülü
Python ve JavaScript arasındaki QWebChannel iletişimini test eder
"""

import json
import pytest
from unittest.mock import Mock, MagicMock, patch, signal

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebChannel import QWebChannel

from pypdf_tools.features.pdf_viewer import PDFJSBridge


class TestPDFJSBridge:
    """PDFJSBridge sınıfı testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """PyQt uygulaması"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def bridge(self, app):
        """PDFJSBridge instance'ı"""
        return PDFJSBridge()
    
    def test_bridge_creation(self, bridge):
        """Bridge başarıyla oluşturulmalı"""
        assert bridge is not None
        assert isinstance(bridge, PDFJSBridge)
        assert isinstance(bridge, QObject)
    
    def test_bridge_signals_exist(self, bridge):
        """Tüm sinyaller mevcut olmalı"""
        # Python'dan React'e gönderilen sinyaller
        assert hasattr(bridge, 'pdfDataChanged')
        assert hasattr(bridge, 'themeChanged')
        assert hasattr(bridge, 'settingsChanged')
        
        # React'den gelen işlemler için sinyaller
        assert hasattr(bridge, 'toolActionRequested')
        assert hasattr(bridge, 'pageChanged')
        assert hasattr(bridge, 'annotationAdded')
        assert hasattr(bridge, 'bookmarkAdded')
    
    def test_initial_state(self, bridge):
        """Başlangıç durumu doğru olmalı"""
        assert bridge._pdf_data is None
        assert bridge._mutex is not None
        assert len(bridge._tool_handlers) > 0
    
    def test_tool_handlers_exist(self, bridge):
        """Tool handler'ları mevcut olmalı"""
        expected_tools = [
            'zoom-in', 'zoom-out', 'rotate', 'split', 'merge',
            'encrypt', 'decrypt', 'highlight', 'text-note',
            'summarize', 'extract'
        ]
        
        for tool in expected_tools:
            assert tool in bridge._tool_handlers
            assert callable(bridge._tool_handlers[tool])


class TestToolActionHandling:
    """Tool action işleme testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def bridge(self, app):
        return PDFJSBridge()
    
    def test_on_tool_action_valid_json(self, bridge):
        """Geçerli JSON ile tool action"""
        # Test verileri
        action_data = json.dumps({
            'toolId': 'zoom-in',
            'data': {'zoom': 100}
        })
        
        # Signal spy oluştur
        signal_spy = Mock()
        bridge.toolActionRequested.connect(signal_spy)
        
        # Action çalıştır
        result = bridge.onToolAction(action_data)
        
        # Sonucu kontrol et
        result_data = json.loads(result)
        assert result_data['success'] is True
        assert 'result' in result_data
        
        # Signal'ın emit edildiğini kontrol et
        signal_spy.assert_called_once_with('zoom-in', {'zoom': 100})
    
    def test_on_tool_action_invalid_json(self, bridge):
        """Geçersiz JSON ile hata kontrolü"""
        # Geçersiz JSON
        action_data = "invalid json data"
        
        result = bridge.onToolAction(action_data)
        result_data = json.loads(result)
        
        assert result_data['success'] is False
        assert 'error' in result_data
    
    def test_on_tool_action_unknown_tool(self, bridge):
        """Bilinmeyen tool için genel yanıt"""
        action_data = json.dumps({
            'toolId': 'unknown-tool',
            'data': {}
        })
        
        result = bridge.onToolAction(action_data)
        result_data = json.loads(result)
        
        assert result_data['success'] is True
        assert 'unknown-tool' in result_data['message']
    
    def test_zoom_in_handler(self, bridge):
        """Zoom-in handler testi"""
        data = {'zoom': 100}
        result = bridge._handle_zoom_in(data)
        
        assert 'zoom' in result
        assert result['zoom'] == 125  # 100 + 25
    
    def test_zoom_out_handler(self, bridge):
        """Zoom-out handler testi"""
        data = {'zoom': 100}
        result = bridge._handle_zoom_out(data)
        
        assert 'zoom' in result
        assert result['zoom'] == 75  # 100 - 25
    
    def test_zoom_limits(self, bridge):
        """Zoom limitleri testi"""
        # Maksimum zoom
        data = {'zoom': 500}
        result = bridge._handle_zoom_in(data)
        assert result['zoom'] == 500  # Değişmemeli
        
        # Minimum zoom
        data = {'zoom': 25}
        result = bridge._handle_zoom_out(data)
        assert result['zoom'] == 25  # Değişmemeli
    
    def test_rotate_handler(self, bridge):
        """Rotate handler testi"""
        # İlk döndürme
        data = {'rotation': 0}
        result = bridge._handle_rotate(data)
        assert result['rotation'] == 90
        
        # Tam tur tamamlama
        data = {'rotation': 270}
        result = bridge._handle_rotate(data)
        assert result['rotation'] == 0  # 360 % 360 = 0


class TestPageAndAnnotationHandling:
    """Sayfa ve annotation işleme testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def bridge(self, app):
        return PDFJSBridge()
    
    def test_on_page_change_valid(self, bridge):
        """Geçerli sayfa değişimi"""
        page_data = json.dumps({'page': 5})
        
        signal_spy = Mock()
        bridge.pageChanged.connect(signal_spy)
        
        bridge.onPageChange(page_data)
        signal_spy.assert_called_once_with(5)
    
    def test_on_page_change_invalid_json(self, bridge):
        """Geçersiz JSON ile sayfa değişimi"""
        # Hata çıktısını bastır (test için)
        with patch('builtins.print'):
            bridge.onPageChange("invalid json")
        # Hata durumunda exception raise edilmemeli
    
    def test_on_annotation_add_valid(self, bridge):
        """Geçerli annotation ekleme"""
        annotation_data = json.dumps({
            'id': 123,
            'type': 'highlight',
            'page': 1,
            'content': 'Test annotation'
        })
        
        signal_spy = Mock()
        bridge.annotationAdded.connect(signal_spy)
        
        bridge.onAnnotationAdd(annotation_data)
        signal_spy.assert_called_once()
        
        # Çağrılan argümanı kontrol et
        call_args = signal_spy.call_args[0][0]
        assert call_args['id'] == 123
        assert call_args['type'] == 'highlight'


class TestDataUpdates:
    """Veri güncelleme testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def bridge(self, app):
        return PDFJSBridge()
    
    def test_update_pdf_data(self, bridge):
        """PDF verisi güncelleme"""
        pdf_data = {
            'fileName': 'test.pdf',
            'totalPages': 10,
            'fileSize': 1024
        }
        
        signal_spy = Mock()
        bridge.pdfDataChanged.connect(signal_spy)
        
        bridge.update_pdf_data(pdf_data)
        
        # Internal state'in güncellendiğini kontrol et
        assert bridge._pdf_data == pdf_data
        
        # Signal'ın emit edildiğini kontrol et
        signal_spy.assert_called_once()
        call_args = signal_spy.call_args[0][0]
        emitted_data = json.loads(call_args)
        assert emitted_data == pdf_data
    
    def test_update_theme(self, bridge):
        """Tema güncelleme"""
        signal_spy = Mock()
        bridge.themeChanged.connect(signal_spy)
        
        bridge.update_theme('dark')
        signal_spy.assert_called_once_with('dark')
    
    def test_update_settings(self, bridge):
        """Ayarlar güncelleme"""
        settings = {
            'showToolbar': True,
            'enableAnnotations': True,
            'language': 'tr'
        }
        
        signal_spy = Mock()
        bridge.settingsChanged.connect(signal_spy)
        
        bridge.update_settings(settings)
        
        signal_spy.assert_called_once()
        call_args = signal_spy.call_args[0][0]
        emitted_settings = json.loads(call_args)
        assert emitted_settings == settings


class TestWebChannelIntegration:
    """QWebChannel entegrasyon testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def web_channel_setup(self, app):
        """QWebChannel kurulum testi"""
        bridge = PDFJSBridge()
        channel = QWebChannel()
        channel.registerObject('pdfBridge', bridge)
        
        return {'bridge': bridge, 'channel': channel}
    
    def test_web_channel_registration(self, web_channel_setup):
        """Bridge'in web channel'a kaydı"""
        bridge = web_channel_setup['bridge']
        channel = web_channel_setup['channel']
        
        # Bridge'in channel'da kayıtlı olduğunu kontrol et
        registered_objects = channel.registeredObjects()
        assert 'pdfBridge' in registered_objects
        assert registered_objects['pdfBridge'] is bridge
    
    def test_bridge_slots_callable(self, web_channel_setup):
        """Bridge slot'larının çağrılabilir olduğunu test et"""
        bridge = web_channel_setup['bridge']
        
        # onToolAction slot'ını test et
        test_action = json.dumps({'toolId': 'test', 'data': {}})
        result = bridge.onToolAction(test_action)
        
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert 'success' in result_data


class TestErrorHandling:
    """Hata işleme testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def bridge(self, app):
        return PDFJSBridge()
    
    def test_tool_handler_exception(self, bridge):
        """Tool handler'da exception durumu"""
        # Handler'ı mock'la ve exception fırlat
        original_handler = bridge._tool_handlers['zoom-in']
        bridge._tool_handlers['zoom-in'] = Mock(side_effect=Exception("Test error"))
        
        try:
            action_data = json.dumps({
                'toolId': 'zoom-in',
                'data': {'zoom': 100}
            })
            
            result = bridge.onToolAction(action_data)
            result_data = json.loads(result)
            
            # Hata durumunda bile başarılı yanıt vermeli (genel handler devreye girer)
            assert result_data['success'] is True
        finally:
            # Handler'ı geri yükle
            bridge._tool_handlers['zoom-in'] = original_handler
    
    def test_mutex_thread_safety(self, bridge):
        """Mutex ile thread safety"""
        # Bu test threading gerektirir, basit bir kontrol yapıyoruz
        pdf_data1 = {'test': 'data1'}
        pdf_data2 = {'test': 'data2'}
        
        # Sıralı çağrılar yapıldığında son veri korunmalı
        bridge.update_pdf_data(pdf_data1)
        bridge.update_pdf_data(pdf_data2)
        
        assert bridge._pdf_data == pdf_data2


# Yardımcı test fonksiyonları
def create_mock_web_channel():
    """Test için mock QWebChannel oluştur"""
    channel = Mock(spec=QWebChannel)
    channel.registerObject = Mock()
    channel.registeredObjects = Mock(return_value={})
    return channel


def create_test_pdf_data():
    """Test için örnek PDF verisi"""
    return {
        'filePath': '/test/path/document.pdf',
        'fileName': 'document.pdf',
        'fileSize': 1024000,
        'totalPages': 15,
        'metadata': {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject'
        },
        'lastModified': 1640995200
    }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
