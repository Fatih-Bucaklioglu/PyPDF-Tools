#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2.0
Modern PDF işleme uygulaması - DÜZELTILMIŞ VERSIYON
Fatih Bucaklıoğlu tarafından geliştirilmiştir.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time

# GUI kütüphaneleri - güvenli import
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"GUI kütüphaneleri bulunamadı: {e}")
    print("Lütfen tkinter kurulumunu kontrol edin:")
    print("  Ubuntu/Debian: sudo apt-get install python3-tk")
    print("  macOS: brew install python-tk")
    print("  Windows: Python kurulumu ile birlikte gelir")
    GUI_AVAILABLE = False

# Proje modülleri - güvenli import
try:
    from utils import ConfigManager, CacheManager, LogManager, ThemeManager
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"Utils modülleri import edilemedi: {e}")
    UTILS_AVAILABLE = False
    # Fallback sınıflar
    class ConfigManager:
        def __init__(self): self.config = {}
        def get(self, key, default=None): return default
        def set(self, key, value): pass
        def save(self): pass
    
    class CacheManager:
        def __init__(self, enabled=False): self.enabled = enabled
        def clear_all(self): pass
    
    class LogManager:
        def __init__(self, enabled=False): self.enabled = enabled
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
        def set_level(self, level): pass
    
    class ThemeManager:
        def __init__(self): self.current_theme = 'light'
        def apply_theme(self, theme, widget): pass

# UI bileşenleri - güvenli import
UI_COMPONENTS_AVAILABLE = False
if GUI_AVAILABLE:
    try:
        from ui.header import ModernHeader
        from ui.sidebar import ModernSidebar
        from ui.content import ModernContent
        UI_COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"UI bileşenleri import edilemedi: {e}")
        print("Fallback UI kullanılacak...")

# İşlem modülleri - güvenli import  
PROCESSORS_AVAILABLE = False
try:
    from resources.pdf_utils import PDFProcessor
    from ocr_module import OCRProcessor
    PROCESSORS_AVAILABLE = True
except ImportError as e:
    print(f"İşlem modülleri import edilemedi: {e}")
    print("Bazı özellikler kullanılamayabilir...")

# Sürüm bilgisi
__version__ = "2.0.0"
__author__ = "Fatih Bucaklıoğlu"
__description__ = "Modern PDF İşleme Uygulaması"

