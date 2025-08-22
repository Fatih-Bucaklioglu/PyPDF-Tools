#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools Ana Uygulama Test Modülü
Ana QMainWindow ve QWebEngineView bileşenlerinin testleri
"""

import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Test edilecek modüller
from pypdf_tools.main import MainWindow, create_app
from pypdf_tools.features.pdf_viewer import PDFViewerWidget, PDFViewerContainer


class TestMainWindow:
    """MainWindow sınıfı testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """PyQt uygulamasını oluştur"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def main_window(self, app):
        """MainWindow instance'ı oluştur"""
        # React build dizini mevcut olmayabilir, mock'la
        with patch('pypdf_tools.features.pdf_viewer.PDFViewerWidget._find_web_build_path') as mock_path:
            # Geçici bir HTML dosyası oluştur
            temp_dir = tempfile.mkdtemp()
            temp_html = Path(temp_dir) / 'index.html'
            temp_html.write_text("""
                <!DOCTYPE html>
                <html>
                <head><title>Test</title></head>
                <body><div id="root">Test PDF Viewer</div></body>
                </html>
            """)
            
            mock_path.return_value = str(temp_dir)
            window = MainWindow()
            yield window
            window.close()
    
    def test_main_window_creation(self, main_window):
        """Ana pencere başarıyla oluşturulmalı"""
        assert main_window is not None
        assert isinstance(main_window, MainWindow)
        assert main_window.windowTitle() == "PyPDF Tools"
    
    def test_central_widget_exists(self, main_window):
        """Merkezi widget mevcut olmalı"""
        central_widget = main_window.centralWidget()
        assert central_widget is not None
    
    def test_pdf_viewer_container_exists(self, main_window):
        """PDF viewer container mevcut olmalı"""
        assert main_window.pdf_viewer_container is not None
        assert isinstance(main_window.pdf_viewer_container, PDFViewerContainer)
    
    def test_menu_bar_exists(self, main_window):
        """Menü çubuğu mevcut olmalı"""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # Menülerin varlığını kontrol et
        menu_titles = [action.text() for action in menu_bar.actions()]
        expected_menus = ['&Dosya', '&Düzenle', '&Görünüm', '&Araçlar', '&Yardım']
        
        for expected_menu in expected_menus:
            assert any(expected_menu in title for title in menu_titles)
    
    def test_status_bar_exists(self, main_window):
        """Durum çubuğu mevcut olmalı"""
        status_bar = main_window.statusBar()
        assert status_bar is not None
        assert main_window.status_bar is status_bar
    
    def test_toolbar_exists(self, main_window):
        """Araç çubuğu mevcut olmalı"""
        toolbars = main_window.findChildren(type(main_window.addToolBar("")))
        assert len(toolbars) > 0
    
    @patch('pypdf_tools.main.QFileDialog.getOpenFileName')
    def test_open_file_dialog(self, mock_dialog, main_window):
        """Dosya aç dialog'u çalışmalı"""
        # Dialog mock'ı
        test_file = "/fake/path/test.pdf"
        mock_dialog.return_value = (test_file, "PDF Files (*.pdf)")
        
        # load_pdf metodunu mock'la
        with patch.object(main_window, 'load_pdf', return_value=True) as mock_load:
            main_window.open_file()
            mock_load.assert_called_once_with(test_file)
    
    def test_theme_change(self, main_window):
        """Tema değişimi çalışmalı"""
        original_theme = main_window.current_theme
        new_theme = 'dark' if original_theme != 'dark' else 'light'
        
        # PDF viewer'ın tema değişimini mock'la
        with patch.object(main_window.pdf_viewer_container, 'set_theme') as mock_set_theme:
            main_window.change_theme(new_theme)
            
            assert main_window.current_theme == new_theme
            mock_set_theme.assert_called_once_with(new_theme)
    
    def test_fullscreen_toggle(self, main_window):
        """Tam ekran geçişi çalışmalı"""
        original_state = main_window.is_fullscreen
        
        with patch.object(main_window, 'showFullScreen') as mock_fullscreen, \
             patch.object(main_window, 'showNormal') as mock_normal:
            
            main_window.toggle_fullscreen()
            
            if not original_state:
                mock_fullscreen.assert_called_once()
                assert main_window.is_fullscreen
            else:
                mock_normal.assert_called_once()
                assert not main_window.is_fullscreen


