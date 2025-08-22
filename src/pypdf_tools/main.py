#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools Ana Uygulama
Hibrit masaüstü PDF yönetim uygulaması
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QMenuBar, QStatusBar, QToolBar, QFileDialog,
    QMessageBox, QSplashScreen, QProgressBar, QLabel
)
from PyQt6.QtCore import QTimer, QSettings, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QPixmap, QKeySequence

from pypdf_tools._version import __version__, APP_NAME, APP_DISPLAY_NAME
from pypdf_tools.features.pdf_viewer import PDFViewerContainer


class MainWindow(QMainWindow):
    """
    PyPDF-Tools ana pencere sınıfı
    React tabanlı PDF görüntüleyici ve PyQt6 menü sistemi
    """
    
    # Sinyaller
    pdfLoaded = pyqtSignal(str)
    themeChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Uygulama ayarları
        self.settings = QSettings('PyPDF-Tools', APP_NAME)
        
        # Ana widget'lar
        self.pdf_viewer_container: Optional[PDFViewerContainer] = None
        self.status_bar: Optional[QStatusBar] = None
        
        # Durum değişkenleri
        self.current_pdf_path: Optional[str] = None
        self.current_theme = 'light'
        self.is_fullscreen = False
        
        # UI kurulumu
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._load_settings()
        self._connect_signals()
        
        # Pencere ayarları
        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
    def _setup_ui(self) -> None:
        """Ana UI bileşenlerini kur"""
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF Viewer Container
        self.pdf_viewer_container = PDFViewerContainer(self)
        main_layout.addWidget(self.pdf_viewer_container)
        
    def _setup_menus(self) -> None:
        """Menü çubuğunu kur"""
        menubar = self.menuBar()
        
        # Dosya Menüsü
        file_menu = menubar.addMenu('&Dosya')
        
        # Aç
        open_action = QAction('&Aç...', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip('PDF dosyası aç')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Son dosyalar
        self.recent_files_menu = file_menu.addMenu('Son &Dosyalar')
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        # Kaydet
        save_action = QAction('&Kaydet', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip('Dosyayı kaydet')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Farklı kaydet
        save_as_action = QAction('&Farklı Kaydet...', self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip('Farklı isimle kaydet')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Yazdır
        print_action = QAction('&Yazdır...', self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.setStatusTip('Dosyayı yazdır')
        print_action.triggered.connect(self.print_file)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        # Çıkış
        exit_action = QAction('Ç&ıkış', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip('Uygulamadan çık')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Düzenle Menüsü
        edit_menu = menubar.addMenu('&Düzenle')
        
        # Geri al
        undo_action = QAction('&Geri Al', self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setStatusTip('Son işlemi geri al')
        edit_menu.addAction(undo_action)
        
        # İleri al
        redo_action = QAction('İ&leri Al', self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setStatusTip('İşlemi tekrarla')
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Kopyala
        copy_action = QAction('&Kopyala', self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setStatusTip('Seçilen metni kopyala')
        edit_menu.addAction(copy_action)
        
        # Görünüm Menüsü
        view_menu = menubar.addMenu('&Görünüm')
        
        # Tema seçimi
        theme_menu = view_menu.addMenu('&Tema')
        
        themes = [
            ('Açık', 'light'),
            ('Koyu', 'dark'),
            ('Neon', 'neon'),
            ('Gece Yarısı', 'midnight')
        ]
        
        for theme_name, theme_id in themes:
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            theme_action.triggered.connect(lambda checked, t=theme_id: self.change_theme(t))
            theme_menu.addAction(theme_action)
            
            if theme_id == self.current_theme:
                theme_action.setChecked(True)
        
        view_menu.addSeparator()
        
        # Tam ekran
        fullscreen_action = QAction('&Tam Ekran', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.setStatusTip('Tam ekran moduna geç')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Araçlar Menüsü
        tools_menu = menubar.addMenu('&Araçlar')
        
        # PDF Birleştir
        merge_action = QAction('PDF &Birleştir...', self)
        merge_action.setStatusTip('Birden fazla PDF dosyasını birleştir')
        merge_action.triggered.connect(self.merge_pdfs)
        tools_menu.addAction(merge_action)
        
        # PDF Böl
        split_action = QAction('PDF &Böl...', self)
        split_action.setStatusTip('PDF dosyasını böl')
        split_action.triggered.connect(self.split_pdf)
        tools_menu.addAction(split_action)
        
        tools_menu.addSeparator()
        
        # Şifrele
        encrypt_action = QAction('&Şifrele...', self)
        encrypt_action.setStatusTip('PDF dosyasını şifrele')
        encrypt_action.triggered.connect(self.encrypt_pdf)
        tools_menu.addAction(encrypt_action)
        
        # Şifre Kaldır
        decrypt_action = QAction('Şifre &Kaldır...', self)
        decrypt_action.setStatusTip('PDF şifresini kaldır')
        decrypt_action.triggered.connect(self.decrypt_pdf)
        tools_menu.addAction(decrypt_action)
        
        tools_menu.addSeparator()
        
        # Ayarlar
        settings_action = QAction('&Ayarlar...', self)
        settings_action.setStatusTip('Uygulama ayarları')
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Yardım Menüsü
        help_menu = menubar.addMenu('&Yardım')
        
        # Hakkında
        about_action = QAction('&Hakkında...', self)
        about_action.setStatusTip('Uygulama hakkında bilgi')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def _setup_toolbar(self) -> None:
        """Araç çubuğunu kur"""
        toolbar = QToolBar('Ana Araçlar')
        self.addToolBar(toolbar)
        
        # Aç butonu
        open_action = QAction('Aç', self)
        open_action.setStatusTip('PDF dosyası aç')
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Kaydet butonu
        save_action = QAction('Kaydet', self)
        save_action.setStatusTip('Dosyayı kaydet')
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Yazdır butonu
        print_action = QAction('Yazdır', self)
        print_action.setStatusTip('Dosyayı yazdır')
        print_action.triggered.connect(self.print_file)
        toolbar.addAction(print_action)
    
    def _setup_statusbar(self) -> None:
        """Durum çubuğunu kur"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Hazır durumu göster
        self.status_bar.showMessage('Hazır')
        
        # Sağ tarafta bilgi göster
        self.status_label = QLabel('PDF yüklü değil')
        self.status_bar.addPermanentWidget(self.status_label)
    
    def _load_settings(self) -> None:
        """Kullanıcı ayarlarını yükle"""
        # Pencere boyutu ve konumu
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        # Tema
        saved_theme = self.settings.value('theme', 'light')
        self.change_theme(saved_theme)
        
        # Son açılan dosya
        last_file = self.settings.value('last_file')
        if last_file and Path(last_file).exists():
            self.current_pdf_path = last_file
    
    def _connect_signals(self) -> None:
        """Sinyal bağlantılarını kur"""
        if self.pdf_viewer_container:
            # PDF yüklendiğinde
            self.pdf_viewer_container.pdf_viewer.pdfLoaded.connect(self._on_pdf_loaded)
            # Tool action'lar
            self.pdf_viewer_container.pdf_viewer.toolActionPerformed.connect(self._on_tool_action)
    
    def _update_recent_files_menu(self) -> None:
        """Son dosyalar menüsünü güncelle"""
        self.recent_files_menu.clear()
        
        recent_files = self.settings.value('recent_files', [])
        if not isinstance(recent_files, list):
            recent_files = []
        
        for i, file_path in enumerate(recent_files[:10]):  # Son 10 dosya
            if Path(file_path).exists():
                action = QAction(f"{i+1}. {Path(file_path).name}", self)
                action.setStatusTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.load_pdf(path))
                self.recent_files_menu.addAction(action)
        
        if not recent_files:
            no_recent_action = QAction('Son dosya yok', self)
            no_recent_action.setEnabled(False)
            self.recent_files_menu.addAction(no_recent_action)
    
    def _add_to_recent_files(self, file_path: str) -> None:
        """Dosyayı son dosyalar listesine ekle"""
        recent_files = self.settings.value('recent_files', [])
        if not isinstance(recent_files, list):
            recent_files = []
        
        # Varsa listeden kaldır
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Başa ekle
        recent_files.insert(0, file_path)
        
        # Maksimum 10 dosya tut
        recent_files = recent_files[:10]
        
        # Kaydet
        self.settings.setValue('recent_files', recent_files)
        self._update_recent_files_menu()
    
    # Slot fonksiyonları
    def open_file(self) -> None:
        """PDF dosyası aç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'PDF Dosyası Aç',
            self.settings.value('last_directory', ''),
            'PDF Dosyaları (*.pdf);;Tüm Dosyalar (*.*)'
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path: str) -> bool:
        """PDF dosyasını yükle"""
        try:
            if not Path(file_path).exists():
                QMessageBox.warning(self, 'Hata', f'Dosya bulunamadı: {file_path}')
                return False
            
            # PDF'i viewer'da yükle
            success = self.pdf_viewer_container.load_pdf(file_path)
            
            if success:
                self.current_pdf_path = file_path
                self.settings.setValue('last_file', file_path)
                self.settings.setValue('last_directory', str(Path(file_path).parent))
                self._add_to_recent_files(file_path)
                
                # Başlığı güncelle
                self.setWindowTitle(f"{APP_DISPLAY_NAME} - {Path(file_path).name}")
                
                # Durum çubuğunu güncelle
                self.status_bar.showMessage(f'PDF yüklendi: {Path(file_path).name}')
                self.status_label.setText(f'{Path(file_path).name}')
                
                return True
            else:
                QMessageBox.critical(self, 'Hata', 'PDF dosyası yüklenemedi!')
                return False
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'PDF yükleme hatası: {str(e)}')
            return False
    
    def save_file(self) -> None:
        """Mevcut PDF'i kaydet"""
        if not self.current_pdf_path:
            self.save_file_as()
        else:
            # Kaydetme işlemi - implementasyon gerekir
            QMessageBox.information(self, 'Bilgi', 'Kaydetme özelliği geliştirilecek')
    
    def save_file_as(self) -> None:
        """PDF'i farklı kaydet"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, 'Uyarı', 'Kaydetmek için önce bir PDF yükleyin')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'PDF Farklı Kaydet',
            self.settings.value('last_directory', ''),
            'PDF Dosyaları (*.pdf)'
        )
        
        if file_path:
            # Kaydetme işlemi - implementasyon gerekir
            QMessageBox.information(self, 'Bilgi', f'Farklı kaydetme: {file_path}\nÖzellik geliştirilecek')
    
    def print_file(self) -> None:
        """PDF yazdır"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, 'Uyarı', 'Yazdırmak için önce bir PDF yükleyin')
            return
        
        # Yazdırma işlemi - implementasyon gerekir
        QMessageBox.information(self, 'Bilgi', 'Yazdırma özelliği geliştirilecek')
    
    def change_theme(self, theme: str) -> None:
        """Tema değiştir"""
        self.current_theme = theme
        self.settings.setValue('theme', theme)
        
        # PDF viewer'a tema bilgisini gönder
        if self.pdf_viewer_container:
            self.pdf_viewer_container.set_theme(theme)
        
        # Ana pencere temasını da değiştir (opsiyonel)
        self._apply_window_theme(theme)
        
        self.themeChanged.emit(theme)
    
    def _apply_window_theme(self, theme: str) -> None:
        """Ana pencere temasını uygula"""
        # Basit tema uygulaması
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: white; }
                QMenuBar { background-color: #3c3c3c; color: white; }
                QMenuBar::item { background-color: transparent; }
                QMenuBar::item:selected { background-color: #4a4a4a; }
                QMenu { background-color: #3c3c3c; color: white; border: 1px solid #555; }
                QMenu::item:selected { background-color: #4a4a4a; }
                QToolBar { background-color: #3c3c3c; border: 1px solid #555; }
                QStatusBar { background-color: #3c3c3c; color: white; }
            """)
        else:
            self.setStyleSheet("")  # Varsayılan tema
    
    def toggle_fullscreen(self) -> None:
        """Tam ekran modunu aç/kapat"""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
    
    def merge_pdfs(self) -> None:
        """PDF birleştirme dialog'u aç"""
        QMessageBox.information(self, 'Bilgi', 'PDF birleştirme özelliği geliştirilecek')
    
    def split_pdf(self) -> None:
        """PDF bölme dialog'u aç"""
        QMessageBox.information(self, 'Bilgi', 'PDF bölme özelliği geliştirilecek')
    
    def encrypt_pdf(self) -> None:
        """PDF şifreleme dialog'u aç"""
        QMessageBox.information(self, 'Bilgi', 'PDF şifreleme özelliği geliştirilecek')
    
    def decrypt_pdf(self) -> None:
        """PDF şifre kaldırma dialog'u aç"""
        QMessageBox.information(self, 'Bilgi', 'PDF şifre kaldırma özelliği geliştirilecek')
    
    def show_settings(self) -> None:
        """Ayarlar dialog'u aç"""
        QMessageBox.information(self, 'Bilgi', 'Ayarlar dialog'u geliştirilecek')
    
    def show_about(self) -> None:
        """Hakkında dialog'u göster"""
        QMessageBox.about(
            self,
            f'{APP_DISPLAY_NAME} Hakkında',
            f"""
            <h3>{APP_DISPLAY_NAME}</h3>
            <p><b>Sürüm:</b> {__version__}</p>
            <p><b>Açıklama:</b> Hibrit masaüstü PDF yönetim ve düzenleme uygulaması</p>
            <p><b>Teknolojiler:</b> Python, PyQt6, React</p>
            <p><b>Geliştirici:</b> Fatih Bucaklıoğlu</p>
            <p><b>GitHub:</b> <a href="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools">PyPDF-Tools</a></p>
            <p>Bu uygulama PDF dosyalarını görüntülemek, düzenlemek ve yönetmek için geliştirilmiştir.</p>
            """
        )
    
    # Event handlers
    def _on_pdf_loaded(self, pdf_data: Dict[str, Any]) -> None:
        """PDF yüklendiğinde çağrılır"""
        self.status_bar.showMessage(f"PDF yüklendi: {pdf_data.get('fileName', 'Bilinmiyor')}")
    
    def _on_tool_action(self, tool_id: str, data: Dict[str, Any]) -> None:
        """Tool action gerçekleştiğinde çağrılır"""
        self.status_bar.showMessage(f"Araç kullanıldı: {tool_id}", 2000)
    
    # Pencere kapatma
    def closeEvent(self, event) -> None:
        """Pencere kapatılırken ayarları kaydet"""
        self.settings.setValue('geometry', self.saveGeometry())
        super().closeEvent(event)


class SplashScreen(QSplashScreen):
    """Uygulama başlangıç ekranı"""
    
    def __init__(self):
        # Basit bir splash ekranı oluştur
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.GlobalColor.white)
        super().__init__(pixmap)
        
        # Metin ekle
        self.showMessage(
            f"{APP_DISPLAY_NAME} v{__version__}\nYükleniyor...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.black
        )


def create_app() -> QApplication:
    """PyQt uygulamasını oluştur"""
    app = QApplication(sys.argv)
    
    # Uygulama meta bilgileri
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName('PyPDF-Tools')
    
    return app


def main() -> int:
    """Ana CLI entry point"""
    parser = argparse.ArgumentParser(description=f'{APP_DISPLAY_NAME} - Hibrit PDF Uygulaması')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {__version__}')
    parser.add_argument('--no-splash', action='store_true', help='Splash ekranını gösterme')
    parser.add_argument('file', nargs='?', help='Açılacak PDF dosyası')
    
    args = parser.parse_args()
    
    # Qt uygulamasını oluştur
    app = create_app()
    
    # Splash screen göster
    splash = None
    if not args.no_splash:
        splash = SplashScreen()
        splash.show()
        app.processEvents()
    
    try:
        # Ana pencereyi oluştur
        main_window = MainWindow()
        
        # Dosya belirtilmişse yükle
        if args.file:
            QTimer.singleShot(500, lambda: main_window.load_pdf(args.file))
        
        # Splash'i kapat ve ana pencereyi göster
        if splash:
            splash.finish(main_window)
        
        main_window.show()
        
        # Uygulamayı çalıştır
        return app.exec()
        
    except Exception as e:
        QMessageBox.critical(None, 'Kritik Hata', f'Uygulama başlatılamadı:\n{str(e)}')
        return 1


def main_gui() -> int:
    """GUI entry point (setup.py için)"""
    return main()


if __name__ == '__main__':
    sys.exit(main())
