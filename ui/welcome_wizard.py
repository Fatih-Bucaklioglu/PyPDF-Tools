#!/usr/bin/env python3
"""
İlk Çalıştırma Sihirbazı
Modern hoşgeldin ekranı ve temel yapılandırma
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    pyqtSignal, QRect, QThread, pyqtSlot
)
from PyQt6.QtGui import (
    QPixmap, QFont, QPalette, QColor, QPainter, 
    QLinearGradient, QBrush, QIcon, QMovie
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QStackedWidget,
    QFrame, QGroupBox, QRadioButton, QCheckBox,
    QComboBox, QLineEdit, QTextEdit, QSpacerItem,
    QSizePolicy, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QSlider, QSpinBox, QTabWidget,
    QScrollArea, QGridLayout, QButtonGroup
)

# Local imports
try:
    from ..core.config_manager import ConfigManager
    from ..core.theme_manager import ThemeManager
    from ..core.language_manager import LanguageManager
    from ..utils.system_info import SystemInfo
    from ..utils.file_utils import create_directory
except ImportError:
    # Fallback for development
    pass

logger = logging.getLogger(__name__)


class AnimatedLabel(QLabel):
    """Animasyonlu etiket widget'ı"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def fade_in(self):
        """Belirme animasyonu"""
        self.setStyleSheet("color: transparent;")
        self.timer = QTimer()
        self.timer.timeout.connect(self._fade_step)
        self.opacity = 0
        self.timer.start(50)
    
    def _fade_step(self):
        """Animasyon adımı"""
        self.opacity += 0.05
        if self.opacity >= 1:
            self.timer.stop()
            self.setStyleSheet("color: inherit;")
        else:
            alpha = int(255 * self.opacity)
            self.setStyleSheet(f"color: rgba(255, 255, 255, {alpha});")