class TestPDFViewerWidget:
    """PDFViewerWidget sınıfı testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """PyQt uygulamasını oluştur"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def temp_html_file(self):
        """Test için geçici HTML dosyası oluştur"""
        temp_dir = tempfile.mkdtemp()
        temp_html = Path(temp_dir) / 'index.html'
        temp_html.write_text("""
            <!DOCTYPE html>
            <html>
            <head><title>PDF Viewer Test</title></head>
            <body>
                <div id="root">
                    <h1>Test PDF Viewer</h1>
                    <script>
                        // Mock QWebChannel
                        window.qt = {
                            webChannelTransport: {},
                            QWebChannel: function(transport, callback) {
                                this.objects = {
                                    pdfBridge: {
                                        onToolAction: function() { return '{"success": true}'; },
                                        onPageChange: function() {},
                                        onAnnotationAdd: function() {}
                                    }
                                };
                                if (callback) callback(this);
                            }
                        };
                    </script>
                </div>
            </body>
            </html>
        """)
        return str(temp_dir)
    
    @pytest.fixture
    def pdf_viewer(self, app, temp_html_file):
        """PDFViewerWidget instance'ı oluştur"""
        with patch('pypdf_tools.features.pdf_viewer.PDFViewerWidget._find_web_build_path') as mock_path:
            mock_path.return_value = temp_html_file
            viewer = PDFViewerWidget()
            yield viewer
            viewer.close()
    
    def test_pdf_viewer_creation(self, pdf_viewer):
        """PDF viewer başarıyla oluşturulmalı"""
        assert pdf_viewer is not None
        assert isinstance(pdf_viewer, PDFViewerWidget)
        assert isinstance(pdf_viewer, QWebEngineView)
    
    def test_web_channel_setup(self, pdf_viewer):
        """QWebChannel kurulumu yapılmalı"""
        assert pdf_viewer._channel is not None
        assert pdf_viewer._bridge is not None
    
    def test_bridge_signals_exist(self, pdf_viewer):
        """Bridge sinyalleri mevcut olmalı"""
        bridge = pdf_viewer._bridge
        
        # Sinyallerin varlığını kontrol et
        assert hasattr(bridge, 'pdfDataChanged')
        assert hasattr(bridge, 'themeChanged')
        assert hasattr(bridge, 'settingsChanged')
        assert hasattr(bridge, 'toolActionRequested')
        assert hasattr(bridge, 'pageChanged')
        assert hasattr(bridge, 'annotationAdded')
    
    def test_theme_setting(self, pdf_viewer):
        """Tema ayarlama çalışmalı"""
        test_themes = ['light', 'dark', 'neon', 'midnight']
        
        for theme in test_themes:
            pdf_viewer.set_theme(theme)
            assert pdf_viewer._current_theme == theme
    
    @patch('pypdf_tools.features.pdf_viewer.Path.exists')
    def test_load_pdf_file_not_found(self, mock_exists, pdf_viewer):
        """Dosya bulunamadığında hata vermeli"""
        mock_exists.return_value = False
        
        result = pdf_viewer.load_pdf("/fake/path/test.pdf")
        assert not result
    
    def test_tool_action_handling(self, pdf_viewer):
        """Tool action handling çalışmalı"""
        bridge = pdf_viewer._bridge
        
        # Test data
        test_action = '{"toolId": "zoom-in", "data": {"zoom": 100}}'
        
        # onToolAction çağrısı
        result = bridge.onToolAction(test_action)
        result_data = eval(result)  # JSON parse yerine eval - test için
        
        assert result_data['success'] is True


