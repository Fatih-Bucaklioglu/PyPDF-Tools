#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Settings Dialog
Kapsamlı ayarlar penceresi
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import threading

class SettingsDialog:
    """
    Modern ayarlar penceresi
    Kategorize edilmiş ayarlar ile kullanıcı dostu arayüz
    """
    
    def __init__(self, parent, config_manager, theme_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        
        self.dialog = None
        self.notebook = None
        
        # Ayar değişkenleri
        self.settings_vars = {}
        
        # Değişiklik takibi
        self.has_changes = False
        self.change_callbacks = []
    
    def show(self):
        """Ayarlar penceresini göster"""
        if self.dialog is not None:
            self.dialog.lift()
            self.dialog.focus()
            return
        
        self.create_dialog()
        self.create_categories()
        self.load_current_settings()
        
        # Pencereyi merkeze konumlandır
        self.center_dialog()
        
        # Pencereyi göster
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus()
    
    def create_dialog(self):
        """Ana dialog penceresini oluştur"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Ayarlar - PyPDF-Stirling Tools v2")
        self.dialog.geometry("800x600")
        self.dialog.minsize(700, 500)
        self.dialog.resizable(True, True)
        
        # Pencere kapatma olayı
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Ana frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık
        title_label = ttk.Label(
            main_frame,
            text="Ayarlar",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Alt butonlar
        self.create_bottom_buttons(main_frame)
    
    def create_bottom_buttons(self, parent):
        """Alt kısım butonları"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Sol taraf - Reset butonu
        reset_btn = ttk.Button(
            button_frame,
            text="🔄 Varsayılanlara Sıfırla",
            command=self.reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Sağ taraf - Ana butonlar
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # İptal
        cancel_btn = ttk.Button(
            right_frame,
            text="❌ İptal",
            command=self.on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Uygula
        apply_btn = ttk.Button(
            right_frame,
            text="✅ Uygula",
            command=self.apply_settings
        )
        apply_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Tamam
        ok_btn = ttk.Button(
            right_frame,
            text="💾 Tamam",
            command=self.on_ok
        )
        ok_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_categories(self):
        """Ayar kategorilerini oluştur"""
        categories = [
            ("Görünüm", self.create_appearance_tab),
            ("Gizlilik", self.create_privacy_tab),
            ("PDF İşleme", self.create_pdf_tab),
            ("OCR", self.create_ocr_tab),
            ("Sistem", self.create_system_tab),
            ("Gelişmiş", self.create_advanced_tab)
        ]
        
        for title, creator_func in categories:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=title)
            creator_func(frame)
    
    def create_appearance_tab(self, parent):
        """Görünüm ayarları sekmesi"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tema seçimi
        theme_group = ttk.LabelFrame(scrollable_frame, text="🎨 Tema", padding=10)
        theme_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['verbose_logging'] = tk.BooleanVar()
        ttk.Checkbutton(
            debug_group,
            text="Detaylı loglama",
            variable=self.settings_vars['verbose_logging']
        ).pack(anchor='w', pady=2)
        
        # Log dosyaları
        log_buttons = ttk.Frame(debug_group)
        log_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            log_buttons,
            text="📄 Log Dosyalarını Aç",
            command=self.open_log_folder
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            log_buttons,
            text="🗑️ Logları Temizle",
            command=self.clear_logs
        ).pack(side=tk.LEFT, padx=5)
        
        # Deneysel özellikler
        experimental_group = ttk.LabelFrame(scrollable_frame, text="🧪 Deneysel Özellikler", padding=10)
        experimental_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            experimental_group,
            text="⚠️ Bu özellikler kararsız olabilir!",
            font=('Arial', 9, 'bold'),
            foreground='orange'
        ).pack(anchor='w', pady=(0, 5))
        
        self.settings_vars['experimental_gpu'] = tk.BooleanVar()
        ttk.Checkbutton(
            experimental_group,
            text="GPU hızlandırma (CUDA desteği gerekli)",
            variable=self.settings_vars['experimental_gpu']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['experimental_ai_features'] = tk.BooleanVar()
        ttk.Checkbutton(
            experimental_group,
            text="AI destekli özellikler",
            variable=self.settings_vars['experimental_ai_features']
        ).pack(anchor='w', pady=2)
        
        # Konfigürasyon yönetimi
        config_group = ttk.LabelFrame(scrollable_frame, text="⚙️ Konfigürasyon", padding=10)
        config_group.pack(fill=tk.X, padx=10, pady=5)
        
        config_buttons = ttk.Frame(config_group)
        config_buttons.pack(fill=tk.X)
        
        ttk.Button(
            config_buttons,
            text="📤 Ayarları Dışa Aktar",
            command=self.export_config
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            config_buttons,
            text="📥 Ayarları İçe Aktar",
            command=self.import_config
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            config_buttons,
            text="📁 Config Klasörünü Aç",
            command=self.open_config_folder
        ).pack(side=tk.LEFT, padx=5)
    
    def load_current_settings(self):
        """Mevcut ayarları yükle"""
        try:
            # Görünüm ayarları
            self.settings_vars['theme'].set(
                self.config_manager.get('appearance.theme', 'light')
            )
            self.settings_vars['language'].set(
                self.config_manager.get('appearance.language', 'tr')
            )
            self.settings_vars['window_width'].set(
                self.config_manager.get('appearance.window_size.width', 1200)
            )
            self.settings_vars['window_height'].set(
                self.config_manager.get('appearance.window_size.height', 800)
            )
            self.settings_vars['animations'].set(
                self.config_manager.get('ui.animations_enabled', True)
            )
            self.settings_vars['tooltips'].set(
                self.config_manager.get('ui.show_tooltips', True)
            )
            self.settings_vars['sound_effects'].set(
                self.config_manager.get('ui.sound_effects', False)
            )
            
            # Gizlilik ayarları
            self.settings_vars['save_cache'].set(
                self.config_manager.get('privacy.save_cache', False)
            )
            self.settings_vars['save_logs'].set(
                self.config_manager.get('privacy.save_logs', False)
            )
            self.settings_vars['auto_cleanup'].set(
                self.config_manager.get('privacy.auto_cleanup', True)
            )
            self.settings_vars['cache_size_limit'].set(
                self.config_manager.get('performance.cache_size_limit_mb', 500)
            )
            self.settings_vars['telemetry'].set(
                self.config_manager.get('privacy.telemetry', False)
            )
            
            # PDF ayarları
            self.settings_vars['output_directory'].set(
                self.config_manager.get('pdf_processing.default_output_dir', str(Path.home() / 'Desktop'))
            )
            self.settings_vars['default_quality'].set(
                self.config_manager.get('pdf_processing.default_quality', 'medium')
            )
            self.settings_vars['default_dpi'].set(
                self.config_manager.get('pdf_processing.default_dpi', 300)
            )
            self.settings_vars['parallel_processing'].set(
                self.config_manager.get('pdf_processing.parallel_processing', True)
            )
            self.settings_vars['max_workers'].set(
                self.config_manager.get('pdf_processing.max_workers', 4)
            )
            self.settings_vars['memory_limit'].set(
                self.config_manager.get('performance.memory_limit_mb', 1024)
            )
            
            # OCR ayarları
            self.settings_vars['ocr_language'].set(
                self.config_manager.get('ocr.default_language', 'tur')
            )
            self.settings_vars['auto_detect_lang'].set(
                self.config_manager.get('ocr.auto_detect_language', True)
            )
            self.settings_vars['ocr_dpi'].set(
                self.config_manager.get('ocr.default_dpi', 300)
            )
            self.settings_vars['ocr_preprocessing'].set(
                self.config_manager.get('ocr.preprocessing', True)
            )
            self.settings_vars['ocr_deskew'].set(
                self.config_manager.get('ocr.deskew', True)
            )
            self.settings_vars['noise_removal'].set(
                self.config_manager.get('ocr.noise_removal', True)
            )
            
            # Sistem ayarları
            self.settings_vars['system_tray'].set(
                self.config_manager.get('system.system_tray', True)
            )
            self.settings_vars['file_association'].set(
                self.config_manager.get('system.file_association', False)
            )
            self.settings_vars['startup_with_system'].set(
                self.config_manager.get('system.startup_with_system', False)
            )
            self.settings_vars['check_updates'].set(
                self.config_manager.get('system.check_updates', True)
            )
            
            # Gelişmiş ayarlar
            self.settings_vars['debug_mode'].set(
                self.config_manager.get('debug_mode', False)
            )
            self.settings_vars['verbose_logging'].set(
                self.config_manager.get('verbose_logging', False)
            )
            self.settings_vars['experimental_gpu'].set(
                self.config_manager.get('experimental.gpu_acceleration', False)
            )
            self.settings_vars['experimental_ai_features'].set(
                self.config_manager.get('experimental.ai_features', False)
            )
            
            # OCR dilleri listesini yükle
            self.refresh_languages()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar yüklenirken hata: {e}")
    
    def center_dialog(self):
        """Dialog'u merkeze konumlandır"""
        self.dialog.update_idletasks()
        
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # Event handlers
    def on_theme_change(self):
        """Tema değişikliği"""
        self.has_changes = True
        
        # Önizleme (isteğe bağlı)
        new_theme = self.settings_vars['theme'].get()
        self.theme_manager.apply_theme(new_theme, self.dialog)
    
    def on_cache_change(self):
        """Cache ayarı değişikliği"""
        self.has_changes = True
        
        if not self.settings_vars['save_cache'].get():
            result = messagebox.askyesno(
                "Onay",
                "Cache devre dışı bırakılacak. Mevcut cache verilerini temizlemek ister misiniz?"
            )
            if result:
                self.clear_cache()
    
    def browse_output_directory(self):
        """Çıktı dizini seç"""
        current_dir = self.settings_vars['output_directory'].get()
        selected_dir = filedialog.askdirectory(
            title="Varsayılan Çıktı Dizini Seçin",
            initialdir=current_dir
        )
        
        if selected_dir:
            self.settings_vars['output_directory'].set(selected_dir)
            self.has_changes = True
    
    def clear_cache(self):
        """Cache temizle"""
        try:
            # Cache manager üzerinden temizle
            if hasattr(self.config_manager, 'app_instance'):
                cache_manager = getattr(self.config_manager.app_instance, 'cache_manager', None)
                if cache_manager:
                    cache_manager.clear_all()
                    messagebox.showinfo("Başarılı", "Cache başarıyla temizlendi")
                else:
                    messagebox.showwarning("Uyarı", "Cache manager bulunamadı")
            else:
                messagebox.showinfo("Bilgi", "Cache temizleme işlemi sonraki başlatmada etkili olacak")
        except Exception as e:
            messagebox.showerror("Hata", f"Cache temizlenirken hata: {e}")
    
    def install_language_pack(self):
        """Dil paketi kur"""
        try:
            from ui.language_installer import LanguageInstaller
            installer = LanguageInstaller(self.dialog)
            installer.show()
        except ImportError:
            messagebox.showinfo(
                "Bilgi", 
                "Dil paketi kurulumu için OCR modülü gerekli.\n"
                "Lütfen gerekli bağımlılıkları kurun:\n"
                "pip install pytesseract"
            )
    
    def refresh_languages(self):
        """Yüklü dilleri yenile"""
        try:
            self.installed_langs_listbox.delete(0, tk.END)
            
            # Config'den yüklü dilleri al
            installed_langs = self.config_manager.get('ocr.installed_languages', ['eng', 'tur'])
            
            for lang in installed_langs:
                display_name = self.get_language_display_name(lang)
                self.installed_langs_listbox.insert(tk.END, f"{lang} - {display_name}")
                
        except Exception as e:
            print(f"Dil listesi yenilenirken hata: {e}")
    
    def get_language_display_name(self, lang_code):
        """Dil kodundan görünen isim"""
        lang_names = {
            'tur': 'Türkçe',
            'eng': 'English', 
            'deu': 'Deutsch',
            'fra': 'Français',
            'spa': 'Español',
            'ita': 'Italiano'
        }
        return lang_names.get(lang_code, lang_code.upper())
    
    def check_updates_now(self):
        """Güncellemeleri şimdi kontrol et"""
        try:
            from utils import UpdateChecker
            
            def check_thread():
                checker = UpdateChecker("2.0.0")
                result = checker.check_for_updates()
                
                # UI thread'inde güncelle
                self.dialog.after(0, lambda: self.show_update_result(result))
            
            # Thread'de kontrol et
            thread = threading.Thread(target=check_thread, daemon=True)
            thread.start()
            
            # UI'da göster
            self.update_status_label.config(text="Kontrol ediliyor...")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme kontrolü başarısız: {e}")
    
    def show_update_result(self, result):
        """Güncelleme sonucunu göster"""
        try:
            if result.get('error'):
                self.update_status_label.config(text=f"Hata: {result['error']}")
                messagebox.showerror("Hata", f"Güncelleme kontrolü başarısız:\n{result['error']}")
            elif result.get('update_available'):
                self.update_status_label.config(text=f"Yeni sürüm mevcut: {result['latest_version']}")
                messagebox.showinfo(
                    "Güncelleme Mevcut",
                    f"Yeni sürüm mevcut!\n\n"
                    f"Mevcut: {result['current_version']}\n"
                    f"Yeni: {result['latest_version']}\n\n"
                    f"İndir: {result.get('download_url', 'GitHub sayfası')}"
                )
            else:
                self.update_status_label.config(text="Güncel sürüm kullanılıyor")
                messagebox.showinfo("Güncel", "En güncel sürümü kullanıyorsunuz!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Sonuç gösterilemedi: {e}")
    
    def open_log_folder(self):
        """Log klasörünü aç"""
        try:
            if hasattr(self.config_manager, 'app_instance'):
                log_manager = getattr(self.config_manager.app_instance, 'log_manager', None)
                if log_manager and hasattr(log_manager, 'log_dir'):
                    log_dir = log_manager.log_dir
                    if os.name == 'nt':  # Windows
                        os.startfile(log_dir)
                    elif os.name == 'posix':  # macOS/Linux
                        os.system(f'xdg-open "{log_dir}"')
                    return
            
            messagebox.showinfo("Bilgi", "Log klasörü bulunamadı")
        except Exception as e:
            messagebox.showerror("Hata", f"Log klasörü açılamadı: {e}")
    
    def clear_logs(self):
        """Log dosyalarını temizle"""
        result = messagebox.askyesno(
            "Onay",
            "Tüm log dosyaları silinecek. Emin misiniz?"
        )
        
        if result:
            try:
                if hasattr(self.config_manager, 'app_instance'):
                    log_manager = getattr(self.config_manager.app_instance, 'log_manager', None)
                    if log_manager and hasattr(log_manager, 'clear_logs'):
                        log_manager.clear_logs()
                        messagebox.showinfo("Başarılı", "Log dosyaları temizlendi")
                        return
                
                messagebox.showinfo("Bilgi", "Log temizleme işlemi sonraki başlatmada etkili olacak")
            except Exception as e:
                messagebox.showerror("Hata", f"Log temizlenirken hata: {e}")
    
    def export_config(self):
        """Ayarları dışa aktar"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Ayarları Kaydet",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.config_manager.export_config(filename)
                messagebox.showinfo("Başarılı", f"Ayarlar kaydedildi:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}")
    
    def import_config(self):
        """Ayarları içe aktar"""
        try:
            filename = filedialog.askopenfilename(
                title="Ayarları Yükle",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                result = messagebox.askyesno(
                    "Onay",
                    "Mevcut ayarlar değişecek. Devam etmek istiyor musunuz?"
                )
                
                if result:
                    self.config_manager.import_config(filename)
                    self.load_current_settings()  # Yeniden yükle
                    messagebox.showinfo("Başarılı", "Ayarlar yüklendi")
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar yüklenemedi: {e}")
    
    def open_config_folder(self):
        """Config klasörünü aç"""
        try:
            config_dir = self.config_manager.config_dir
            if os.name == 'nt':  # Windows
                os.startfile(config_dir)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'xdg-open "{config_dir}"')
        except Exception as e:
            messagebox.showerror("Hata", f"Config klasörü açılamadı: {e}")
    
    def reset_to_defaults(self):
        """Varsayılanlara sıfırla"""
        result = messagebox.askyesno(
            "Onay",
            "Tüm ayarlar varsayılan değerlere sıfırlanacak. Emin misiniz?"
        )
        
        if result:
            try:
                self.config_manager.reset_to_defaults()
                self.load_current_settings()
                messagebox.showinfo("Başarılı", "Ayarlar varsayılanlara sıfırlandı")
                self.has_changes = False
            except Exception as e:
                messagebox.showerror("Hata", f"Sıfırlama başarısız: {e}")
    
    def apply_settings(self):
        """Ayarları uygula"""
        try:
            self.save_settings()
            messagebox.showinfo("Başarılı", "Ayarlar uygulandı")
            self.has_changes = False
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar uygulanamadı: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            # Görünüm ayarları
            self.config_manager.set('appearance.theme', self.settings_vars['theme'].get())
            self.config_manager.set('appearance.language', self.settings_vars['language'].get())
            self.config_manager.set('appearance.window_size.width', self.settings_vars['window_width'].get())
            self.config_manager.set('appearance.window_size.height', self.settings_vars['window_height'].get())
            self.config_manager.set('ui.animations_enabled', self.settings_vars['animations'].get())
            self.config_manager.set('ui.show_tooltips', self.settings_vars['tooltips'].get())
            self.config_manager.set('ui.sound_effects', self.settings_vars['sound_effects'].get())
            
            # Gizlilik ayarları
            self.config_manager.set('privacy.save_cache', self.settings_vars['save_cache'].get())
            self.config_manager.set('privacy.save_logs', self.settings_vars['save_logs'].get())
            self.config_manager.set('privacy.auto_cleanup', self.settings_vars['auto_cleanup'].get())
            self.config_manager.set('performance.cache_size_limit_mb', self.settings_vars['cache_size_limit'].get())
            self.config_manager.set('privacy.telemetry', self.settings_vars['telemetry'].get())
            
            # PDF ayarları
            self.config_manager.set('pdf_processing.default_output_dir', self.settings_vars['output_directory'].get())
            self.config_manager.set('pdf_processing.default_quality', self.settings_vars['default_quality'].get())
            self.config_manager.set('pdf_processing.default_dpi', self.settings_vars['default_dpi'].get())
            self.config_manager.set('pdf_processing.parallel_processing', self.settings_vars['parallel_processing'].get())
            self.config_manager.set('pdf_processing.max_workers', self.settings_vars['max_workers'].get())
            self.config_manager.set('performance.memory_limit_mb', self.settings_vars['memory_limit'].get())
            
            # OCR ayarları
            self.config_manager.set('ocr.default_language', self.settings_vars['ocr_language'].get())
            self.config_manager.set('ocr.auto_detect_language', self.settings_vars['auto_detect_lang'].get())
            self.config_manager.set('ocr.default_dpi', self.settings_vars['ocr_dpi'].get())
            self.config_manager.set('ocr.preprocessing', self.settings_vars['ocr_preprocessing'].get())
            self.config_manager.set('ocr.deskew', self.settings_vars['ocr_deskew'].get())
            self.config_manager.set('ocr.noise_removal', self.settings_vars['noise_removal'].get())
            
            # Sistem ayarları
            self.config_manager.set('system.system_tray', self.settings_vars['system_tray'].get())
            self.config_manager.set('system.file_association', self.settings_vars['file_association'].get())
            self.config_manager.set('system.startup_with_system', self.settings_vars['startup_with_system'].get())
            self.config_manager.set('system.check_updates', self.settings_vars['check_updates'].get())
            
            # Gelişmiş ayarlar
            self.config_manager.set('debug_mode', self.settings_vars['debug_mode'].get())
            self.config_manager.set('verbose_logging', self.settings_vars['verbose_logging'].get())
            self.config_manager.set('experimental.gpu_acceleration', self.settings_vars['experimental_gpu'].get())
            self.config_manager.set('experimental.ai_features', self.settings_vars['experimental_ai_features'].get())
            
            # Kaydet
            self.config_manager.save()
            
        except Exception as e:
            raise Exception(f"Ayarlar kaydedilemedi: {e}")
    
    def on_ok(self):
        """Tamam butonu"""
        try:
            if self.has_changes:
                self.save_settings()
            self.close_dialog()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    
    def on_cancel(self):
        """İptal butonu"""
        if self.has_changes:
            result = messagebox.askyesno(
                "Onay",
                "Kaydedilmemiş değişiklikler var. Çıkmak istediğinizden emin misiniz?"
            )
            if not result:
                return
        
        self.close_dialog()
    
    def on_close(self):
        """Pencere kapatma"""
        self.on_cancel()
    
    def close_dialog(self):
        """Dialog'u kapat"""
        try:
            if self.dialog:
                self.dialog.grab_release()
                self.dialog.destroy()
                self.dialog = None
        except:
            pass

# Yardımcı sınıf - Dil kurulum penceresi
class LanguageInstaller:
    """OCR Dil paketi kurulum penceresi"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Dil kurulum penceresini göster"""
        if self.dialog:
            return
            
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("OCR Dil Paketi Kurulumu")
        self.dialog.geometry("400x300")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # İçerik
        ttk.Label(
            self.dialog,
            text="OCR Dil Paketi Kurulumu",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        ttk.Label(
            self.dialog,
            text="Bu özellik henüz geliştirilmekte.\n"
                 "Manuel kurulum için:\n\n"
                 "1. Tesseract OCR kurulu olmalı\n"
                 "2. Dil paketleri sistem seviyesinde kurulmalı\n"
                 "3. Uygulama yeniden başlatılmalı"
        ).pack(pady=20, padx=20)
        
        ttk.Button(
            self.dialog,
            text="Kapat",
            command=self.dialog.destroy
        ).pack(pady=10)

if __name__ == "__main__":
    # Test için basit örnek
    root = tk.Tk()
    root.withdraw()
    
    class MockConfig:
        def get(self, key, default=None):
            return default
        def set(self, key, value):
            pass
        def save(self):
            pass
    
    class MockTheme:
        def apply_theme(self, theme, widget):
            pass
    
    settings = SettingsDialog(root, MockConfig(), MockTheme())
    settings.show()
    
    root.mainloop()
theme'] = tk.StringVar()
        
        themes = [
            ('light', '☀️ Aydınlık'),
            ('dark', '🌙 Karanlık'), 
            ('neon', '⚡ Neon'),
            ('midnight', '🌊 Gece Yarısı Mavisi')
        ]
        
        for i, (theme_id, theme_name) in enumerate(themes):
            rb = ttk.Radiobutton(
                theme_group,
                text=theme_name,
                variable=self.settings_vars['theme'],
                value=theme_id,
                command=self.on_theme_change
            )
            rb.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        
        # Dil seçimi
        lang_group = ttk.LabelFrame(scrollable_frame, text="🌍 Dil", padding=10)
        lang_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(lang_group, text="Arayüz Dili:").grid(row=0, column=0, sticky='w', pady=2)
        
        self.settings_vars['language'] = tk.StringVar()
        lang_combo = ttk.Combobox(
            lang_group,
            textvariable=self.settings_vars['language'],
            values=['tr - Türkçe', 'en - English', 'de - Deutsch', 'fr - Français'],
            state='readonly',
            width=20
        )
        lang_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Pencere ayarları
        window_group = ttk.LabelFrame(scrollable_frame, text="🪟 Pencere", padding=10)
        window_group.pack(fill=tk.X, padx=10, pady=5)
        
        # Başlangıç boyutu
        ttk.Label(window_group, text="Başlangıç Boyutu:").grid(row=0, column=0, sticky='w', pady=2)
        
        size_frame = ttk.Frame(window_group)
        size_frame.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        self.settings_vars['window_width'] = tk.IntVar()
        self.settings_vars['window_height'] = tk.IntVar()
        
        ttk.Label(size_frame, text="Genişlik:").pack(side=tk.LEFT)
        width_spin = ttk.Spinbox(
            size_frame,
            from_=800, to=2560, increment=50,
            textvariable=self.settings_vars['window_width'],
            width=8
        )
        width_spin.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(size_frame, text="Yükseklik:").pack(side=tk.LEFT)
        height_spin = ttk.Spinbox(
            size_frame,
            from_=600, to=1440, increment=50,
            textvariable=self.settings_vars['window_height'],
            width=8
        )
        height_spin.pack(side=tk.LEFT, padx=5)
        
        # UI Efektleri
        effects_group = ttk.LabelFrame(scrollable_frame, text="✨ Efektler", padding=10)
        effects_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['animations'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_group,
            text="Animasyonları etkinleştir",
            variable=self.settings_vars['animations']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['tooltips'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_group,
            text="Tooltip'leri göster",
            variable=self.settings_vars['tooltips']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['sound_effects'] = tk.BooleanVar()
        ttk.Checkbutton(
            effects_group,
            text="Ses efektleri",
            variable=self.settings_vars['sound_effects']
        ).pack(anchor='w', pady=2)
    
    def create_privacy_tab(self, parent):
        """Gizlilik ayarları sekmesi"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Veri saklama
        storage_group = ttk.LabelFrame(scrollable_frame, text="💾 Veri Saklama", padding=10)
        storage_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['save_cache'] = tk.BooleanVar()
        cache_cb = ttk.Checkbutton(
            storage_group,
            text="Cache verilerini sakla (performans artışı)",
            variable=self.settings_vars['save_cache'],
            command=self.on_cache_change
        )
        cache_cb.pack(anchor='w', pady=2)
        
        self.settings_vars['save_logs'] = tk.BooleanVar()
        logs_cb = ttk.Checkbutton(
            storage_group,
            text="Log dosyalarını sakla (sorun giderme için)",
            variable=self.settings_vars['save_logs']
        )
        logs_cb.pack(anchor='w', pady=2)
        
        self.settings_vars['auto_cleanup'] = tk.BooleanVar()
        cleanup_cb = ttk.Checkbutton(
            storage_group,
            text="Uygulama kapandığında geçici dosyaları temizle",
            variable=self.settings_vars['auto_cleanup']
        )
        cleanup_cb.pack(anchor='w', pady=2)
        
        # Cache boyutu
        cache_size_frame = ttk.Frame(storage_group)
        cache_size_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(cache_size_frame, text="Maksimum Cache Boyutu (MB):").pack(side=tk.LEFT)
        
        self.settings_vars['cache_size_limit'] = tk.IntVar()
        cache_size_spin = ttk.Spinbox(
            cache_size_frame,
            from_=100, to=2048, increment=100,
            textvariable=self.settings_vars['cache_size_limit'],
            width=8
        )
        cache_size_spin.pack(side=tk.LEFT, padx=10)
        
        # Cache temizleme butonu
        ttk.Button(
            cache_size_frame,
            text="🧹 Cache Temizle",
            command=self.clear_cache
        ).pack(side=tk.RIGHT)
        
        # Telemetry
        telemetry_group = ttk.LabelFrame(scrollable_frame, text="📊 Telemetri", padding=10)
        telemetry_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['telemetry'] = tk.BooleanVar()
        ttk.Checkbutton(
            telemetry_group,
            text="Anonim kullanım istatistikleri gönder (geliştirme için)",
            variable=self.settings_vars['telemetry']
        ).pack(anchor='w', pady=2)
        
        ttk.Label(
            telemetry_group,
            text="Not: Sadece anonim kullanım verileri toplanır, kişisel bilgiler asla paylaşılmaz.",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor='w', pady=2)
    
    def create_pdf_tab(self, parent):
        """PDF işleme ayarları sekmesi"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Varsayılan ayarlar
        defaults_group = ttk.LabelFrame(scrollable_frame, text="⚙️ Varsayılan Ayarlar", padding=10)
        defaults_group.pack(fill=tk.X, padx=10, pady=5)
        
        # Çıktı dizini
        output_frame = ttk.Frame(defaults_group)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Varsayılan Çıktı Dizini:").pack(anchor='w')
        
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.settings_vars['output_directory'] = tk.StringVar()
        output_entry = ttk.Entry(
            path_frame,
            textvariable=self.settings_vars['output_directory']
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            path_frame,
            text="📁 Seç",
            command=self.browse_output_directory
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Kalite ayarları
        quality_frame = ttk.Frame(defaults_group)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Varsayılan Kalite:").pack(side=tk.LEFT)
        
        self.settings_vars['default_quality'] = tk.StringVar()
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.settings_vars['default_quality'],
            values=['low', 'medium', 'high'],
            state='readonly',
            width=10
        )
        quality_combo.pack(side=tk.LEFT, padx=10)
        
        # DPI ayarları  
        dpi_frame = ttk.Frame(defaults_group)
        dpi_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dpi_frame, text="Varsayılan DPI:").pack(side=tk.LEFT)
        
        self.settings_vars['default_dpi'] = tk.IntVar()
        dpi_spin = ttk.Spinbox(
            dpi_frame,
            from_=72, to=600, increment=25,
            textvariable=self.settings_vars['default_dpi'],
            width=8
        )
        dpi_spin.pack(side=tk.LEFT, padx=10)
        
        # Performans ayarları
        perf_group = ttk.LabelFrame(scrollable_frame, text="🚀 Performans", padding=10)
        perf_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['parallel_processing'] = tk.BooleanVar()
        ttk.Checkbutton(
            perf_group,
            text="Paralel işleme kullan (daha hızlı)",
            variable=self.settings_vars['parallel_processing']
        ).pack(anchor='w', pady=2)
        
        # İşçi sayısı
        workers_frame = ttk.Frame(perf_group)
        workers_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(workers_frame, text="Maksimum İşçi Thread Sayısı:").pack(side=tk.LEFT)
        
        self.settings_vars['max_workers'] = tk.IntVar()
        workers_spin = ttk.Spinbox(
            workers_frame,
            from_=1, to=16, increment=1,
            textvariable=self.settings_vars['max_workers'],
            width=5
        )
        workers_spin.pack(side=tk.LEFT, padx=10)
        
        # Bellek sınırı
        memory_frame = ttk.Frame(perf_group)
        memory_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(memory_frame, text="Bellek Sınırı (MB):").pack(side=tk.LEFT)
        
        self.settings_vars['memory_limit'] = tk.IntVar()
        memory_spin = ttk.Spinbox(
            memory_frame,
            from_=512, to=8192, increment=512,
            textvariable=self.settings_vars['memory_limit'],
            width=8
        )
        memory_spin.pack(side=tk.LEFT, padx=10)
    
    def create_ocr_tab(self, parent):
        """OCR ayarları sekmesi"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Varsayılan dil
        lang_group = ttk.LabelFrame(scrollable_frame, text="🌍 Dil Ayarları", padding=10)
        lang_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(lang_group, text="Varsayılan OCR Dili:").grid(row=0, column=0, sticky='w', pady=2)
        
        self.settings_vars['ocr_language'] = tk.StringVar()
        ocr_lang_combo = ttk.Combobox(
            lang_group,
            textvariable=self.settings_vars['ocr_language'],
            values=['tur', 'eng', 'deu', 'fra', 'spa'],
            state='readonly',
            width=10
        )
        ocr_lang_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        self.settings_vars['auto_detect_lang'] = tk.BooleanVar()
        ttk.Checkbutton(
            lang_group,
            text="Otomatik dil algılama",
            variable=self.settings_vars['auto_detect_lang']
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=2)
        
        # Yüklü diller
        installed_frame = ttk.Frame(lang_group)
        installed_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(installed_frame, text="Yüklü Dil Paketleri:").pack(anchor='w')
        
        # Listbox ve scrollbar
        listbox_frame = ttk.Frame(installed_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.installed_langs_listbox = tk.Listbox(listbox_frame, height=4)
        lang_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        
        self.installed_langs_listbox.config(yscrollcommand=lang_scrollbar.set)
        lang_scrollbar.config(command=self.installed_langs_listbox.yview)
        
        self.installed_langs_listbox.pack(side="left", fill="both", expand=True)
        lang_scrollbar.pack(side="right", fill="y")
        
        # Dil yönetim butonları
        lang_buttons = ttk.Frame(installed_frame)
        lang_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            lang_buttons,
            text="➕ Dil Paketi Kur",
            command=self.install_language_pack
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            lang_buttons,
            text="🔄 Yenile",
            command=self.refresh_languages
        ).pack(side=tk.LEFT, padx=5)
        
        # OCR kalite ayarları
        quality_group = ttk.LabelFrame(scrollable_frame, text="🔍 Kalite Ayarları", padding=10)
        quality_group.pack(fill=tk.X, padx=10, pady=5)
        
        # OCR DPI
        dpi_frame = ttk.Frame(quality_group)
        dpi_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(dpi_frame, text="OCR DPI:").pack(side=tk.LEFT)
        
        self.settings_vars['ocr_dpi'] = tk.IntVar()
        ocr_dpi_spin = ttk.Spinbox(
            dpi_frame,
            from_=150, to=600, increment=25,
            textvariable=self.settings_vars['ocr_dpi'],
            width=8
        )
        ocr_dpi_spin.pack(side=tk.LEFT, padx=10)
        
        # Ön işleme seçenekleri
        preprocessing_group = ttk.LabelFrame(scrollable_frame, text="🛠️ Ön İşleme", padding=10)
        preprocessing_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['ocr_preprocessing'] = tk.BooleanVar()
        ttk.Checkbutton(
            preprocessing_group,
            text="Görüntü ön işleme uygula",
            variable=self.settings_vars['ocr_preprocessing']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['ocr_deskew'] = tk.BooleanVar()
        ttk.Checkbutton(
            preprocessing_group,
            text="Eğim düzeltme",
            variable=self.settings_vars['ocr_deskew']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['noise_removal'] = tk.BooleanVar()
        ttk.Checkbutton(
            preprocessing_group,
            text="Gürültü azaltma",
            variable=self.settings_vars['noise_removal']
        ).pack(anchor='w', pady=2)
    
    def create_system_tab(self, parent):
        """Sistem ayarları sekmesi"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sistem entegrasyonu
        integration_group = ttk.LabelFrame(scrollable_frame, text="🔗 Sistem Entegrasyonu", padding=10)
        integration_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['system_tray'] = tk.BooleanVar()
        ttk.Checkbutton(
            integration_group,
            text="Sistem tepsisinde göster",
            variable=self.settings_vars['system_tray']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['file_association'] = tk.BooleanVar()
        ttk.Checkbutton(
            integration_group,
            text="PDF dosyalarını bu uygulamayla ilişkilendir",
            variable=self.settings_vars['file_association']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['startup_with_system'] = tk.BooleanVar()
        ttk.Checkbutton(
            integration_group,
            text="Sistem başlangıcında başlat",
            variable=self.settings_vars['startup_with_system']
        ).pack(anchor='w', pady=2)
        
        # Güncellemeler
        update_group = ttk.LabelFrame(scrollable_frame, text="🔄 Güncellemeler", padding=10)
        update_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['check_updates'] = tk.BooleanVar()
        ttk.Checkbutton(
            update_group,
            text="Başlangıçta güncellemeleri kontrol et",
            variable=self.settings_vars['check_updates']
        ).pack(anchor='w', pady=2)
        
        # Güncelleme kontrolü butonu
        update_buttons = ttk.Frame(update_group)
        update_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            update_buttons,
            text="🔍 Şimdi Kontrol Et",
            command=self.check_updates_now
        ).pack(side=tk.LEFT)
        
        self.update_status_label = ttk.Label(
            update_buttons,
            text="Son kontrol: Hiçbir zaman",
            font=('Arial', 8),
            foreground='gray'
        )
        self.update_status_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_advanced_tab(self, parent):
        """Gelişmiş ayarlar sekmesi"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Debug ayarları
        debug_group = ttk.LabelFrame(scrollable_frame, text="🐛 Debug", padding=10)
        debug_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['debug_mode'] = tk.BooleanVar()
        ttk.Checkbutton(
            debug_group,
            text="Debug modunu etkinleştir",
            variable=self.settings_vars['debug_mode']
        ).pack(anchor='w', pady=2)
        
        self.settings_vars['