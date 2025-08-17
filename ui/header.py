#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Modern Header Bileşeni
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import json

class ModernHeader(ttk.Frame):
    """
    Modern ve animasyonlu header bileşeni
    """
    
    def __init__(self, parent, config_manager, theme_manager, app_instance):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.app_instance = app_instance
        
        # Header durumu
        self.current_theme = self.config_manager.get('appearance.theme', 'light')
        self.current_language = self.config_manager.get('appearance.language', 'tr')
        self.search_active = False
        
        # Animasyon durumu
        self.animation_running = False
        self.theme_transition_active = False
        
        # UI elemanları
        self.logo_frame = None
        self.search_frame = None
        self.controls_frame = None
        self.theme_buttons = {}
        self.search_var = tk.StringVar()
        
        self.create_header()
        self.setup_animations()
        self.apply_current_theme()
    
    def create_header(self):
        """Header'ı oluştur"""
        self.configure(height=60, style='Header.TFrame')
        self.pack_propagate(False)
        
        # Ana container
        main_container = ttk.Frame(self, style='HeaderContainer.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
        
        # Sol taraf - Logo ve title
        self.create_logo_section(main_container)
        
        # Orta - Arama çubuğu
        self.create_search_section(main_container)
        
        # Sağ taraf - Kontroller
        self.create_controls_section(main_container)
    
    def create_logo_section(self, parent):
        """Logo ve başlık bölümünü oluştur"""
        self.logo_frame = ttk.Frame(parent, style='HeaderSection.TFrame')
        self.logo_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Logo ikonu
        logo_container = ttk.Frame(self.logo_frame, style='LogoContainer.TFrame')
        logo_container.pack(side=tk.LEFT, padx=(0, 12))
        
        # Logo için canvas
        self.logo_canvas = tk.Canvas(
            logo_container, 
            width=32, 
            height=32, 
            highlightthickness=0,
            relief='flat'
        )
        self.logo_canvas.pack()
        
        self.create_animated_logo()
        
        # Başlık ve versiyon
        title_frame = ttk.Frame(self.logo_frame, style='TitleFrame.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        # Ana başlık
        title_label = ttk.Label(
            title_frame,
            text="PyPDF-Stirling Tools",
            style='Title.TLabel'
        )
        title_label.pack(anchor='w')
        
        # Versiyon
        version_label = ttk.Label(
            title_frame,
            text="v2.0",
            style='Version.TLabel'
        )
        version_label.pack(anchor='w')
        
        # Hover efekti
        self.add_hover_effect(self.logo_frame, self.on_logo_hover, self.on_logo_leave)
    
    def create_animated_logo(self):
        """Animasyonlu logo oluştur"""
        self.logo_canvas.delete("all")
        
        # Gradient background
        colors = self.get_logo_colors()
        self.create_gradient_background(colors['primary'], colors['secondary'])
        
        # PDF ikonu
        self.create_pdf_icon()
        
        # Animasyon başlat
        self.start_logo_animation()
    
    def get_logo_colors(self):
        """Tema göre logo renklerini al"""
        theme_colors = {
            'light': {'primary': '#3b82f6', 'secondary': '#2563eb', 'text': '#ffffff'},
            'dark': {'primary': '#60a5fa', 'secondary': '#3b82f6', 'text': '#1e293b'},
            'neon': {'primary': '#00ffff', 'secondary': '#00e6e6', 'text': '#0a0a0a'},
            'midnight': {'primary': '#0ea5e9', 'secondary': '#0284c7', 'text': '#e2e8f0'}
        }
        return theme_colors.get(self.current_theme, theme_colors['light'])
    
    def create_gradient_background(self, color1, color2):
        """Gradient arkaplan oluştur"""
        # Basit gradient efekti
        self.logo_canvas.create_oval(
            2, 2, 30, 30,
            fill=color1,
            outline=color2,
            width=2,
            tags="logo_bg"
        )
    
    def create_pdf_icon(self):
        """PDF ikonu oluştur"""
        # PDF simgesi
        self.logo_canvas.create_text(
            16, 16,
            text="📄",
            font=("Arial", 14),
            fill="white",
            tags="pdf_icon"
        )
    
    def start_logo_animation(self):
        """Logo animasyonunu başlat"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_logo_pulse()
    
    def animate_logo_pulse(self):
        """Logo nabız animasyonu"""
        if not self.animation_running:
            return
        
        # Nabız efekti
        for scale in [1.0, 1.1, 1.0]:
            if self.animation_running:
                self.logo_canvas.after(500, lambda s=scale: self.scale_logo(s))
        
        # Döngüyü devam ettir
        self.logo_canvas.after(3000, self.animate_logo_pulse)
    
    def scale_logo(self, scale):
        """Logo ölçeklendirme"""
        try:
            # Canvas elemanlarını ölçeklendir
            self.logo_canvas.scale("all", 16, 16, scale, scale)
        except tk.TclError:
            pass  # Canvas yok edilmişse hata verme
    
    def create_search_section(self, parent):
        """Arama bölümünü oluştur"""
        self.search_frame = ttk.Frame(parent, style='SearchFrame.TFrame')
        self.search_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=20)
        
        # Arama container'ı
        search_container = ttk.Frame(self.search_frame, style='SearchContainer.TFrame')
        search_container.pack(anchor='center')
        
        # Arama ikonu
        search_icon = ttk.Label(
            search_container,
            text="🔍",
            style='SearchIcon.TLabel'
        )
        search_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        # Arama giriş alanı
        self.search_entry = ttk.Entry(
            search_container,
            textvariable=self.search_var,
            style='Search.TEntry',
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Placeholder text
        self.setup_search_placeholder()
        
        # Arama eventi
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        # Temizle butonu
        self.clear_button = ttk.Button(
            search_container,
            text="✕",
            style='SearchClear.TButton',
            width=3,
            command=self.clear_search
        )
        self.clear_button.pack(side=tk.LEFT, padx=(5, 10))
        
        # Gelişmiş arama butonu
        advanced_search_btn = ttk.Button(
            search_container,
            text="⚙",
            style='AdvancedSearch.TButton',
            width=3,
            command=self.show_advanced_search
        )
        advanced_search_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_search_placeholder(self):
        """Arama placeholder ayarla"""
        placeholder_text = self.get_text('search_placeholder', 'PDF içinde ara...')
        
        def add_placeholder():
            if not self.search_var.get():
                self.search_entry.configure(foreground='gray')
                self.search_var.set(placeholder_text)
        
        def remove_placeholder(event=None):
            if self.search_var.get() == placeholder_text:
                self.search_var.set('')
                self.search_entry.configure(foreground='black')
        
        # İlk placeholder'ı ekle
        add_placeholder()
        
        # Event binding
        self.search_entry.bind('<FocusIn>', remove_placeholder)
        self.search_entry.bind('<FocusOut>', lambda e: add_placeholder())
    
    def create_controls_section(self, parent):
        """Kontroller bölümünü oluştur"""
        self.controls_frame = ttk.Frame(parent, style='ControlsFrame.TFrame')
        self.controls_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Tema seçicisi
        self.create_theme_selector()
        
        # Dil seçicisi
        self.create_language_selector()
        
        # Ayarlar butonu
        self.create_settings_button()
        
        # Bildirim butonu
        self.create_notification_button()
        
        # Profil butonu
        self.create_profile_button()
    
    def create_theme_selector(self):
        """Tema seçicisini oluştur"""
        theme_frame = ttk.Frame(self.controls_frame, style='ThemeFrame.TFrame')
        theme_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Tema butonları container'ı
        themes_container = ttk.Frame(theme_frame, style='ThemesContainer.TFrame')
        themes_container.pack()
        
        themes = [
            ('light', '☀️', 'Aydınlık'),
            ('dark', '🌙', 'Karanlık'),
            ('neon', '⚡', 'Neon'),
            ('midnight', '🌊', 'Gece Yarısı')
        ]
        
        for theme_id, icon, tooltip in themes:
            btn = self.create_theme_button(themes_container, theme_id, icon, tooltip)
            self.theme_buttons[theme_id] = btn
        
        # Aktif temayı işaretle
        self.update_active_theme_button()
    
    def create_theme_button(self, parent, theme_id, icon, tooltip):
        """Tema butonu oluştur"""
        btn = ttk.Button(
            parent,
            text=icon,
            style=f'Theme{theme_id.title()}.TButton',
            width=3,
            command=lambda: self.change_theme(theme_id)
        )
        btn.pack(side=tk.LEFT, padx=1)
        
        # Tooltip ekle
        self.add_tooltip(btn, tooltip)
        
        # Hover animasyonu
        self.add_theme_button_animation(btn, theme_id)
        
        return btn
    
    def create_language_selector(self):
        """Dil seçicisini oluştur"""
        lang_frame = ttk.Frame(self.controls_frame, style='LangFrame.TFrame')
        lang_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Dil dropdown
        languages = [
            ('tr', '🇹🇷 Türkçe'),
            ('en', '🇺🇸 English'),
            ('de', '🇩🇪 Deutsch'),
            ('fr', '🇫🇷 Français'),
            ('es', '🇪🇸 Español')
        ]
        
        self.lang_var = tk.StringVar(value=self.current_language)
        
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=[f"{code} {name}" for code, name in languages],
            state="readonly",
            style='Language.TCombobox',
            width=12
        )
        lang_combo.pack()
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Mevcut dili ayarla
        for i, (code, name) in enumerate(languages):
            if code == self.current_language:
                lang_combo.current(i)
                break
    
    def create_settings_button(self):
        """Ayarlar butonunu oluştur"""
        settings_btn = ttk.Button(
            self.controls_frame,
            text="⚙",
            style='Settings.TButton',
            width=3,
            command=self.show_settings
        )
        settings_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.add_tooltip(settings_btn, self.get_text('settings', 'Ayarlar'))
        self.add_button_animation(settings_btn)
    
    def create_notification_button(self):
        """Bildirim butonunu oluştur"""
        self.notification_btn = ttk.Button(
            self.controls_frame,
            text="🔔",
            style='Notification.TButton',
            width=3,
            command=self.show_notifications
        )
        self.notification_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bildirim badge'i
        self.notification_badge = ttk.Label(
            self.notification_btn,
            text="3",
            style='NotificationBadge.TLabel'
        )
        
        self.add_tooltip(self.notification_btn, self.get_text('notifications', 'Bildirimler'))
        self.add_button_animation(self.notification_btn)
    
    def create_profile_button(self):
        """Profil butonunu oluştur"""
        profile_btn = ttk.Button(
            self.controls_frame,
            text="👤",
            style='Profile.TButton',
            width=3,
            command=self.show_profile_menu
        )
        profile_btn.pack(side=tk.LEFT)
        
        self.add_tooltip(profile_btn, self.get_text('profile', 'Profil'))
        self.add_button_animation(profile_btn)
    
    def setup_animations(self):
        """Animasyonları ayarla"""
        self.animation_queue = []
        self.animation_thread = None
    
    def add_hover_effect(self, widget, on_enter, on_leave):
        """Hover efekti ekle"""
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
        # Alt widget'lara da bind et
        for child in widget.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
    
    def add_tooltip(self, widget, text):
        """Tooltip ekle"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(
                tooltip,
                text=text,
                background="yellow",
                relief="solid",
                borderwidth=1
            )
            label.pack()
            
            # 2 saniye sonra gizle
            tooltip.after(2000, tooltip.destroy)
        
        widget.bind('<Enter>', show_tooltip)
    
    def add_button_animation(self, button):
        """Buton animasyonu ekle"""
        original_style = button.cget('style')
        
        def on_enter(event):
            button.configure(style=f'Hover.{original_style}')
            # Hafif büyütme efekti simüle et
            button.configure(cursor='hand2')
        
        def on_leave(event):
            button.configure(style=original_style)
            button.configure(cursor='')
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    def add_theme_button_animation(self, button, theme_id):
        """Tema butonu animasyonu"""
        def on_enter(event):
            if theme_id != self.current_theme:
                # Preview efekti
                self.preview_theme(theme_id)
        
        def on_leave(event):
            if theme_id != self.current_theme:
                # Preview'ı kapat
                self.end_theme_preview()
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    # Event Handlers
    def on_logo_hover(self, event):
        """Logo hover olayı"""
        # Logo animasyonunu hızlandır
        self.start_logo_animation()
    
    def on_logo_leave(self, event):
        """Logo leave olayı"""
        pass
    
    def on_search_change(self, event):
        """Arama değişikliği olayı"""
        query = self.search_var.get().strip()
        
        if query and query != self.get_text('search_placeholder', 'PDF içinde ara...'):
            # Real-time arama
            self.perform_search(query)
        else:
            # Aramayı temizle
            self.clear_search_results()
    
    def on_search_focus_in(self, event):
        """Arama odaklanma olayı"""
        self.search_active = True
        self.animate_search_focus()
    
    def on_search_focus_out(self, event):
        """Arama odak kaybı olayı"""
        self.search_active = False
        self.animate_search_blur()
    
    def on_language_change(self, event):
        """Dil değişikliği olayı"""
        selected = self.lang_var.get()
        lang_code = selected.split()[0]
        
        if lang_code != self.current_language:
            self.change_language(lang_code)
    
    # Actions
    def change_theme(self, theme_id):
        """Temayı değiştir"""
        if theme_id == self.current_theme or self.theme_transition_active:
            return
        
        self.theme_transition_active = True
        
        # Tema geçiş animasyonu başlat
        self.animate_theme_transition(theme_id)
        
        # Temayı uygula
        self.apply_theme(theme_id)
        
        # Ayarlara kaydet
        self.config_manager.set('appearance.theme', theme_id)
        self.config_manager.save()
        
        # UI'ı güncelle
        self.update_active_theme_button()
        
        self.theme_transition_active = False
    
    def preview_theme(self, theme_id):
        """Tema önizlemesi göster"""
        # Hafif önizleme efekti
        pass
    
    def end_theme_preview(self):
        """Tema önizlemesini sonlandır"""
        pass
    
    def change_language(self, lang_code):
        """Dil değiştir"""
        self.current_language = lang_code
        
        # Konfigürasyonu güncelle
        self.config_manager.set('appearance.language', lang_code)
        self.config_manager.save()
        
        # UI metinlerini güncelle
        self.update_ui_texts()
        
        # Ana uygulamaya bildir
        if hasattr(self.app_instance, 'on_language_changed'):
            self.app_instance.on_language_changed(lang_code)
    
    def perform_search(self, query):
        """Arama gerçekleştir"""
        # Ana uygulamada arama yap
        if hasattr(self.app_instance, 'content') and self.app_instance.content:
            self.app_instance.content.search_content(query)
    
    def clear_search(self):
        """Aramayı temizle"""
        self.search_var.set('')
        self.clear_search_results()
    
    def clear_search_results(self):
        """Arama sonuçlarını temizle"""
        if hasattr(self.app_instance, 'content') and self.app_instance.content:
            self.app_instance.content.clear_search_results()
    
    def show_advanced_search(self):
        """Gelişmiş arama penceresini göster"""
        try:
            from ui.advanced_search import AdvancedSearchDialog
            dialog = AdvancedSearchDialog(
                parent=self.winfo_toplevel(),
                app_instance=self.app_instance
            )
            dialog.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Gelişmiş arama henüz mevcut değil")
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        self.app_instance.show_settings()
    
    def show_notifications(self):
        """Bildirimleri göster"""
        try:
            from ui.notifications import NotificationPanel
            panel = NotificationPanel(
                parent=self.winfo_toplevel(),
                app_instance=self.app_instance
            )
            panel.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Bildirimler henüz mevcut değil")
    
    def show_profile_menu(self):
        """Profil menüsünü göster"""
        # Popup menü oluştur
        popup = tk.Menu(self, tearoff=0)
        popup.add_command(label="Kullanıcı Ayarları", command=self.show_user_settings)
        popup.add_command(label="İstatistikler", command=self.show_statistics)
        popup.add_separator()
        popup.add_command(label="Hakkında", command=self.show_about)
        
        # Menüyü göster
        try:
            popup.tk_popup(self.winfo_rootx() + 50, self.winfo_rooty() + 50)
        finally:
            popup.grab_release()
    
    # Animation Methods
    def animate_theme_transition(self, new_theme):
        """Tema geçiş animasyonu"""
        # Fade out - fade in efekti
        steps = 10
        for i in range(steps):
            alpha = 1.0 - (i / steps)
            self.after(i * 50, lambda a=alpha: self.set_alpha(a))
        
        # Yeni temayı uygula
        self.after(steps * 50, lambda: self.apply_theme(new_theme))
        
        # Fade in
        for i in range(steps):
            alpha = i / steps
            self.after((steps + i) * 50, lambda a=alpha: self.set_alpha(a))
    
    def animate_search_focus(self):
        """Arama odaklanma animasyonu"""
        # Search bar'ı büyüt
        pass
    
    def animate_search_blur(self):
        """Arama odak kaybı animasyonu"""
        # Search bar'ı küçült
        pass
    
    def set_alpha(self, alpha):
        """Widget şeffaflığını ayarla"""
        # Tkinter'da limited alpha desteği
        pass
    
    # Utility Methods
    def apply_theme(self, theme_id):
        """Tema uygula"""
        self.current_theme = theme_id
        self.theme_manager.apply_theme(theme_id, self.winfo_toplevel())
        
        # Logo renklerini güncelle
        self.create_animated_logo()
    
    def apply_current_theme(self):
        """Mevcut temayı uygula"""
        self.apply_theme(self.current_theme)
    
    def update_active_theme_button(self):
        """Aktif tema butonunu güncelle"""
        for theme_id, button in self.theme_buttons.items():
            if theme_id == self.current_theme:
                button.configure(style=f'ActiveTheme{theme_id.title()}.TButton')
            else:
                button.configure(style=f'Theme{theme_id.title()}.TButton')
    
    def get_text(self, key, default=""):
        """Çeviri metnini al"""
        # Basit çeviri sistemi
        translations = {
            'tr': {
                'search_placeholder': 'PDF içinde ara...',
                'settings': 'Ayarlar',
                'notifications': 'Bildirimler',
                'profile': 'Profil'
            },
            'en': {
                'search_placeholder': 'Search in PDF...',
                'settings': 'Settings',
                'notifications': 'Notifications',
                'profile': 'Profile'
            }
        }
        
        lang_dict = translations.get(self.current_language, translations['en'])
        return lang_dict.get(key, default)
    
    def update_ui_texts(self):
        """UI metinlerini güncelle"""
        # Placeholder'ı güncelle
        self.setup_search_placeholder()
    
    def show_user_settings(self):
        """Kullanıcı ayarları"""
        messagebox.showinfo("Bilgi", "Kullanıcı ayarları henüz mevcut değil")
    
    def show_statistics(self):
        """İstatistikleri göster"""
        messagebox.showinfo("Bilgi", "İstatistikler henüz mevcut değil")
    
    def show_about(self):
        """Hakkında penceresini göster"""
        about_text = f"""
        PyPDF-Stirling Tools v2.0
        
        Modern PDF İşleme Uygulaması
        Fatih Bucaklıoğlu tarafından geliştirildi
        
        Bu uygulama modern GUI tasarımı ile
        güçlü PDF işleme yeteneklerini birleştirir.
        """
        messagebox.showinfo("Hakkında", about_text)
    
    def destroy(self):
        """Cleanup işlemleri"""
        self.animation_running = False
        super().destroy()