class TestPDFViewerContainer:
    """PDFViewerContainer sınıfı testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """PyQt uygulamasını oluştur"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def container(self, app):
        """PDFViewerContainer instance'ı oluştur"""
        with patch('pypdf_tools.features.pdf_viewer.PDFViewerWidget._find_web_build_path') as mock_path:
            temp_dir = tempfile.mkdtemp()
            temp_html = Path(temp_dir) / 'index.html'
            temp_html.write_text('<html><body>Test</body></html>')
            mock_path.return_value = str(temp_dir)
            
            container = PDFViewerContainer()
            yield container
            container.close()
    
    def test_container_creation(self, container):
        """Container başarıyla oluşturulmalı"""
        assert container is not None
        assert isinstance(container, PDFViewerContainer)
    
    def test_pdf_viewer_in_container(self, container):
        """Container içinde PDF viewer olmalı"""
        assert container.pdf_viewer is not None
        assert isinstance(container.pdf_viewer, PDFViewerWidget)
    
    def test_load_pdf_delegates_to_viewer(self, container):
        """load_pdf çağrısı viewer'a yönlendirilmeli"""
        with patch.object(container.pdf_viewer, 'load_pdf', return_value=True) as mock_load:
            result = container.load_pdf("/fake/test.pdf")
            
            assert result is True
            mock_load.assert_called_once_with("/fake/test.pdf")
    
    def test_set_theme_delegates_to_viewer(self, container):
        """set_theme çağrısı viewer'a yönlendirilmeli"""
        with patch.object(container.pdf_viewer, 'set_theme') as mock_set_theme:
            container.set_theme('dark')
            mock_set_theme.assert_called_once_with('dark')


class TestCreateApp:
    """create_app fonksiyonu testleri"""
    
    def test_create_app_returns_qapplication(self):
        """create_app QApplication döndürmeli"""
        if QApplication.instance():
            # Zaten bir instance varsa onu kullan
            app = QApplication.instance()
        else:
            app = create_app()
        
        assert isinstance(app, QApplication)
        assert app.applicationName() == "pypdf-tools"
        assert app.applicationDisplayName() == "PyPDF Tools"


# Integration testleri
class TestIntegration:
    """Entegrasyon testleri"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Test uygulaması"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    def test_main_window_with_pdf_viewer_integration(self, app):
        """MainWindow ve PDFViewer entegrasyonu"""
        with patch('pypdf_tools.features.pdf_viewer.PDFViewerWidget._find_web_build_path') as mock_path:
            temp_dir = tempfile.mkdtemp()
            temp_html = Path(temp_dir) / 'index.html'
            temp_html.write_text('<html><body>Integration Test</body></html>')
            mock_path.return_value = str(temp_dir)
            
            # Ana pencereyi oluştur
            main_window = MainWindow()
            
            try:
                # PDF viewer'ın ana pencerede olduğunu kontrol et
                assert main_window.pdf_viewer_container is not None
                
                # Sinyal bağlantılarının yapıldığını kontrol et
                pdf_viewer = main_window.pdf_viewer_container.pdf_viewer
                assert pdf_viewer._bridge is not None
                
                # Tema değişiminin çalıştığını test et
                with patch.object(main_window.pdf_viewer_container, 'set_theme') as mock_set_theme:
                    main_window.change_theme('dark')
                    mock_set_theme.assert_called_once_with('dark')
                
            finally:
                main_window.close()


# Test konfigürasyonu ve yardımcı fonksiyonlar
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Test ortamını hazırla"""
    # QT_QPA_PLATFORM ortam değişkenini ayarla (headless test için)
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


def test_imports():
    """Tüm modüllerin başarıyla import edildiğini test et"""
    try:
        from pypdf_tools.main import MainWindow, create_app
        from pypdf_tools.features.pdf_viewer import PDFViewerWidget, PDFViewerContainer
        assert True  # Import başarılı
    except ImportError as e:
        pytest.fail(f"Import hatası: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
