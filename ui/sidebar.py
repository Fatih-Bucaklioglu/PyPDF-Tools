#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Modern Animasyonlu Sidebar Bileşeni
"""

import tkinter as tk
from tkinter import ttk
import math
import threading
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass

@dataclass
class MenuItem:
    """Menü öğesi veri sınıfı"""
    id: str
    title: str
    icon: str
    category: str
    action: Callable
    tooltip: str = ""
    badge: str = ""
    enabled: bool = True

class ModernSidebar(ttk.Frame):
    """
    Modern animasyonlu sidebar bileşeni
    Performans optimize edilmiş, göze hitap eden animasyonlar
    """
    
    def __init__(self, parent, config_manager, theme_manager, app_instance):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.app_instance = app_instance
        
        # Sidebar durumu
        self.current_category = 'basic'
        self.active_item = None
        self.is_collapsed = False
        self.animation_running = False
        
        # Animasyon parametreleri
        self.animation_duration = 300  # ms
        self.animation_fps = 60
        self.hover_animation_duration = 200
        
        # UI elemanları
        self.menu_items = {}
        self.category_frames = {}
        self.item_buttons = {}
        
        # Animasyon state
        self.animation_queue = []
        self.hover_states = {}
        
        self.create_sidebar()
        self.create_menu_items()
        self.setup_animations()
    
    def create_sidebar(self):
        """Sidebar'ı oluştur"""
        self.configure(style='Sidebar.TFrame', width=280)
        self.pack_propagate(False)
        
        # Ana container
        self.main_container = ttk.Frame(self, style='SidebarContainer.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Üst bölüm - Hızlı erişim
        self.create_quick_access()
        
        # Orta bölüm - Ana menü
        self.create_main_menu()
        
        # Alt bölüm - Araçlar ve ayarlar
        self.create_bottom_section()
    
    def create_quick_access(self):
        """Hızlı erişim bölümünü oluştur"""
        quick_frame = ttk.Frame(self.main_container, style='QuickAccess.TFrame')
        quick_frame.pack(fill=tk.X, padx=15, pady=(20, 10))
        
        # Başlık
        title_label = ttk.Label(
            quick_frame,
            text="Hızlı Erişim",
            style='SectionTitle.TLabel'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Hızlı erişim butonları
        quick_buttons_frame = ttk.Frame(quick_frame, style='QuickButtons.TFrame')
        quick_buttons_frame.pack(fill=tk.X)
        
        quick_actions = [
            ('merge', '🔗', 'Birleştir', self.quick_merge),
            ('split', '✂️', 'Böl', self.quick_split),
            ('compress', '🗜️', 'Sıkıştır', self.quick_compress),
            ('convert', '🔄', 'Dönüştür', self.quick_convert)
        ]
        
        for i, (action_id, icon, text, command) in enumerate(quick_actions):
            btn = self.create_quick_button(
                quick_buttons_frame, action_id, icon, text, command
            )
            
            # 2x2 grid layout
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Grid yapılandırması
        quick_buttons_frame.columnconfigure(0, weight=1)
        quick_buttons_frame.columnconfigure(1, weight=1)
    
    def create_quick_button(self, parent, action_id, icon, text, command):
        """Hızlı erişim butonu oluştur"""
        btn_frame = ttk.Frame(parent, style='QuickButtonFrame.TFrame')
        
        # Buton
        btn = ttk.Button(
            btn_frame,
            style='QuickAction.TButton',
            command=command
        )
        btn.pack(fill=tk.BOTH, expand=True)
        
        # İkon ve metin
        content_frame = ttk.Frame(btn, style='QuickButtonContent.TFrame')
        content_frame.pack(expand=True)
        
        icon_label = ttk.Label(
            content_frame,
            text=icon,
            style='QuickIcon.TLabel'
        )
        icon_label.pack(pady=(5, 2))
        
        text_label = ttk.Label(
            content_frame,
            text=text,
            style='QuickText.TLabel'
        )
        text_label.pack(pady=(0, 5))
        
        # Hover animasyonu ekle
        self.add_quick_button_animation(btn, action_id)
        
        return btn_frame
    
    def create_main_menu(self):
        """Ana menüyü oluştur"""
        menu_frame = ttk.Frame(self.main_container, style='MainMenu.TFrame')
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollable frame oluştur
        self.create_scrollable_menu(menu_frame)
        
        # Kategorileri oluştur
        self.create_menu_categories()
    
    def create_scrollable_menu(self, parent):
        """Kaydırılabilir menü oluştur"""
        # Canvas ve scrollbar
        self.menu_canvas = tk.Canvas(
            parent,
            highlightthickness=0,
            relief='flat'
        )
        
        self.menu_scrollbar = ttk.Scrollbar(
            parent,
            orient='vertical',
            command=self.menu_canvas.yview,
            style='MenuScrollbar.Vertical.TScrollbar'
        )
        
        self.scrollable_frame = ttk.Frame(self.menu_canvas, style='ScrollableMenu.TFrame')
        
        # Layout
        self.menu_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.menu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas konfigürasyonu
        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)
        
        # Scrollable frame'i canvas'a bind et
        canvas_frame = self.menu_canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor='nw'
        )
        
        # Scroll bölgesi güncelleme
        def configure_scroll_region(event):
            self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox('all'))
            
        def configure_canvas_width(event):
            canvas_width = event.width
            self.menu_canvas.itemconfig(canvas_frame, width=canvas_width)
        
        self.scrollable_frame.bind('<Configure>', configure_scroll_region)
        self.menu_canvas.bind('<Configure>', configure_canvas_width)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.menu_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.menu_canvas.bind("<MouseWheel>", on_mousewheel)
    
    def create_menu_categories(self):
        """Menü kategorilerini oluştur"""
        categories = [
            {
                'id': 'basic',
                'title': 'Temel İşlemler',
                'items': [
                    MenuItem('merge', 'PDF Birleştir', '🔗', 'basic', self.merge_pdfs, 'Birden fazla PDF dosyasını birleştir'),
                    MenuItem('split', 'PDF Böl', '✂️', 'basic', self.split_pdf, 'PDF dosyasını sayfalara böl'),
                    MenuItem('rotate', 'Sayfa Döndür', '🔄', 'basic', self.rotate_pages, 'PDF sayfalarını döndür'),
                    MenuItem('reorder', 'Sayfa Düzenle', '📄', 'basic', self.reorder_pages, 'Sayfa sırasını değiştir'),
                    MenuItem('extract_pages', 'Sayfa Çıkar', '📤', 'basic', self.extract_pages, 'Belirli sayfaları çıkar')
                ]
            },
            {
                'id': 'conversion',
                'title': 'Dönüştürme',
                'items': [
                    MenuItem('to_pdf', 'PDF\'e Dönüştür', '📥', 'conversion', self.convert_to_pdf, 'Dosyaları PDF formatına dönüştür'),
                    MenuItem('from_pdf', 'PDF\'den Dönüştür', '📤', 'conversion', self.convert_from_pdf, 'PDF\'i diğer formatlara dönüştür'),
                    MenuItem('images_to_pdf', 'Resim → PDF', '🖼️', 'conversion', self.images_to_pdf, 'Resimleri PDF\'e dönüştür'),
                    MenuItem('pdf_to_images', 'PDF → Resim', '🖼️', 'conversion', self.pdf_to_images, 'PDF\'i resimlere dönüştür')
                ]
            },
            {
                'id': 'optimization',
                'title': 'Optimizasyon',
                'items': [
                    MenuItem('compress', 'Sıkıştır', '🗜️', 'optimization', self.compress_pdf, 'PDF boyutunu küçült'),
                    MenuItem('optimize', 'Optimize Et', '⚡', 'optimization', self.optimize_pdf, 'PDF performansını artır'),
                    MenuItem('clean', 'Temizle', '🧹', 'optimization', self.clean_pdf, 'Gereksiz verileri kaldır'),
                    MenuItem('repair', 'Onar', '🔧', 'optimization', self.repair_pdf, 'Bozuk PDF\'leri onar')
                ]
            },
            {
                'id': 'security',
                'title': 'Güvenlik',
                'items': [
                    MenuItem('encrypt', 'Şifrele', '🔐', 'security', self.encrypt_pdf, 'PDF\'e şifre koy'),
                    MenuItem('decrypt', 'Şifre Kaldır', '🔓', 'security', self.decrypt_pdf, 'PDF şifresini kaldır'),
                    MenuItem('sign', 'Dijital İmza', '✍️', 'security', self.sign_pdf, 'PDF\'i dijital olarak imzala'),
                    MenuItem('verify', 'İmza Doğrula', '✅', 'security', self.verify_signature, 'Dijital imzayı doğrula'),
                    MenuItem('permissions', 'İzinler', '🛡️', 'security', self.set_permissions, 'PDF izinlerini ayarla')
                ]
            },
            {
                'id': 'editing',
                'title': 'Düzenleme',
                'items': [
                    MenuItem('watermark', 'Filigran Ekle', '💧', 'editing', self.add_watermark, 'Metin/resim filigranı ekle'),
                    MenuItem('text_add', 'Metin Ekle', '📝', 'editing', self.add_text, 'PDF\'e metin ekle'),
                    MenuItem('image_add', 'Resim Ekle', '🖼️', 'editing', self.add_image, 'PDF\'e resim ekle'),
                    MenuItem('page_numbers', 'Sayfa No', '#️⃣', 'editing', self.add_page_numbers, 'Sayfa numarası ekle'),
                    MenuItem('header_footer', 'Üstbilgi/Altbilgi', '📋', 'editing', self.add_header_footer, 'Üstbilgi ve altbilgi ekle')
                ]
            },
            {
                'id': 'extraction',
                'title': 'Çıkarma',
                'items': [
                    MenuItem('extract_text', 'Metin Çıkar', '📄', 'extraction', self.extract_text, 'PDF\'den metin çıkar'),
                    MenuItem('extract_images', 'Resim Çıkar', '🖼️', 'extraction', self.extract_images, 'PDF\'den resimleri çıkar'),
                    MenuItem('extract_metadata', 'Metadata', '📊', 'extraction', self.extract_metadata, 'PDF metadata bilgilerini çıkar')
                ]
            },
            {
                'id': 'ocr',
                'title': 'OCR İşlemleri',
                'items': [
                    MenuItem('ocr_process', 'OCR Uygula', '👁️', 'ocr', self.apply_ocr, 'Taranmış PDF\'leri aranabilir hale getir'),
                    MenuItem('ocr_languages', 'Dil Paketleri', '🌍', 'ocr', self.manage_ocr_languages, 'OCR dil paketlerini yönet'),
                    MenuItem('text_search', 'Metin Ara', '🔍', 'ocr', self.search_text, 'PDF içinde metin ara')
                ]
            },
            {
                'id': 'advanced',
                'title': 'Gelişmiş',
                'items': [
                    MenuItem('compare', 'Karşılaştır', '⚖️', 'advanced', self.compare_pdfs, 'İki PDF\'i karşılaştır'),
                    MenuItem('validate', 'Doğrula', '✔️', 'advanced', self.validate_pdf, 'PDF formatını doğrula'),
                    MenuItem('batch', 'Toplu İşlem', '📦', 'advanced', self.batch_process, 'Birden fazla dosyayı işle'),
                    MenuItem('automation', 'Otomasyon', '🤖', 'advanced', self.show_automation, 'Otomatik işlemler ayarla'),
                    MenuItem('scripts', 'Scriptler', '📜', 'advanced', self.show_scripts, 'Kendi scriptlerinizi yazın')
                ]
            }
        ]
        
        # Kategorileri oluştur
        for category in categories:
            self.create_category_section(category)
    
    def create_category_section(self, category):
        """Kategori bölümü oluştur"""
        category_id = category['id']
        
        # Kategori frame
        category_frame = ttk.Frame(self.scrollable_frame, style='CategoryFrame.TFrame')
        category_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.category_frames[category_id] = category_frame
        
        # Kategori başlığı
        header_frame = ttk.Frame(category_frame, style='CategoryHeader.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Collapse/Expand butonu
        collapse_btn = ttk.Button(
            header_frame,
            text="▼",
            style='CollapseButton.TButton',
            width=3,
            command=lambda: self.toggle_category(category_id)
        )
        collapse_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Başlık
        title_label = ttk.Label(
            header_frame,
            text=category['title'],
            style='CategoryTitle.TLabel'
        )
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # İtemler frame
        items_frame = ttk.Frame(category_frame, style='CategoryItems.TFrame')
        items_frame.pack(fill=tk.X)
        
        # Menü itemlerini oluştur
        for item in category['items']:
            self.create_menu_item(items_frame, item)
        
        # Kategori durumunu sakla
        self.category_frames[category_id] = {
            'frame': category_frame,
            'items_frame': items_frame,
            'collapse_btn': collapse_btn,
            'collapsed': False
        }
    
    def create_menu_item(self, parent, menu_item: MenuItem):
        """Menü öğesi oluştur"""
        item_frame = ttk.Frame(parent, style='MenuItem.TFrame')
        item_frame.pack(fill=tk.X, pady=1)
        
        # Menü butonu
        btn = ttk.Button(
            item_frame,
            style='MenuButton.TButton',
            command=menu_item.action
        )
        btn.pack(fill=tk.X, padx=(20, 0))
        
        # Buton içeriği
        content_frame = ttk.Frame(btn, style='MenuButtonContent.TFrame')
        content_frame.pack(fill=tk.X, expand=True, padx=10, pady=8)
        
        # Sol taraf - İkon ve başlık
        left_frame = ttk.Frame(content_frame, style='MenuButtonLeft.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İkon
        icon_label = ttk.Label(
            left_frame,
            text=menu_item.icon,
            style='MenuIcon.TLabel'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Başlık
        title_label = ttk.Label(
            left_frame,
            text=menu_item.title,
            style='MenuTitle.TLabel'
        )
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # Sağ taraf - Badge ve ok
        right_frame = ttk.Frame(content_frame, style='MenuButtonRight.TFrame')
        right_frame.pack(side=tk.RIGHT)
        
        # Badge (varsa)
        if menu_item.badge:
            badge_label = ttk.Label(
                right_frame,
                text=menu_item.badge,
                style='MenuBadge.TLabel'
            )
            badge_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Ok ikonu
        arrow_label = ttk.Label(
            right_frame,
            text="→",
            style='MenuArrow.TLabel'
        )
        arrow_label.pack(side=tk.RIGHT)
        
        # Menü öğesini sakla
        self.item_buttons[menu_item.id] = {
            'button': btn,
            'frame': item_frame,
            'menu_item': menu_item
        }
        
        # Animasyon ve etkileşimler ekle
        self.setup_menu_item_interactions(btn, menu_item)
        
        return item_frame
    
    def setup_menu_item_interactions(self, button, menu_item):
        """Menü öğesi etkileşimlerini ayarla"""
        # Hover animasyonu
        self.add_menu_item_hover(button, menu_item.id)
        
        # Tooltip
        if menu_item.tooltip:
            self.add_tooltip(button, menu_item.tooltip)
        
        # Keyboard navigation
        button.bind('<Return>', lambda e: menu_item.action())
        button.bind('<space>', lambda e: menu_item.action())
    
    def create_bottom_section(self):
        """Alt bölümü oluştur"""
        bottom_frame = ttk.Frame(self.main_container, style='BottomSection.TFrame')
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(10, 20))
        
        # Ayırıcı
        separator = ttk.Separator(bottom_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Araçlar
        tools_frame = ttk.Frame(bottom_frame, style='ToolsFrame.TFrame')
        tools_frame.pack(fill=tk.X)
        
        tools = [
            ('pdf_viewer', '📖', 'PDF Okuyucu', self.open_pdf_viewer),
            ('settings', '⚙️', 'Ayarlar', self.open_settings),
            ('help', '❓', 'Yardım', self.show_help)
        ]
        
        for tool_id, icon, title, command in tools:
            tool_btn = ttk.Button(
                tools_frame,
                text=f"{icon} {title}",
                style='ToolButton.TButton',
                command=command
            )
            tool_btn.pack(fill=tk.X, pady=2)
            
            self.add_tool_button_animation(tool_btn, tool_id)
        
        # Sürüm bilgisi
        version_label = ttk.Label(
            bottom_frame,
            text="v2.0.0",
            style='VersionLabel.TLabel'
        )
        version_label.pack(pady=(15, 0))
    
    def setup_animations(self):
        """Animasyon sistemini ayarla"""
        self.animation_active = True
        self.animation_thread_pool = []
    
    # Animation Methods
    def add_quick_button_animation(self, button, action_id):
        """Hızlı erişim butonu animasyonu"""
        original_bg = button.cget('style')
        
        def on_enter(event):
            if not self.animation_running:
                self.animate_button_hover(button, 'enter')
        
        def on_leave(event):
            if not self.animation_running:
                self.animate_button_hover(button, 'leave')
        
        def on_click(event):
            self.animate_button_click(button)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        button.bind('<Button-1>', on_click)
    
    def add_menu_item_hover(self, button, item_id):
        """Menü öğesi hover animasyonu"""
        def on_enter(event):
            self.animate_menu_item_hover(item_id, True)
            self.set_active_item(item_id)
        
        def on_leave(event):
            self.animate_menu_item_hover(item_id, False)
            if self.active_item == item_id:
                self.set_active_item(None)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    def add_tool_button_animation(self, button, tool_id):
        """Araç butonu animasyonu"""
        def on_enter(event):
            self.animate_tool_button(button, 'hover')
        
        def on_leave(event):
            self.animate_tool_button(button, 'normal')
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    def animate_button_hover(self, button, direction):
        """Buton hover animasyonu"""
        if direction == 'enter':
            # Hafif büyütme ve renk değişimi
            self.animate_scale(button, 1.0, 1.02, 100)
        else:
            # Normal boyuta dön
            self.animate_scale(button, 1.02, 1.0, 100)
    
    def animate_button_click(self, button):
        """Buton tıklama animasyonu"""
        # Tıklama efekti - küçült ve büyüt
        self.animate_scale(button, 1.0, 0.95, 50)
        button.after(50, lambda: self.animate_scale(button, 0.95, 1.0, 50))
    
    def animate_menu_item_hover(self, item_id, is_hover):
        """Menü öğesi hover animasyonu"""
        if item_id in self.item_buttons:
            button = self.item_buttons[item_id]['button']
            
            if is_hover:
                # Hover durumu
                button.configure(style='MenuButtonHover.TButton')
                self.animate_slide_in_arrow(item_id)
            else:
                # Normal durum
                button.configure(style='MenuButton.TButton')
                self.animate_slide_out_arrow(item_id)
    
    def animate_tool_button(self, button, state):
        """Araç butonu animasyonu"""
        if state == 'hover':
            button.configure(style='ToolButtonHover.TButton')
        else:
            button.configure(style='ToolButton.TButton')
    
    def animate_scale(self, widget, start_scale, end_scale, duration):
        """Widget ölçeklendirme animasyonu"""
        steps = duration // (1000 // self.animation_fps)
        if steps == 0:
            steps = 1
        
        def update_scale(step):
            if step <= steps:
                progress = step / steps
                current_scale = start_scale + (end_scale - start_scale) * progress
                
                # Ölçeklendirme simülasyonu (Tkinter'da limited)
                # Gerçek uygulamada custom widget veya PIL kullanılabilir
                
                widget.after(1000 // self.animation_fps, lambda: update_scale(step + 1))
        
        update_scale(0)
    
    def animate_slide_in_arrow(self, item_id):
        """Ok ikonu kayma animasyonu - giriş"""
        # Arrow slide animasyonu simülasyonu
        pass
    
    def animate_slide_out_arrow(self, item_id):
        """Ok ikonu kayma animasyonu - çıkış"""
        # Arrow slide animasyonu simülasyonu
        pass
    
    def toggle_category(self, category_id):
        """Kategori daralt/genişlet"""
        if category_id in self.category_frames:
            category_info = self.category_frames[category_id]
            items_frame = category_info['items_frame']
            collapse_btn = category_info['collapse_btn']
            
            if category_info['collapsed']:
                # Genişlet
                items_frame.pack(fill=tk.X)
                collapse_btn.configure(text="▼")
                category_info['collapsed'] = False
                self.animate_category_expand(items_frame)
            else:
                # Daralt
                self.animate_category_collapse(items_frame)
                items_frame.pack_forget()
                collapse_btn.configure(text="▶")
                category_info['collapsed'] = True
    
    def animate_category_expand(self, frame):
        """Kategori genişletme animasyonu"""
        # Yükseklik animasyonu simülasyonu
        frame.configure(height=1)
        
        def expand_step(current_height):
            if current_height < 200:  # Hedef yükseklik
                frame.configure(height=current_height + 10)
                frame.after(20, lambda: expand_step(current_height + 10))
            else:
                frame.configure(height='')  # Auto height
        
        expand_step(1)
    
    def animate_category_collapse(self, frame):
        """Kategori daraltma animasyonu"""
        current_height = frame.winfo_reqheight()
        
        def collapse_step(height):
            if height > 0:
                frame.configure(height=height)
                frame.after(20, lambda: collapse_step(height - 10))
        
        collapse_step(current_height)
    
    # Utility Methods
    def set_active_item(self, item_id):
        """Aktif menü öğesini ayarla"""
        self.active_item = item_id
    
    def add_tooltip(self, widget, text):
        """Tooltip ekle"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(background='yellow')
            
            label = ttk.Label(
                tooltip,
                text=text,
                background='yellow',
                relief='solid',
                borderwidth=1,
                wraplength=200
            )
            label.pack()
            
            # 3 saniye sonra gizle
            tooltip.after(3000, tooltip.destroy)
        
        def hide_tooltip(event):
            pass
        
        widget.bind('<Enter>', show_tooltip)
    
    def configure_for_small_screen(self):
        """Küçük ekran için yapılandır"""
        self.configure(width=60)  # Collapsed width
        self.is_collapsed = True
        
        # Sadece ikonları göster
        for item_id, item_info in self.item_buttons.items():
            button = item_info['button']
            # Buton metnini gizle, sadece ikonu göster
            # Bu özellik custom widget gerektirir
    
    def configure_for_large_screen(self):
        """Büyük ekran için yapılandır"""
        self.configure(width=280)  # Normal width
        self.is_collapsed = False
        
        # Tam menüyü göster
        for item_id, item_info in self.item_buttons.items():
            button = item_info['button']
            # Buton metnini göster
    
    # Action Methods (Bu metodlar content sınıfına delegate edilecek)
    def quick_merge(self):
        """Hızlı birleştirme"""
        self.app_instance.content.set_operation('merge')
    
    def quick_split(self):
        """Hızlı bölme"""
        self.app_instance.content.set_operation('split')
    
    def quick_compress(self):
        """Hızlı sıkıştırma"""
        self.app_instance.content.set_operation('compress')
    
    def quick_convert(self):
        """Hızlı dönüştürme"""
        self.app_instance.content.set_operation('convert')
    
    # PDF Operations
    def merge_pdfs(self):
        self.app_instance.content.set_operation('merge')
    
    def split_pdf(self):
        self.app_instance.content.set_operation('split')
    
    def rotate_pages(self):
        self.app_instance.content.set_operation('rotate')
    
    def reorder_pages(self):
        self.app_instance.content.set_operation('reorder')
    
    def extract_pages(self):
        self.app_instance.content.set_operation('extract_pages')
    
    def convert_to_pdf(self):
        self.app_instance.content.set_operation('to_pdf')
    
    def convert_from_pdf(self):
        self.app_instance.content.set_operation('from_pdf')
    
    def images_to_pdf(self):
        self.app_instance.content.set_operation('images_to_pdf')
    
    def pdf_to_images(self):
        self.app_instance.content.set_operation('pdf_to_images')
    
    def compress_pdf(self):
        self.app_instance.content.set_operation('compress')
    
    def optimize_pdf(self):
        self.app_instance.content.set_operation('optimize')
    
    def clean_pdf(self):
        self.app_instance.content.set_operation('clean')
    
    def repair_pdf(self):
        self.app_instance.content.set_operation('repair')
    
    def encrypt_pdf(self):
        self.app_instance.content.set_operation('encrypt')
    
    def decrypt_pdf(self):
        self.app_instance.content.set_operation('decrypt')
    
    def sign_pdf(self):
        self.app_instance.content.set_operation('sign')
    
    def verify_signature(self):
        self.app_instance.content.set_operation('verify')
    
    def set_permissions(self):
        self.app_instance.content.set_operation('permissions')
    
    def add_watermark(self):
        self.app_instance.content.set_operation('watermark')
    
    def add_text(self):
        self.app_instance.content.set_operation('add_text')
    
    def add_image(self):
        self.app_instance.content.set_operation('add_image')
    
    def add_page_numbers(self):
        self.app_instance.content.set_operation('page_numbers')
    
    def add_header_footer(self):
        self.app_instance.content.set_operation('header_footer')
    
    def extract_text(self):
        self.app_instance.content.set_operation('extract_text')
    
    def extract_images(self):
        self.app_instance.content.set_operation('extract_images')
    
    def extract_metadata(self):
        self.app_instance.content.set_operation('extract_metadata')
    
    def apply_ocr(self):
        self.app_instance.content.set_operation('ocr')
    
    def manage_ocr_languages(self):
        self.app_instance.content.show_ocr_language_manager()
    
    def search_text(self):
        self.app_instance.content.set_operation('search')
    
    def compare_pdfs(self):
        self.app_instance.content.set_operation('compare')
    
    def validate_pdf(self):
        self.app_instance.content.set_operation('validate')
    
    def batch_process(self):
        self.app_instance.content.set_operation('batch')
    
    def show_automation(self):
        self.app_instance.content.show_automation_panel()
    
    def show_scripts(self):
        self.app_instance.content.show_script_editor()
    
    def open_pdf_viewer(self):
        """PDF okuyucuyu aç"""
        try:
            self.app_instance.pdf_viewer.show()
        except Exception as e:
            tk.messagebox.showerror("Hata", f"PDF okuyucu açılamadı: {e}")
    
    def open_settings(self):
        """Ayarlar penceresini aç"""
        self.app_instance.show_settings()
    
    def show_help(self):
        """Yardım penceresini göster"""
        self.app_instance.show_help()
    
    def cleanup(self):
        """Temizlik işlemleri"""
        self.animation_active = False
        # Animation thread'leri durdur
        for thread in self.animation_thread_pool:
            if thread.is_alive():
                thread.join(timeout=1)