class SetupWorker(QThread):
    """Arka plan kurulum işlemleri"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, setup_data: Dict[str, Any]):
        super().__init__()
        self.setup_data = setup_data
        self.is_cancelled = False
    
    def cancel(self):
        """Kurulumu iptal et"""
        self.is_cancelled = True
    
    def run(self):
        """Kurulum işlemlerini çalıştır"""
        try:
            steps = [
                ("Yapılandırma dosyaları oluşturuluyor...", self._create_config),
                ("Tema ayarları uygulanıyor...", self._apply_theme),
                ("Dil dosyaları hazırlanıyor...", self._setup_language),
                ("OCR dil paketleri kontrol ediliyor...", self._check_ocr_languages),
                ("Klasör izinleri ayarlanıyor...", self._setup_permissions),
                ("Geçici dosyalar temizleniyor...", self._cleanup_temp),
                ("Kurulum tamamlanıyor...", self._finalize_setup),
            ]
            
            for i, (status, func) in enumerate(steps):
                if self.is_cancelled:
                    return
                    
                self.status_updated.emit(status)
                func()
                self.progress_updated.emit(int((i + 1) / len(steps) * 100))
                self.msleep(500)  # Görsel efekt için bekleme
            
            self.finished_signal.emit(True)
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self.finished_signal.emit(False)
    
    def _create_config(self):
        """Yapılandırma dosyalarını oluştur"""
        try:
            config_manager = ConfigManager()
            config_manager.create_default_config(self.setup_data)
        except Exception as e:
            logger.error(f"Config creation failed: {e}")
    
    def _apply_theme(self):
        """Tema ayarlarını uygula"""
        try:
            theme_manager = ThemeManager()
            theme_manager.apply_theme(self.setup_data.get('theme', 'dark'))
        except Exception as e:
            logger.error(f"Theme application failed: {e}")
    
    def _setup_language(self):
        """Dil ayarlarını yapılandır"""
        try:
            lang_manager = LanguageManager()
            lang_manager.set_language(self.setup_data.get('language', 'tr'))
        except Exception as e:
            logger.error(f"Language setup failed: {e}")
    
    def _check_ocr_languages(self):
        """OCR dil paketlerini kontrol et"""
        # OCR dil paketi kontrolü implementasyonu
        pass
    
    def _setup_permissions(self):
        """Klasör izinlerini ayarla"""
        try:
            allowed_dirs = self.setup_data.get('allowed_directories', [])
            for directory in allowed_dirs:
                create_directory(directory)
        except Exception as e:
            logger.error(f"Permission setup failed: {e}")
    
    def _cleanup_temp(self):
        """Geçici dosyaları temizle"""
        # Geçici dosya temizleme implementasyonu
        pass
    
    def _finalize_setup(self):
        """Kurulumu sonlandır"""
        # Son işlemler
        pass


class WelcomeWizard(QDialog):
    """İlk çalıştırma sihirbazı ana sınıfı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_data = {}
        self.current_page = 0
        self.setup_worker = None
        
        self.setWindowTitle("PyPDF-Tools v2.0 - Kurulum Sihirbazı")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        
        # UI bileşenlerini oluştur
        self._setup_ui()
        self._setup_animations()
        self._setup_connections()
        
        # İlk sayfayı göster
        self._show_welcome_page()
    
    def _setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.header_frame = self._create_header()
        main_layout.addWidget(self.header_frame)
        
        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Footer
        self.footer_frame = self._create_footer()
        main_layout.addWidget(self.footer_frame)
        
        self.setLayout(main_layout)
        
        # Sayfaları oluştur
        self._create_pages()
        
        # Tema uygula
        self._apply_wizard_theme()
    
    def _create_header(self) -> QFrame:
        """Header alanını oluştur"""
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2196F3, stop:1 #21CBF3);
                border: none;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/app_icon.png").scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        layout.addWidget(logo_label)
        
        # Başlık
        title_layout = QVBoxLayout()
        self.title_label = QLabel("PyPDF-Tools v2.0")
        self.title_label.setStyleSheet("""
            color: white; 
            font-size: 24px; 
            font-weight: bold;
        """)
        
        self.subtitle_label = QLabel("Modern PDF İşleme Uygulaması")
        self.subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8); 
            font-size: 14px;
        """)
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        layout.addLayout(title_layout)
        
        layout.addStretch()
        header.setLayout(layout)
        
        return header
    
    def _create_footer(self) -> QFrame:
        """Footer alanını oluştur"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        self.back_button = QPushButton("« Geri")
        self.back_button.setEnabled(False)
        self.back_button.clicked.connect(self._go_back)
        
        self.next_button = QPushButton("İleri »")
        self.next_button.clicked.connect(self._go_next)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.cancel_button)
        
        footer.setLayout(layout)
        return footer
    
    def _create_pages(self):
        """Sihirbaz sayfalarını oluştur"""
        # 1. Hoşgeldin sayfası
        self.welcome_page = self._create_welcome_page()
        self.content_stack.addWidget(self.welcome_page)
        
        # 2. Tema seçimi sayfası
        self.theme_page = self._create_theme_page()
        self.content_stack.addWidget(self.theme_page)
        
        # 3. Dil seçimi sayfası
        self.language_page = self._create_language_page()
        self.content_stack.addWidget(self.language_page)
        
        # 4. Güvenlik ayarları sayfası
        self.privacy_page = self._create_privacy_page()
        self.content_stack.addWidget(self.privacy_page)
        
        # 5. OCR ayarları sayfası
        self.ocr_page = self._create_ocr_page()
        self.content_stack.addWidget(self.ocr_page)
        
        # 6. Klasör izinleri sayfası
        self.permissions_page = self._create_permissions_page()
        self.content_stack.addWidget(self.permissions_page)
        
        # 7. Özet sayfası
        self.summary_page = self._create_summary_page()
        self.content_stack.addWidget(self.summary_page)
        
        # 8. Kurulum sayfası
        self.installation_page = self._create_installation_page()
        self.content_stack.addWidget(self.installation_page)
        
        # 9. Tamamlanma sayfası
        self.completion_page = self._create_completion_page()
        self.content_stack.addWidget(self.completion_page)
    
    def _create_welcome_page(self) -> QFrame:
        """Hoşgeldin sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Hoşgeldin mesajı
        welcome_label = AnimatedLabel("""
        <h2>PyPDF-Tools v2.0'a Hoş Geldiniz!</h2>
        <p>Bu sihirbaz, uygulamayı ilk kullanımınız için yapılandırmanıza yardımcı olacak.</p>
        <p>Stirling-PDF'den ilham alınarak geliştirilmiş bu modern PDF işleme uygulaması 
        ile şunları yapabilirsiniz:</p>
        """)
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        # Özellikler listesi
        features_group = QGroupBox("🚀 Ana Özellikler")
        features_layout = QGridLayout()
        
        features = [
            ("📄 PDF Birleştirme & Bölme", "Çoklu PDF dosyalarını birleştirin veya tek dosyayı bölin"),
            ("🗜️ PDF Sıkıştırma", "%90'a kadar boyut azaltımı"),
            ("🔄 Format Dönüştürme", "Word, Excel, PowerPoint ↔ PDF"),
            ("🔍 OCR İşlemi", "50+ dil desteği ile metin tanıma"),
            ("🔒 Güvenlik", "Şifreleme ve dijital imza"),
            ("🎨 Modern Arayüz", "4 farklı tema seçeneği"),
            ("⚡ Otomasyon", "Script desteği ve toplu işlemler"),
            ("🖥️ Cross-Platform", "Windows, macOS, Linux desteği"),
        ]
        
        for i, (title, desc) in enumerate(features):
            row = i // 2
            col = i % 2
            
            feature_frame = QFrame()
            feature_layout = QVBoxLayout()
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; color: #2196F3;")
            
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 12px;")
            
            feature_layout.addWidget(title_label)
            feature_layout.addWidget(desc_label)
            feature_frame.setLayout(feature_layout)
            
            features_layout.addWidget(feature_frame, row, col)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_theme_page(self) -> QFrame:
        """Tema seçimi sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>🎨 Tema Seçimi</h2>")
        layout.addWidget(title)
        
        desc = QLabel("Uygulamanın görünümünü belirleyin. İstediğiniz zaman değiştirebilirsiniz.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Tema seçenekleri
        self.theme_group = QButtonGroup()
        themes_layout = QGridLayout()
        
        themes = [
            ("light", "🌞 Aydınlık", "Modern beyaz tasarım\nGündüz çalışma için ideal", "#ffffff"),
            ("dark", "🌙 Karanlık", "Göz dostu koyu tasarım\nGece çalışması için perfect", "#2b2b2b"),
            ("neon", "⚡ Neon", "Canlı renkli tasarım\nEnerjik ve modern görünüm", "#00ff88"),
            ("midnight", "🌃 Gece Yarısı", "Derin mavi tonlar\nProfesyonel ve sakin", "#1a237e"),
        ]
        
        for i, (theme_id, name, desc, color) in enumerate(themes):
            theme_frame = QFrame()
            theme_frame.setFixedSize(180, 120)
            theme_frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: {color};
                }}
                QFrame:hover {{
                    border-color: #2196F3;
                }}
            """)
            
            theme_layout = QVBoxLayout()
            
            radio = QRadioButton(name)
            radio.setProperty("theme_id", theme_id)
            self.theme_group.addButton(radio)
            
            if theme_id == "dark":  # Varsayılan seçim
                radio.setChecked(True)
            
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 11px; color: #666;")
            
            theme_layout.addWidget(radio)
            theme_layout.addWidget(desc_label)
            theme_layout.addStretch()
            
            theme_frame.setLayout(theme_layout)
            themes_layout.addWidget(theme_frame, i // 2, i % 2)
        
        layout.addLayout(themes_layout)
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_language_page(self) -> QFrame:
        """Dil seçimi sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>🌍 Dil Seçimi</h2>")
        layout.addWidget(title)
        
        desc = QLabel("Uygulamanın dilini seçin. Dinamik dil değiştirme desteklenir.")
        layout.addWidget(desc)
        
        # Dil seçenekleri
        lang_group = QGroupBox("Kullanılabilir Diller")
        lang_layout = QVBoxLayout()
        
        self.language_combo = QComboBox()
        languages = [
            ("tr", "🇹🇷 Türkçe", True),
            ("en", "🇺🇸 English", True),
            ("de", "🇩🇪 Deutsch", False),
            ("fr", "🇫🇷 Français", False),
            ("es", "🇪🇸 Español", False),
            ("it", "🇮🇹 Italiano", False),
            ("pt", "🇵🇹 Português", False),
            ("ru", "🇷🇺 Русский", False),
            ("zh", "🇨🇳 中文", False),
            ("ja", "🇯🇵 日本語", False),
        ]
        
        for lang_code, lang_name, available in languages:
            display_name = lang_name if available else f"{lang_name} (Yakında)"
            self.language_combo.addItem(display_name, lang_code)
            
            if not available:
                # Disable unavailable languages
                index = self.language_combo.count() - 1
                model = self.language_combo.model()
                item = model.item(index)
                item.setEnabled(False)
        
        self.language_combo.setCurrentIndex(0)  # Türkçe varsayılan
        lang_layout.addWidget(self.language_combo)
        
        # Dil paketi bilgisi
        info_label = QLabel("""
        <b>Not:</b> Dil paketleri otomatik olarak indirilir. İnternet bağlantısı gereklidir.
        <br>Dil değişiklikleri anında uygulanır ve yeniden başlatma gerektirmez.
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        lang_layout.addWidget(info_label)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_privacy_page(self) -> QFrame:
        """Güvenlik ve gizlilik ayarları sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>🔒 Gizlilik ve Güvenlik</h2>")
        layout.addWidget(title)
        
        desc = QLabel("Veri saklama ve güvenlik tercihlerinizi belirleyin.")
        layout.addWidget(desc)
        
        # Veri saklama ayarları
        data_group = QGroupBox("📊 Veri Saklama")
        data_layout = QVBoxLayout()
        
        self.save_cache_checkbox = QCheckBox("Önbellek dosyalarını kaydet (Daha hızlı açılış)")
        self.save_cache_checkbox.setChecked(False)
        data_layout.addWidget(self.save_cache_checkbox)
        
        self.save_logs_checkbox = QCheckBox("Log dosyalarını kaydet (Hata ayıklama için)")
        self.save_logs_checkbox.setChecked(True)
        data_layout.addWidget(self.save_logs_checkbox)
        
        self.auto_cleanup_checkbox = QCheckBox("Uygulama kapanışında geçici dosyaları temizle")
        self.auto_cleanup_checkbox.setChecked(True)
        data_layout.addWidget(self.auto_cleanup_checkbox)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Güvenlik ayarları
        security_group = QGroupBox("🛡️ Güvenlik")
        security_layout = QVBoxLayout()
        
        self.remember_passwords_checkbox = QCheckBox("PDF şifrelerini hatırla (Güvenli depolanır)")
        self.remember_passwords_checkbox.setChecked(False)
        security_layout.addWidget(self.remember_passwords_checkbox)
        
        self.secure_delete_checkbox = QCheckBox("Dosya silinirken güvenli silme kullan")
        self.secure_delete_checkbox.setChecked(True)
        security_layout.addWidget(self.secure_delete_checkbox)
        
        self.check_updates_checkbox = QCheckBox("Otomatik güncellemeleri kontrol et")
        self.check_updates_checkbox.setChecked(True)
        security_layout.addWidget(self.check_updates_checkbox)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Gizlilik bilgisi
        privacy_info = QLabel("""
        <b>🔐 Gizlilik Taahhüdü:</b>
        <br>• Dosyalarınız sadece cihazınızda işlenir
        <br>• Hiçbir veri sunucularımıza gönderilmez
        <br>• İnternet bağlantısı sadece güncellemeler için kullanılır
        <br>• Kullanım istatistikleri anonim olarak toplanabilir (isteğe bağlı)
        """)
        privacy_info.setWordWrap(True)
        privacy_info.setStyleSheet("""
            background-color: #e8f5e8; 
            border: 1px solid #4caf50; 
            border-radius: 4px; 
            padding: 10px; 
            color: #2e7d32;
        """)
        layout.addWidget(privacy_info)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_ocr_page(self) -> QFrame:
        """OCR ayarları sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>🔍 OCR Ayarları</h2>")
        layout.addWidget(title)
        
        desc = QLabel("Optik Karakter Tanıma (OCR) dil paketlerini seçin.")
        layout.addWidget(desc)
        
        # OCR motor seçimi
        engine_group = QGroupBox("🔧 OCR Motoru")
        engine_layout = QVBoxLayout()
        
        self.ocr_engine_combo = QComboBox()
        engines = [
            ("tesseract", "Tesseract (Varsayılan)", "En yaygın OCR motoru"),
            ("easyocr", "EasyOCR (Daha doğru)", "AI tabanlı, daha yavaş"),
            ("paddleocr", "PaddleOCR (Çince için)", "Çince karakterler için optimize"),
        ]
        
        for engine_id, name, desc in engines:
            self.ocr_engine_combo.addItem(f"{name} - {desc}", engine_id)
        
        engine_layout.addWidget(self.ocr_engine_combo)
        engine_group.setLayout(engine_layout)
        layout.addWidget(engine_group)
        
        # Dil paketi seçimi
        lang_group = QGroupBox("📚 OCR Dil Paketleri")
        lang_layout = QVBoxLayout()
        
        # Popüler diller
        popular_label = QLabel("<b>Popüler Diller:</b>")
        lang_layout.addWidget(popular_label)
        
        self.ocr_languages = {}
        popular_langs = [
            ("tur", "🇹🇷 Türkçe", True),
            ("eng", "🇺🇸 English", True),
            ("deu", "🇩🇪 Deutsch", False),
            ("fra", "🇫🇷 Français", False),
            ("spa", "🇪🇸 Español", False),
            ("ita", "🇮🇹 Italiano", False),
        ]
        
        for lang_code, lang_name, default_checked in popular_langs:
            checkbox = QCheckBox(lang_name)
            checkbox.setChecked(default_checked)
            self.ocr_languages[lang_code] = checkbox
            lang_layout.addWidget(checkbox)
        
        # Daha fazla dil butonu
        more_langs_button = QPushButton("+ Daha Fazla Dil...")
        more_langs_button.clicked.connect(self._show_more_languages)
        lang_layout.addWidget(more_langs_button)
        
        # OCR ayarları
        ocr_settings_layout = QHBoxLayout()
        
        # Görüntü ön işleme
        preprocessing_checkbox = QCheckBox("Görüntü ön işleme (Kaliteyi artırır)")
        preprocessing_checkbox.setChecked(True)
        self.preprocessing_enabled = preprocessing_checkbox
        lang_layout.addWidget(preprocessing_checkbox)
        
        # Otomatik dil algılama
        auto_detect_checkbox = QCheckBox("Otomatik dil algılama")
        auto_detect_checkbox.setChecked(True)
        self.auto_detect_language = auto_detect_checkbox
        lang_layout.addWidget(auto_detect_checkbox)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # İndirme bilgisi
        download_info = QLabel("""
        <b>ℹ️ Not:</b> Seçilen dil paketleri kurulum sırasında otomatik olarak indirilir.
        İndirme boyutu yaklaşık 1-5 MB per dil paketi.
        """)
        download_info.setWordWrap(True)
        download_info.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(download_info)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_permissions_page(self) -> QFrame:
        """Klasör izinleri sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>📁 Klasör İzinleri</h2>")
        layout.addWidget(title)
        
        desc = QLabel("PyPDF-Tools'un erişebileceği klasörleri belirleyin.")
        layout.addWidget(desc)
        
        # İzin türleri
        permission_group = QGroupBox("🔓 İzin Türleri")
        permission_layout = QVBoxLayout()
        
        self.full_access_radio = QRadioButton("Tam erişim (Tüm klasörler)")
        self.full_access_radio.setChecked(True)
        permission_layout.addWidget(self.full_access_radio)
        
        self.limited_access_radio = QRadioButton("Sınırlı erişim (Belirli klasörler)")
        permission_layout.addWidget(self.limited_access_radio)
        
        self.sandbox_access_radio = QRadioButton("Sandbox modu (Sadece uygulama klasörü)")
        permission_layout.addWidget(self.sandbox_access_radio)
        
        permission_group.setLayout(permission_layout)
        layout.addWidget(permission_group)
        
        # Klasör listesi (sınırlı erişim için)
        self.folders_group = QGroupBox("📂 İzin Verilen Klasörler")
        folders_layout = QVBoxLayout()
        
        # Varsayılan klasörler
        default_folders = [
            str(Path.home() / "Desktop"),
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
        ]
        
        self.folder_list = QListWidget()
        for folder in default_folders:
            self.folder_list.addItem(folder)
        
        folders_layout.addWidget(self.folder_list)
        
        # Klasör ekleme/çıkarma butonları
        folder_buttons = QHBoxLayout()
        
        add_folder_btn = QPushButton("+ Klasör Ekle")
        add_folder_btn.clicked.connect(self._add_folder)
        folder_buttons.addWidget(add_folder_btn)
        
        remove_folder_btn = QPushButton("- Klasör Çıkar")
        remove_folder_btn.clicked.connect(self._remove_folder)
        folder_buttons.addWidget(remove_folder_btn)
        
        folders_layout.addLayout(folder_buttons)
        self.folders_group.setLayout(folders_layout)
        self.folders_group.setEnabled(False)
        layout.addWidget(self.folders_group)
        
        # İzin değişikliği bağlantıları
        self.full_access_radio.toggled.connect(lambda: self.folders_group.setEnabled(False))
        self.limited_access_radio.toggled.connect(lambda: self.folders_group.setEnabled(True))
        self.sandbox_access_radio.toggled.connect(lambda: self.folders_group.setEnabled(False))
        
        # Güvenlik uyarısı
        security_warning = QLabel("""
        <b>⚠️ Güvenlik Notu:</b>
        <br>• Tam erişim: Uygulamanın tüm dosyalarınıza erişimi olur
        <br>• Sınırlı erişim: Sadece belirlediğiniz klasörlere erişim
        <br>• Sandbox: En güvenli, sadece geçici işlem klasörü
        """)
        security_warning.setWordWrap(True)
        security_warning.setStyleSheet("""
            background-color: #fff3cd; 
            border: 1px solid #ffc107; 
            border-radius: 4px; 
            padding: 10px; 
            color: #856404;
        """)
        layout.addWidget(security_warning)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_summary_page(self) -> QFrame:
        """Ayarlar özeti sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>📋 Ayarlar Özeti</h2>")
        layout.addWidget(title)
        
        desc = QLabel("Seçtiğiniz ayarları kontrol edin. 'Geri' butonuyla değişiklik yapabilirsiniz.")
        layout.addWidget(desc)
        
        # Özet alanı
        self.summary_area = QScrollArea()
        self.summary_content = QLabel()
        self.summary_content.setWordWrap(True)
        self.summary_content.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Consolas', monospace;
        """)
        
        self.summary_area.setWidget(self.summary_content)
        self.summary_area.setWidgetResizable(True)
        layout.addWidget(self.summary_area)
        
        # Kurulum başlat butonu
        install_layout = QHBoxLayout()
        install_layout.addStretch()
        
        self.start_setup_btn = QPushButton("🚀 Kurulumu Başlat")
        self.start_setup_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.start_setup_btn.clicked.connect(self._start_installation)
        
        install_layout.addWidget(self.start_setup_btn)
        layout.addLayout(install_layout)
        
        page.setLayout(layout)
        return page
    
    def _create_installation_page(self) -> QFrame:
        """Kurulum sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("<h2>⚙️ Kurulum Yapılıyor</h2>")
        layout.addWidget(title)
        
        # Progress bar
        self.install_progress = QProgressBar()
        self.install_progress.setRange(0, 100)
        self.install_progress.setValue(0)
        layout.addWidget(self.install_progress)
        
        # Status label
        self.install_status = QLabel("Kurulum başlatılıyor...")
        self.install_status.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.install_status)
        
        # Log area
        self.install_log = QTextEdit()
        self.install_log.setReadOnly(True)
        self.install_log.setMaximumHeight(200)
        self.install_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.install_log)
        
        # Cancel button
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        
        self.cancel_install_btn = QPushButton("Kurulumu İptal Et")
        self.cancel_install_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.cancel_install_btn.clicked.connect(self._cancel_installation)
        
        cancel_layout.addWidget(self.cancel_install_btn)
        layout.addLayout(cancel_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def _create_completion_page(self) -> QFrame:
        """Tamamlanma sayfası"""
        page = QFrame()
        layout = QVBoxLayout()
        
        # Başarı ikonu ve mesajı
        success_layout = QVBoxLayout()
        success_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        success_icon = QLabel("🎉")
        success_icon.setStyleSheet("font-size: 72px;")
        success_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_layout.addWidget(success_icon)
        
        success_title = QLabel("<h1>Kurulum Tamamlandı!</h1>")
        success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_title.setStyleSheet("color: #28a745; margin: 20px;")
        success_layout.addWidget(success_title)
        
        success_desc = QLabel("""
        PyPDF-Tools v2.0 başarıyla yapılandırıldı ve kullanıma hazır!
        <br><br>
        Artık modern PDF işleme özelliklerinin keyfini çıkarabilirsiniz.
        """)
        success_desc.setWordWrap(True)
        success_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_desc.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
        success_layout.addWidget(success_desc)
        
        layout.addLayout(success_layout)
        
        # Hızlı başlangıç
        quick_start_group = QGroupBox("🚀 Hızlı Başlangıç")
        quick_layout = QVBoxLayout()
        
        tips = [
            "💡 Dosyaları doğrudan uygulamaya sürükleyip bırakabilirsiniz",
            "⌨️ Klavye kısayolları: Ctrl+O (Aç), Ctrl+S (Kaydet), F1 (Yardım)",
            "🎨 Temalar: Ayarlar > Görünüm menüsünden tema değiştirebilirsiniz",
            "📚 Yardım: F1 tuşu ile detaylı kullanım kılavuzuna erişebilirsiniz",
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet("padding: 5px; font-size: 14px;")
            quick_layout.addWidget(tip_label)
        
        quick_start_group.setLayout(quick_layout)
        layout.addWidget(quick_start_group)
        
        # Final buttons
        final_layout = QHBoxLayout()
        final_layout.addStretch()
        
        self.open_app_btn = QPushButton("📱 Uygulamayı Aç")
        self.open_app_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.open_app_btn.clicked.connect(self._open_application)
        
        self.close_wizard_btn = QPushButton("❌ Sihirbazı Kapat")
        self.close_wizard_btn.clicked.connect(self.accept)
        
        final_layout.addWidget(self.open_app_btn)
        final_layout.addWidget(self.close_wizard_btn)
        layout.addLayout(final_layout)
        
        page.setLayout(layout)
        return page
    
    def _setup_animations(self):
        """Animasyonları kurulumla"""
        # Sayfa geçiş animasyonu
        self.page_animation = QPropertyAnimation(self.content_stack, b"currentIndex")
        self.page_animation.setDuration(300)
        self.page_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _setup_connections(self):
        """Sinyal bağlantılarını kur"""
        pass
    
    def _apply_wizard_theme(self):
        """Sihirbaz temasını uygula"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QCheckBox, QRadioButton {
                spacing: 8px;
                color: #333333;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """)
    
    def _show_welcome_page(self):
        """Hoşgeldin sayfasını göster"""
        self.content_stack.setCurrentIndex(0)
        self.current_page = 0
        self._update_buttons()
    
    def _go_next(self):
        """Sonraki sayfaya git"""
        if self.current_page < self.content_stack.count() - 1:
            if self.current_page == 6:  # Summary sayfası
                self._update_summary()
            
            self.current_page += 1
            self.content_stack.setCurrentIndex(self.current_page)
            self._update_buttons()
    
    def _go_back(self):
        """Önceki sayfaya git"""
        if self.current_page > 0:
            self.current_page -= 1
            self.content_stack.setCurrentIndex(self.current_page)
            self._update_buttons()
    
    def _update_buttons(self):
        """Butonları güncelle"""
        self.back_button.setEnabled(self.current_page > 0)
        
        if self.current_page == self.content_stack.count() - 1:
            self.next_button.setText("Bitir")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.accept)
        elif self.current_page == 6:  # Summary sayfası
            self.next_button.setText("Kuruluma Geç")
        else:
            self.next_button.setText("İleri »")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self._go_next)
    
    def _update_summary(self):
        """Ayarlar özetini güncelle"""
        # Seçilen ayarları topla
        self.setup_data = self._collect_settings()
        
        # Özet metni oluştur
        summary_text = self._generate_summary_text()
        self.summary_content.setText(summary_text)
    
    def _collect_settings(self) -> Dict[str, Any]:
        """Tüm ayarları topla"""
        settings = {}
        
        # Tema
        for button in self.theme_group.buttons():
            if button.isChecked():
                settings['theme'] = button.property('theme_id')
                break
        
        # Dil
        current_lang = self.language_combo.currentData()
        settings['language'] = current_lang
        
        # Gizlilik
        settings['privacy'] = {
            'save_cache': self.save_cache_checkbox.isChecked(),
            'save_logs': self.save_logs_checkbox.isChecked(),
            'auto_cleanup': self.auto_cleanup_checkbox.isChecked(),
            'remember_passwords': self.remember_passwords_checkbox.isChecked(),
            'secure_delete': self.secure_delete_checkbox.isChecked(),
            'check_updates': self.check_updates_checkbox.isChecked(),
        }
        
        # OCR
        selected_ocr_langs = []
        for lang_code, checkbox in self.ocr_languages.items():
            if checkbox.isChecked():
                selected_ocr_langs.append(lang_code)
        
        settings['ocr'] = {
            'engine': self.ocr_engine_combo.currentData(),
            'languages': selected_ocr_langs,
            'preprocessing': self.preprocessing_enabled.isChecked(),
            'auto_detect': self.auto_detect_language.isChecked(),
        }
        
        # Klasör izinleri
        if self.full_access_radio.isChecked():
            permission_type = 'full'
        elif self.limited_access_radio.isChecked():
            permission_type = 'limited'
        else:
            permission_type = 'sandbox'
        
        allowed_dirs = []
        for i in range(self.folder_list.count()):
            allowed_dirs.append(self.folder_list.item(i).text())
        
        settings['permissions'] = {
            'type': permission_type,
            'allowed_directories': allowed_dirs,
        }
        
        return settings
    
    def _generate_summary_text(self) -> str:
        """Özet metnini oluştur"""
        data = self.setup_data
        
        # Tema adını çevir
        theme_names = {
            'light': '🌞 Aydınlık',
            'dark': '🌙 Karanlık', 
            'neon': '⚡ Neon',
            'midnight': '🌃 Gece Yarısı'
        }
        
        # Dil adını çevir
        lang_names = {
            'tr': '🇹🇷 Türkçe',
            'en': '🇺🇸 English'
        }
        
        # İzin türünü çevir
        permission_names = {
            'full': 'Tam Erişim',
            'limited': 'Sınırlı Erişim',
            'sandbox': 'Sandbox Modu'
        }
        
        summary = f"""
<h3>🎨 Görünüm Ayarları</h3>
<b>Tema:</b> {theme_names.get(data.get('theme', 'dark'), 'Bilinmiyor')}<br>
<b>Dil:</b> {lang_names.get(data.get('language', 'tr'), 'Bilinmiyor')}<br>

<h3>🔒 Gizlilik Ayarları</h3>
<b>Önbellek kaydet:</b> {'Evet' if data['privacy']['save_cache'] else 'Hayır'}<br>
<b>Log kaydet:</b> {'Evet' if data['privacy']['save_logs'] else 'Hayır'}<br>
<b>Otomatik temizlik:</b> {'Evet' if data['privacy']['auto_cleanup'] else 'Hayır'}<br>
<b>Şifreleri hatırla:</b> {'Evet' if data['privacy']['remember_passwords'] else 'Hayır'}<br>
<b>Güvenli silme:</b> {'Evet' if data['privacy']['secure_delete'] else 'Hayır'}<br>
<b>Güncelleme kontrolü:</b> {'Evet' if data['privacy']['check_updates'] else 'Hayır'}<br>

<h3>🔍 OCR Ayarları</h3>
<b>Motor:</b> {data['ocr']['engine']}<br>
<b>Dil sayısı:</b> {len(data['ocr']['languages'])} dil<br>
<b>Seçilen diller:</b> {', '.join(data['ocr']['languages'])}<br>
<b>Görüntü ön işleme:</b> {'Evet' if data['ocr']['preprocessing'] else 'Hayır'}<br>
<b>Otomatik dil algılama:</b> {'Evet' if data['ocr']['auto_detect'] else 'Hayır'}<br>

<h3>📁 Dosya İzinleri</h3>
<b>İzin türü:</b> {permission_names.get(data['permissions']['type'], 'Bilinmiyor')}<br>
<b>İzinli klasör sayısı:</b> {len(data['permissions']['allowed_directories'])}<br>
        """
        
        return summary
    
    def _start_installation(self):
        """Kurulumu başlat"""
        self.current_page = 7  # Installation sayfası
        self.content_stack.setCurrentIndex(7)
        self._update_buttons()