class PyPDFToolsV2:
    """
    PyPDF-Stirling Tools v2 Ana Uygulama Sınıfı - DÜZELTILMIŞ
    """
    
    def __init__(self):
        """Ana uygulamayı başlat"""
        self.root = None
        self.config_manager = None
        self.cache_manager = None
        self.log_manager = None
        self.theme_manager = None
        self.pdf_processor = None
        self.ocr_processor = None
        
        # UI bileşenleri
        self.header = None
        self.sidebar = None
        self.content = None
        
        # Uygulama durumu
        self.current_files = []
        self.current_operation = None
        self.is_processing = False
        
        # Başlatma durumu
        self.initialization_successful = False
    
    def check_dependencies(self):
        """Bağımlılıkları kontrol et"""
        missing_deps = []
        warnings = []
        
        if not GUI_AVAILABLE:
            missing_deps.append("tkinter (GUI için gerekli)")
        
        if not UTILS_AVAILABLE:
            warnings.append("Utils modülleri (bazı özellikler sınırlı)")
        
        if not UI_COMPONENTS_AVAILABLE:
            warnings.append("UI bileşenleri (basit arayüz kullanılacak)")
        
        if not PROCESSORS_AVAILABLE:
            warnings.append("İşlem modülleri (PDF işleme sınırlı)")
        
        # PDF işleme bağımlılıkları
        pdf_deps = []
        try:
            import PyPDF2
        except ImportError:
            pdf_deps.append("PyPDF2")
        
        try:
            import fitz
        except ImportError:
            pdf_deps.append("PyMuPDF")
        
        try:
            from PIL import Image
        except ImportError:
            pdf_deps.append("Pillow")
        
        if pdf_deps:
            warnings.append(f"PDF kütüphaneleri: {', '.join(pdf_deps)}")
        
        # OCR bağımlılıkları
        ocr_deps = []
        try:
            import pytesseract
        except ImportError:
            ocr_deps.append("pytesseract")
        
        try:
            import cv2
        except ImportError:
            ocr_deps.append("opencv-python")
        
        if ocr_deps:
            warnings.append(f"OCR kütüphaneleri: {', '.join(ocr_deps)}")
        
        # Sonuçları göster
        if missing_deps:
            print("❌ EKSİK BAĞIMLILIKLAR:")
            for dep in missing_deps:
                print(f"   - {dep}")
            print("\nKurulum için: pip install -r requirements.txt")
            return False
        
        if warnings:
            print("⚠️  UYARILAR:")
            for warning in warnings:
                print(f"   - {warning}")
        
        print("✅ Temel bağımlılıklar mevcut")
        return True
    
    def initialize_application(self):
        """Uygulamayı başlat ve tüm bileşenleri hazırla"""
        try:
            print("🚀 PyPDF-Stirling Tools v2 başlatılıyor...")
            
            # Bağımlılık kontrolü
            if not self.check_dependencies():
                print("❌ Kritik bağımlılıklar eksik, çıkılıyor...")
                return False
            
            # Yönetici sınıfları
            self.config_manager = ConfigManager()
            self.log_manager = LogManager(
                enabled=self.config_manager.get('privacy.save_logs', False)
            )
            self.cache_manager = CacheManager(
                enabled=self.config_manager.get('privacy.save_cache', False)
            )
            self.theme_manager = ThemeManager()
            
            self.log_manager.info("PyPDF Tools v2 başlatılıyor...")
            
            # GUI kontrolü
            if not GUI_AVAILABLE:
                self.log_manager.error("GUI mevcut değil, konsol modu")
                return self.run_console_mode()
            
            # Ana pencereyi oluştur
            self.create_main_window()
            
            # İşleme motorları
            if PROCESSORS_AVAILABLE:
                self.initialize_processors()
            
            # UI bileşenleri
            if UI_COMPONENTS_AVAILABLE:
                self.create_modern_ui()
            else:
                self.create_fallback_ui()
            
            # Sistem entegrasyonu
            self.setup_system_integration()
            
            # İlk çalıştırma
            self.check_first_run()
            
            self.initialization_successful = True
            self.log_manager.info("Uygulama başarıyla başlatıldı")
            return True
            
        except Exception as e:
            error_msg = f"Uygulama başlatılamadı: {e}"
            print(f"❌ {error_msg}")
            if self.log_manager:
                self.log_manager.error(error_msg)
            return False
    
    def create_main_window(self):
        """Ana pencereyi oluştur"""
        try:
            self.root = tk.Tk()
            self.root.title(f"PyPDF-Stirling Tools v{__version__}")
            self.root.withdraw()  # İlk başta gizle
            
            # Pencere boyutları
            window_width = self.config_manager.get('appearance.window_size.width', 1200)
            window_height = self.config_manager.get('appearance.window_size.height', 800)
            
            # Ekran ortasında konumlandır
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            self.root.minsize(800, 600)
            
            # Tema uygula
            current_theme = self.config_manager.get('appearance.theme', 'light')
            self.theme_manager.apply_theme(current_theme, self.root)
            
            # Pencere kapatma olayı
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            raise Exception(f"Ana pencere oluşturulamadı: {e}")
    
    def initialize_processors(self):
        """İşleme motorlarını başlat"""
        try:
            # PDF işlemci
            self.pdf_processor = PDFProcessor(
                cache_manager=self.cache_manager,
                log_manager=self.log_manager
            )
            
            # OCR işlemci
            self.ocr_processor = OCRProcessor(
                languages=['eng', 'tur'],
                cache_enabled=self.cache_manager.enabled,
                log_manager=self.log_manager
            )
            
            self.log_manager.info("İşleme motorları başlatıldı")
            
        except Exception as e:
            self.log_manager.warning(f"İşleme motorları başlatılamadı: {e}")
            # Fallback işlemciler oluştur
            self.pdf_processor = None
            self.ocr_processor = None
    
    def create_modern_ui(self):
        """Modern UI bileşenlerini oluştur"""
        try:
            # Header
            self.header = ModernHeader(
                parent=self.root,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                app_instance=self
            )
            
            # Ana çerçeve
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Sidebar
            self.sidebar = ModernSidebar(
                parent=main_frame,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                app_instance=self
            )
            
            # Content
            self.content = ModernContent(
                parent=main_frame,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                pdf_processor=self.pdf_processor,
                ocr_processor=self.ocr_processor,
                app_instance=self
            )
            
            # Layout
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            self.log_manager.info("Modern UI oluşturuldu")
            
        except Exception as e:
            self.log_manager.error(f"Modern UI oluşturulamadı: {e}")
            self.create_fallback_ui()
    
    def create_fallback_ui(self):
        """Basit fallback UI oluştur"""
        try:
            # Basit menü
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Dosya", menu=file_menu)
            file_menu.add_command(label="Aç", command=self.open_files_simple)
            file_menu.add_command(label="Çıkış", command=self.on_closing)
            
            # Ana frame
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Basit arayüz
            ttk.Label(main_frame, text="PyPDF-Stirling Tools v2", 
                     font=('Arial', 16, 'bold')).pack(pady=10)
            
            ttk.Label(main_frame, 
                     text="Basit mod - Bazı bağımlılıklar eksik olduğu için sınırlı özellikler").pack()
            
            # Dosya seçme
            self.file_frame = ttk.Frame(main_frame)
            self.file_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(self.file_frame, text="PDF Dosyası Seç", 
                      command=self.open_files_simple).pack()
            
            self.file_label = ttk.Label(self.file_frame, text="Dosya seçilmedi")
            self.file_label.pack(pady=5)
            
            self.log_manager.info("Fallback UI oluşturuldu")
            
        except Exception as e:
            raise Exception(f"Fallback UI oluşturulamadı: {e}")
    
    def open_files_simple(self):
        """Basit dosya açma"""
        try:
            files = filedialog.askopenfilenames(
                title="PDF Dosyaları Seçin",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if files:
                self.current_files = list(files)
                self.file_label.config(text=f"{len(files)} dosya seçildi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya seçilemedi: {e}")
    
    def setup_system_integration(self):
        """Sistem entegrasyonu - güvenli"""
        try:
            # Basit entegrasyon
            pass
        except Exception as e:
            self.log_manager.warning(f"Sistem entegrasyonu başarısız: {e}")
    
    def check_first_run(self):
        """İlk çalıştırma kontrolü - güvenli"""
        try:
            is_first_run = self.config_manager.get('app.first_run', True)
            if is_first_run:
                self.config_manager.set('app.first_run', False)
                self.config_manager.save()
                
                # Karşılama mesajı
                if GUI_AVAILABLE:
                    messagebox.showinfo("Hoş Geldiniz", 
                                      f"{__description__}\n\nSürüm: {__version__}")
        except Exception as e:
            self.log_manager.warning(f"İlk çalıştırma kontrolü başarısız: {e}")
    
    def run_console_mode(self):
        """Konsol modu çalıştır"""
        print("\n🔧 PyPDF-Stirling Tools v2 - Konsol Modu")
        print("=" * 50)
        print("GUI bağımlılıkları eksik olduğu için konsol modunda çalışıyor")
        print("\nTemel komutlar:")
        print("  help - Yardım")
        print("  exit - Çıkış")
        
        while True:
            try:
                command = input("\nPyPDF> ").strip().lower()
                
                if command == 'exit':
                    break
                elif command == 'help':
                    self.show_console_help()
                elif command == '':
                    continue
                else:
                    print("Bilinmeyen komut. 'help' yazarak yardım alabilirsiniz.")
                    
            except KeyboardInterrupt:
                print("\n\nÇıkılıyor...")
                break
            except Exception as e:
                print(f"Hata: {e}")
        
        return True
    
    def show_console_help(self):
        """Konsol yardımı"""
        print("\n📚 PyPDF-Stirling Tools v2 Yardım")
        print("-" * 30)
        print("Bu sürüm GUI bağımlılıkları eksik olduğu için")
        print("sınırlı konsol modunda çalışmaktadır.")
        print("\nTam özellikler için şu adımları takip edin:")
        print("  1. pip install -r requirements.txt")
        print("  2. Sistem bağımlılıklarını kurun (Tesseract OCR vb.)")
        print("  3. Uygulamayı yeniden başlatın")
    
    def run(self):
        """Uygulamayı çalıştır"""
        if not self.initialization_successful:
            print("❌ Uygulama başlatılamadı")
            return False
        
        if not GUI_AVAILABLE:
            return True  # Console mode zaten çalıştırıldı
        
        try:
            # Pencereyi göster
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # Ana döngü
            self.root.mainloop()
            return True
            
        except KeyboardInterrupt:
            self.log_manager.info("Uygulama kullanıcı tarafından durduruldu")
            return True
        except Exception as e:
            error_msg = f"Uygulama çalışırken hata: {e}"
            print(f"❌ {error_msg}")
            if self.log_manager:
                self.log_manager.error(error_msg)
            return False
    
    def on_closing(self):
        """Pencere kapatma - güvenli"""
        try:
            # Ayarları kaydet
            if self.config_manager:
                if self.root:
                    try:
                        geometry = self.root.geometry()
                        width, height, x, y = map(int, geometry.replace('x', '+').split('+'))
                        self.config_manager.set('appearance.window_size.width', width)
                        self.config_manager.set('appearance.window_size.height', height)
                    except:
                        pass
                
                self.config_manager.save()
            
            # Cache temizle
            if self.cache_manager and not self.cache_manager.enabled:
                self.cache_manager.clear_all()
            
            # Log
            if self.log_manager:
                self.log_manager.info("Uygulama kapatılıyor")
            
            # Pencereyi kapat
            if self.root:
                self.root.quit()
                self.root.destroy()
            
        except Exception as e:
            print(f"⚠️ Kapanış hatası: {e}")
        finally:
            sys.exit(0)
    
    # Public Methods - güvenli wrapper'lar
    def show_settings(self):
        """Ayarlar penceresini göster - DÜZELTİLMİŞ"""
        try:
            from ui.settings_dialog import SettingsDialog
            settings = SettingsDialog(
                parent=self.root,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager
            )
            settings.show()
        except ImportError as e:
            # Fallback - basit ayarlar
            if GUI_AVAILABLE:
                settings_text = f"""
PyPDF-Stirling Tools v2 Ayarları

Tema: {self.config_manager.get('appearance.theme', 'light')}
Dil: {self.config_manager.get('appearance.language', 'tr')}
Cache: {'Açık' if self.config_manager.get('privacy.save_cache', False) else 'Kapalı'}

Detaylı ayarlar için ui.settings_dialog modülünü kurun.
                """
                messagebox.showinfo("Ayarlar", settings_text.strip())
        except Exception as e:
            if GUI_AVAILABLE:
                messagebox.showerror("Hata", f"Ayarlar penceresi açılamadı: {e}")

    
    def show_help(self):
        """Yardım - güvenli"""
        if GUI_AVAILABLE:
            help_text = f"{__description__}\nSürüm: {__version__}\nGeliştirici: {__author__}"
            messagebox.showinfo("Yardım", help_text)

def main():
    """Ana fonksiyon - DÜZELTİLMİŞ"""
    try:
        print(f"🚀 {__description__} v{__version__}")
        print("-" * 50)
        
        # Komut satırı argümanları
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test':
                print("Test modu - bağımlılık kontrolü")
                app = PyPDFToolsV2()
                return 0 if app.check_dependencies() else 1
            elif sys.argv[1] == '--console':
                print("Konsol modu zorla")
                global GUI_AVAILABLE
                GUI_AVAILABLE = False
        
        # Uygulama başlat
        app = PyPDFToolsV2()
        
        if app.initialize_application():
            app.run()
            return 0
        else:
            print("❌ Başlatma başarısız")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Güle güle!")
        return 0
    except Exception as e:
        print(f"❌ Kritik hata: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)