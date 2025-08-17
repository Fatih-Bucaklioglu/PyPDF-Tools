def create_content_area(self):
        """Content area'yı oluştur"""
        self.configure(style='Content.TFrame')
        
        # Ana container
        main_container = ttk.Frame(self, style='ContentContainer.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Üst bölüm - Drop zone ve file list
        self.create_upper_section(main_container)
        
        # Orta bölüm - Options panel
        self.create_middle_section(main_container)
        
        # Alt bölüm - Progress ve results
        self.create_lower_section(main_container)
        
        # Varsayılan görünümü ayarla
        self.show_welcome_view()
    
    def create_upper_section(self, parent):
        """Üst bölüm oluştur"""
        upper_frame = ttk.Frame(parent, style='UpperSection.TFrame')
        upper_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Drop zone
        self.create_drop_zone(upper_frame)
        
        # File list (başlangıçta gizli)
        self.create_file_list(upper_frame)
    
    def create_drop_zone(self, parent):
        """Dosya sürükle-bırak alanı oluştur"""
        self.drop_zone = ttk.Frame(parent, style='DropZone.TFrame')
        self.drop_zone.pack(fill=tk.BOTH, expand=True)
        
        # Drop zone içeriği
        drop_content = ttk.Frame(self.drop_zone, style='DropZoneContent.TFrame')
        drop_content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Drop ikonu
        self.drop_icon = tk.Canvas(
            drop_content,
            width=64,
            height=64,
            highlightthickness=0,
            relief='flat'
        )
        self.drop_icon.pack(pady=(0, 16))
        
        self.create_drop_icon()
        
        # Ana mesaj
        self.drop_title = ttk.Label(
            drop_content,
            text="PDF dosyalarınızı buraya sürükleyin",
            style='DropTitle.TLabel'
        )
        self.drop_title.pack(pady=(0, 8))
        
        # Alt mesaj
        self.drop_subtitle = ttk.Label(
            drop_content,
            text="veya dosya seçmek için tıklayın",
            style='DropSubtitle.TLabel'
        )
        self.drop_subtitle.pack(pady=(0, 20))
        
        # Dosya seçme butonu
        select_btn = ttk.Button(
            drop_content,
            text="📁 Dosya Seç",
            style='SelectFile.TButton',
            command=self.open_files_dialog
        )
        select_btn.pack(pady=(0, 10))
        
        # Desteklenen formatlar
        formats_label = ttk.Label(
            drop_content,
            text="Desteklenen: PDF, DOC, DOCX, JPG, PNG, TIFF",
            style='FormatsLabel.TLabel'
        )
        formats_label.pack()
        
        # Drop zone tıklama olayı
        self.drop_zone.bind('<Button-1>', lambda e: self.open_files_dialog())
        self.add_drop_zone_bindings()
    
    def create_drop_icon(self):
        """Drop ikonu oluştur"""
        self.drop_icon.delete("all")
        
        # Animasyonlu dosya ikonu
        # Dış çerçeve
        self.drop_icon.create_rectangle(
            16, 20, 48, 56,
            outline='#3b82f6',
            width=2,
            fill='',
            tags='file_outline'
        )
        
        # Dosya köşesi
        self.drop_icon.create_polygon(
            38, 20, 48, 30, 38, 30,
            outline='#3b82f6',
            fill='#dbeafe',
            width=2,
            tags='file_corner'
        )
        
        # İç çizgiler
        for i, y in enumerate([35, 40, 45]):
            self.drop_icon.create_line(
                22, y, 42, y,
                fill='#3b82f6',
                width=1,
                tags=f'file_line_{i}'
            )
        
        # Animasyon başlat
        self.animate_drop_icon()
    
    def animate_drop_icon(self):
        """Drop ikonu animasyonu"""
        def pulse():
            # Pulse efekti
            for scale in [1.0, 1.1, 1.0]:
                self.drop_icon.after(500, lambda s=scale: self.scale_drop_icon(s))
        
        # 3 saniyede bir tekrarla
        self.drop_icon.after(3000, pulse)
        pulse()
    
    def scale_drop_icon(self, scale):
        """Drop ikonu ölçeklendir"""
        try:
            self.drop_icon.scale("all", 32, 32, scale, scale)
        except tk.TclError:
            pass
    
    def add_drop_zone_bindings(self):
        """Drop zone olayları ekle"""
        # Drag enter
        def on_drag_enter(event):
            self.drop_zone.configure(style='DropZoneHover.TFrame')
            self.animate_drop_zone_enter()
        
        # Drag leave
        def on_drag_leave(event):
            self.drop_zone.configure(style='DropZone.TFrame')
            self.animate_drop_zone_leave()
        
        # Drop
        def on_drop(event):
            files = event.data.split(' ')
            self.handle_dropped_files(files)
        
        # Mouse enter/leave
        self.drop_zone.bind('<Enter>', on_drag_enter)
        self.drop_zone.bind('<Leave>', on_drag_leave)
        
        # Drag and drop bindings (tkinterdnd2 gerekli)
        try:
            self.drop_zone.drop_target_register('DND_Files')
            self.drop_zone.dnd_bind('<<DropEnter>>', on_drag_enter)
            self.drop_zone.dnd_bind('<<DropLeave>>', on_drag_leave)
            self.drop_zone.dnd_bind('<<Drop>>', on_drop)
        except:
            pass  # DnD desteklenmiyorsa sessizce geç
    
    def create_file_list(self, parent):
        """Dosya listesi oluştur"""
        self.file_list_frame = ttk.Frame(parent, style='FileList.TFrame')
        # Başlangıçta gizli
        
        # Başlık
        list_header = ttk.Frame(self.file_list_frame, style='FileListHeader.TFrame')
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            list_header,
            text="Seçilen Dosyalar",
            style='FileListTitle.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Temizle butonu
        clear_btn = ttk.Button(
            list_header,
            text="🗑️ Temizle",
            style='ClearFiles.TButton',
            command=self.clear_files
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Dosya ekleme butonu
        add_btn = ttk.Button(
            list_header,
            text="➕ Dosya Ekle",
            style='AddFiles.TButton',
            command=self.open_files_dialog
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Scrollable dosya listesi
        self.create_scrollable_file_list()
    
    def create_scrollable_file_list(self):
        """Kaydırılabilir dosya listesi"""
        # Frame ve scrollbar
        list_container = ttk.Frame(self.file_list_frame, style='FileListContainer.TFrame')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve scrollbar
        self.files_canvas = tk.Canvas(
            list_container,
            highlightthickness=0,
            relief='flat',
            height=200
        )
        
        files_scrollbar = ttk.Scrollbar(
            list_container,
            orient='vertical',
            command=self.files_canvas.yview
        )
        
        self.files_scrollable_frame = ttk.Frame(self.files_canvas)
        
        # Layout
        self.files_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas ayarları
        self.files_canvas.configure(yscrollcommand=files_scrollbar.set)
        
        # Scrollable frame'i canvas'a ekle
        canvas_frame = self.files_canvas.create_window(
            (0, 0),
            window=self.files_scrollable_frame,
            anchor='nw'
        )
        
        # Scroll region güncelleme
        def configure_scroll_region(event):
            self.files_canvas.configure(scrollregion=self.files_canvas.bbox('all'))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.files_canvas.itemconfig(canvas_frame, width=canvas_width)
        
        self.files_scrollable_frame.bind('<Configure>', configure_scroll_region)
        self.files_canvas.bind('<Configure>', configure_canvas_width)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.files_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.files_canvas.bind("<MouseWheel>", on_mousewheel)
    
    def create_middle_section(self, parent):
        """Orta bölüm - Options panel"""
        self.options_panel = ttk.Frame(parent, style='OptionsPanel.TFrame')
        # Başlangıçta gizli
        
        # Panel başlığı
        options_header = ttk.Frame(self.options_panel, style='OptionsPanelHeader.TFrame')
        options_header.pack(fill=tk.X, pady=(0, 15))
        
        self.options_title = ttk.Label(
            options_header,
            text="İşlem Ayarları",
            style='OptionsPanelTitle.TLabel'
        )
        self.options_title.pack(side=tk.LEFT)
        
        # İşlem seçici
        operation_frame = ttk.Frame(options_header, style='OperationFrame.TFrame')
        operation_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            operation_frame,
            text="İşlem:",
            style='OperationLabel.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.operation_var = tk.StringVar()
        self.operation_combo = ttk.Combobox(
            operation_frame,
            textvariable=self.operation_var,
            state='readonly',
            style='Operation.TCombobox'
        )
        self.operation_combo.pack(side=tk.LEFT)
        self.operation_combo.bind('<<ComboboxSelected>>', self.on_operation_change)
        
        # Dinamik options container
        self.dynamic_options = ttk.Frame(self.options_panel, style='DynamicOptions.TFrame')
        self.dynamic_options.pack(fill=tk.X, pady=(0, 15))
        
        # Action buttons
        self.create_action_buttons()
    
    def create_action_buttons(self):
        """Aksiyon butonları oluştur"""
        actions_frame = ttk.Frame(self.options_panel, style='ActionsFrame.TFrame')
        actions_frame.pack(fill=tk.X)
        
        # Sol taraf - Output directory
        output_frame = ttk.Frame(actions_frame, style='OutputFrame.TFrame')
        output_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            output_frame,
            text="Çıktı Klasörü:",
            style='OutputLabel.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_var = tk.StringVar()
        self.output_var.set(self.config_manager.get('pdf_processing.output_directory', '~/Desktop'))
        
        output_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_var,
            style='OutputPath.TEntry'
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            output_frame,
            text="📁",
            style='BrowseOutput.TButton',
            width=3,
            command=self.browse_output_directory
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Sağ taraf - Process button
        self.process_btn = ttk.Button(
            actions_frame,
            text="🚀 İşlemi Başlat",
            style='ProcessButton.TButton',
            command=self.start_processing
        )
        self.process_btn.pack(side=tk.RIGHT, padx=(20, 0))
    
    def create_lower_section(self, parent):
        """Alt bölüm - Progress ve results"""
        lower_frame = ttk.Frame(parent, style='LowerSection.TFrame')
        lower_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Progress panel
        self.create_progress_panel(lower_frame)
        
        # Results panel
        self.create_results_panel(lower_frame)
    
    def create_progress_panel(self, parent):
        """Progress panel oluştur"""
        self.progress_panel = ttk.Frame(parent, style='ProgressPanel.TFrame')
        # Başlangıçta gizli
        
        # Progress header
        progress_header = ttk.Frame(self.progress_panel, style='ProgressHeader.TFrame')
        progress_header.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_title = ttk.Label(
            progress_header,
            text="İşlem Durumu",
            style='ProgressTitle.TLabel'
        )
        self.progress_title.pack(side=tk.LEFT)
        
        # Cancel button
        self.cancel_btn = ttk.Button(
            progress_header,
            text="❌ İptal",
            style='CancelButton.TButton',
            command=self.cancel_processing
        )
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Progress bars container
        progress_container = ttk.Frame(self.progress_panel, style='ProgressContainer.TFrame')
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        # Ana progress bar
        self.main_progress_var = tk.DoubleVar()
        self.main_progress = ttk.Progressbar(
            progress_container,
            variable=self.main_progress_var,
            maximum=100,
            style='Main.Horizontal.TProgressbar'
        )
        self.main_progress.pack(fill=tk.X, pady=(0, 5))
        
        # Progress text
        self.progress_text = ttk.Label(
            progress_container,
            text="Hazırlanıyor...",
            style='ProgressText.TLabel'
        )
        self.progress_text.pack(anchor='w')
        
        # Detaylı progress (dosya bazında)
        self.file_progress_frame = ttk.Frame(progress_container, style='FileProgress.TFrame')
        self.file_progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # İstatistikler
        stats_frame = ttk.Frame(self.progress_panel, style='StatsFrame.TFrame')
        stats_frame.pack(fill=tk.X)
        
        self.stats_labels = {}
        stats_items = [
            ('processed', 'İşlenen: 0'),
            ('remaining', 'Kalan: 0'),
            ('errors', 'Hata: 0'),
            ('speed', 'Hız: 0 MB/s'),
            ('eta', 'Tahmini: --:--')
        ]
        
        for stat_id, initial_text in stats_items:
            label = ttk.Label(
                stats_frame,
                text=initial_text,
                style='StatsLabel.TLabel'
            )
            label.pack(side=tk.LEFT, padx=(0, 20))
            self.stats_labels[stat_id] = label
    
    def create_results_panel(self, parent):
        """Results panel oluştur"""
        self.results_panel = ttk.Frame(parent, style='ResultsPanel.TFrame')
        # Başlangıçta gizli
        
        # Results header
        results_header = ttk.Frame(self.results_panel, style='ResultsHeader.TFrame')
        results_header.pack(fill=tk.X, pady=(0, 10))
        
        results_title = ttk.Label(
            results_header,
            text="İşlem Sonuçları",
            style='ResultsTitle.TLabel'
        )
        results_title.pack(side=tk.LEFT)
        
        # Export results button
        export_btn = ttk.Button(
            results_header,
            text="💾 Rapor Kaydet",
            style='ExportResults.TButton',
            command=self.export_results
        )
        export_btn.pack(side=tk.RIGHT)
        
        # Open output folder button
        open_folder_btn = ttk.Button(
            results_header,
            text="📁 Klasörü Aç",
            style='OpenFolder.TButton',
            command=self.open_output_folder
        )
        open_folder_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Results treeview
        self.create_results_treeview()
    
    def create_results_treeview(self):
        """Results treeview oluştur"""
        tree_container = ttk.Frame(self.results_panel, style='TreeContainer.TFrame')
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview ve scrollbar
        self.results_tree = ttk.Treeview(
            tree_container,
            style='Results.Treeview',
            columns=('file', 'operation', 'status', 'size', 'time'),
            show='headings',
            height=8
        )
        
        results_v_scrollbar = ttk.Scrollbar(
            tree_container,
            orient='vertical',
            command=self.results_tree.yview
        )
        
        results_h_scrollbar = ttk.Scrollbar(
            tree_container,
            orient='horizontal',
            command=self.results_tree.xview
        )
        
        # Layout
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        results_v_scrollbar.grid(row=0, column=1, sticky='ns')
        results_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Scrollbar bağlantıları
        self.results_tree.configure(
            yscrollcommand=results_v_scrollbar.set,
            xscrollcommand=results_h_scrollbar.set
        )
        
        # Sütun ayarları
        columns = {
            'file': ('Dosya', 200),
            'operation': ('İşlem', 100),
            'status': ('Durum', 80),
            'size': ('Boyut', 80),
            'time': ('Süre', 80)
        }
        
        for col_id, (heading, width) in columns.items():
            self.results_tree.heading(col_id, text=heading)
            self.results_tree.column(col_id, width=width, minwidth=50)
        
        # Çift tıklama olayı
        self.results_tree.bind('<Double-1>', self.on_result_double_click)
    
    def setup_drag_and_drop(self):
        """Drag and drop sistemi ayarla"""
        try:
            import tkinterdnd2 as tkdnd
            
            # Drop zone'u DnD uyumlu yap
            self.drop_zone.drop_target_register('DND_Files')
            
            def handle_drop(event):
                files = self.parse_drop_data(event.data)
                self.handle_dropped_files(files)
            
            self.drop_zone.dnd_bind('<<Drop>>', handle_drop)
            
        except ImportError:
            # DnD desteği yok, sadece click-to-select
            pass
    
    def parse_drop_data(self, data):
        """Drop data'sını parse et"""
        if isinstance(data, str):
            # Windows ve Unix path'lerini handle et
            if data.startswith('{') and data.endswith('}'):
                # Windows path with spaces
                return [data[1:-1]]
            else:
                # Multiple files or Unix paths
                return data.split()
        return []
    
    def bind_dnd_events(self):
        """DnD eventlerini bind et"""
        # Header'dan çağrılacak
        pass
    
    # Event Handlers
    def animate_drop_zone_enter(self):
        """Drop zone'a girerken animasyon"""
        self.drop_title.configure(text="Dosyaları bırakın!")
        self.animate_drop_icon_hover()
    
    def animate_drop_zone_leave(self):
        """Drop zone'dan çıkarken animasyon"""
        self.drop_title.configure(text="PDF dosyalarınızı buraya sürükleyin")
    
    def animate_drop_icon_hover(self):
        """Drop icon hover animasyonu"""
        # İkonu büyüt
        self.scale_drop_icon(1.2)
        self.drop_zone.after(200, lambda: self.scale_drop_icon(1.0))
    
    def handle_dropped_files(self, files):
        """Bırakılan dosyaları işle"""
        valid_files = []
        
        for file_path in files:
            path = Path(file_path.strip('"\''))
            
            if path.exists() and path.is_file():
                # Desteklenen format kontrolü
                if self.is_supported_file(path):
                    valid_files.append(str(path))
        
        if valid_files:
            self.add_files(valid_files)
        else:
            messagebox.showwarning(
                "Uyarı",
                "Desteklenmeyen dosya formatı!\n\nDesteklenen formatlar:\n" +
                "PDF, DOC, DOCX, JPG, PNG, TIFF, BMP"
            )
    
    def is_supported_file(self, file_path):
        """Dosya formatı destekleniyor mu?"""
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', 
            '.tiff', '.tif', '.bmp', '.gif', '.webp'
        }
        return file_path.suffix.lower() in supported_extensions
    
    def open_files_dialog(self):
        """Dosya seçme diyalogu"""
        filetypes = [
            ('PDF Dosyaları', '*.pdf'),
            ('Word Dosyaları', '*.doc *.docx'),
            ('Resim Dosyaları', '*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif'),
            ('Tüm Dosyalar', '*.*')
        ]
        
        initial_dir = self.config_manager.get('ui.last_open_directory', os.path.expanduser('~'))
        
        files = filedialog.askopenfilenames(
            title="PDF Dosyaları Seçin",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if files:
            # Son açılan dizini kaydet
            last_dir = os.path.dirname(files[0])
            self.config_manager.set('ui.last_open_directory', last_dir)
            self.config_manager.save()
            
            self.add_files(files)
    
    def add_files(self, files):
        """Dosyaları listeye ekle"""
        new_files = []
        
        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                new_files.append(file_path)
        
        if new_files:
            self.update_file_list_display()
            self.show_file_list()
            self.animate_file_addition(len(new_files))
    
    def update_file_list_display(self):
        """Dosya listesi görüntüsünü güncelle"""
        # Mevcut öğeleri temizle
        for widget in self.files_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Her dosya için satır oluştur
        for i, file_path in enumerate(self.selected_files):
            self.create_file_item(self.files_scrollable_frame, file_path, i)
    
    def create_file_item(self, parent, file_path, index):
        """Dosya öğesi oluştur"""
        path = Path(file_path)
        
        # Ana frame
        item_frame = ttk.Frame(parent, style='FileItem.TFrame')
        item_frame.pack(fill=tk.X, pady=2)
        
        # Sol taraf - ikon ve bilgiler
        left_frame = ttk.Frame(item_frame, style='FileItemLeft.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        
        # Dosya ikonu
        icon = self.get_file_icon(path.suffix.lower())
        icon_label = ttk.Label(
            left_frame,
            text=icon,
            style='FileIcon.TLabel'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dosya bilgileri
        info_frame = ttk.Frame(left_frame, style='FileInfo.TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dosya adı
        name_label = ttk.Label(
            info_frame,
            text=path.name,
            style='FileName.TLabel'
        )
        name_label.pack(anchor='w')
        
        # Dosya yolu ve boyutu
        try:
            size = path.stat().st_size
            size_str = self.format_file_size(size)
        except:
            size_str = "Bilinmiyor"
        
        details_text = f"{path.parent} • {size_str}"
        details_label = ttk.Label(
            info_frame,
            text=details_text,
            style='FileDetails.TLabel'
        )
        details_label.pack(anchor='w')
        
        # Sağ taraf - aksiyonlar
        right_frame = ttk.Frame(item_frame, style='FileItemRight.TFrame')
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        # Kaldır butonu
        remove_btn = ttk.Button(
            right_frame,
            text="🗑️",
            style='RemoveFile.TButton',
            width=3,
            command=lambda idx=index: self.remove_file(idx)
        )
        remove_btn.pack(side=tk.RIGHT)
        
        # Önizleme butonu (PDF için)
        if path.suffix.lower() == '.pdf':
            preview_btn = ttk.Button(
                right_frame,
                text="👁️",
                style='PreviewFile.TButton',
                width=3,
                command=lambda fp=file_path: self.preview_file(fp)
            )
            preview_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Hover efekti
        self.add_file_item_hover(item_frame)
    
    def get_file_icon(self, extension):
        """Dosya türüne göre ikon döndür"""
        icons = {
            '.pdf': '📄',
            '.doc': '📝', '.docx': '📝',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
            '.tiff': '🖼️', '.tif': '🖼️', '.bmp': '🖼️',
            '.gif': '🖼️', '.webp': '🖼️'
        }
        return icons.get(extension, '📎')
    
    def format_file_size(self, size):
        """Dosya boyutunu format et"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def add_file_item_hover(self, item_frame):
        """Dosya öğesi hover efekti"""
        original_style = item_frame.cget('style')
        
        def on_enter(event):
            item_frame.configure(style='FileItemHover.TFrame')
        
        def on_leave(event):
            item_frame.configure(style=original_style)
        
        item_frame.bind('<Enter>', on_enter)
        item_frame.bind('<Leave>', on_leave)
        
        # Alt widget'lara da bind et
        for child in item_frame.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
    
    def remove_file(self, index):
        """Dosyayı listeden kaldır"""
        if 0 <= index < len(self.selected_files):
            removed_file = self.selected_files.pop(index)
            self.update_file_list_display()
            
            # Liste boşsa drop zone'u göster
            if not self.selected_files:
                self.show_welcome_view()
    
    def clear_files(self):
        """Tüm dosyaları temizle"""
        self.selected_files.clear()
        self.show_welcome_view()
    
    def preview_file(self, file_path):
        """Dosya önizlemesi göster"""
        try:
            if hasattr(self.app_instance, 'pdf_viewer'):
                self.app_instance.pdf_viewer.open_file(file_path)
            else:
                messagebox.showinfo("Bilgi", "PDF okuyucu henüz mevcut değil")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
    
    def animate_file_addition(self, count):
        """Dosya ekleme animasyonu"""
        # Başarı mesajı göster
        self.show_notification(f"✅ {count} dosya eklendi", "success")
    
    def show_notification(self, message, type_="info"):
        """Bildirim göster"""
        # Basit notification sistemi
        notification = tk.Toplevel(self.winfo_toplevel())
        notification.overrideredirect(True)
        notification.configure(bg='green' if type_ == "success" else 'blue')
        
        label = ttk.Label(
            notification,
            text=message,
            background='green' if type_ == "success" else 'blue',
            foreground='white',
            padding=10
        )
        label.pack()
        
        # Konumlandır
        x = self.winfo_toplevel().winfo_x() + 50
        y = self.winfo_toplevel().winfo_y() + 50
        notification.geometry(f"+{x}+{y}")
        
        # 3 saniye sonra kapat
        notification.after(3000, notification.destroy)
    
    # View Management
    def show_welcome_view(self):
        """Karşılama görünümünü göster"""
        self.hide_all_panels()
        self.drop_zone.pack(fill=tk.BOTH, expand=True)
    
    def show_file_list(self):
        """Dosya listesini göster"""
        self.drop_zone.pack_forget()
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Options panel'i göster
        if self.selected_files:
            self.show_options_panel()
    
    def show_options_panel(self):
        """Options panel'i göster"""
        self.options_panel.pack(fill=tk.X, pady=(0, 20))
        self.populate_operation_combo()
    
    def show_progress_panel(self):
        """Progress panel'i göster"""
        self.progress_panel.pack(fill=tk.X, pady=(0, 20))
    
    def show_results_panel(self):
        """Results panel'i göster"""
        self.results_panel.pack(fill=tk.X)
    
    def hide_all_panels(self):
        """Tüm panelleri gizle"""
        for panel in [self.file_list_frame, self.options_panel, 
                     self.progress_panel, self.results_panel]:
            if panel:
                panel.pack_forget()
    
    def populate_operation_combo(self):
        """Operation combo'yu doldur"""
        operations = [
            ('merge', '🔗 PDF Birleştir'),
            ('split', '✂️ PDF Böl'),
            ('compress', '🗜️ PDF Sıkıştır'),
            ('convert', '🔄 Format Dönüştür'),
            ('rotate', '↻ Sayfa Döndür'),
            ('extract_text', '📄 Metin Çıkar'),
            ('extract_images', '🖼️ Resim Çıkar'),
            ('watermark', '💧 Filigran Ekle'),
            ('encrypt', '🔐 Şifrele'),
            ('decrypt', '🔓 Şifre Kaldır'),
            ('ocr', '👁️ OCR Uygula'),
            ('optimize', '⚡ Optimize Et')
        ]
        
        self.operation_combo['values'] = [op[1] for op in operations]
        
        # Varsayılan işlem
        if self.current_operation:
            for i, (op_id, op_name) in enumerate(operations):
                if op_id == self.current_operation:
                    self.operation_combo.current(i)
                    break
        else:
            self.operation_combo.current(0)
        
        self.on_operation_change()
    
    def on_operation_change(self, event=None):
        """İşlem değişikliği olayı"""
        selected = self.operation_combo.get()
        
        # Operation ID'sini bul
        operations = {
            '🔗 PDF Birleştir': 'merge',
            '✂️ PDF Böl': 'split',
            '🗜️ PDF Sıkıştır': 'compress',
            '🔄 Format Dönüştür': 'convert',
            '↻ Sayfa Döndür': 'rotate',
            '📄 Metin Çıkar': 'extract_text',
            '🖼️ Resim Çıkar': 'extract_images',
            '💧 Filigran Ekle': 'watermark',
            '🔐 Şifrele': 'encrypt',
            '🔓 Şifre Kaldır': 'decrypt',
            '👁️ OCR Uygula': 'ocr',
            '⚡ Optimize Et': 'optimize'
        }
        
        self.current_operation = operations.get(selected, 'merge')
        self.update_options_panel()
    
    def update_options_panel(self):
        """Options panel'ini güncelle"""
        # Mevcut dinamik seçenekleri temizle
        for widget in self.dynamic_options.winfo_children():
            widget.destroy()
        
        # Seçilen işleme göre seçenekleri oluştur
        self.create_operation_options()
    
    def create_operation_options(self):
        """İşlem seçeneklerini oluştur"""
        if self.current_operation == 'merge':
            self.create_merge_options()
        elif self.current_operation == 'split':
            self.create_split_options()
        elif self.current_operation == 'compress':
            self.create_compress_options()
        elif self.current_operation == 'convert':
            self.create_convert_options()
        elif self.current_operation == 'rotate':
            self.create_rotate_options()
        elif self.current_operation == 'watermark':
            self.create_watermark_options()
        elif self.current_operation == 'encrypt':
            self.create_encrypt_options()
        elif self.current_operation == 'ocr':
            self.create_ocr_options()
        # Diğer işlemler için benzer metodlar...
    
    def create_merge_options(self):
        """Birleştirme seçenekleri"""
        # Birleştirme sırası
        order_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Birleştirme Sırası",
            style='OptionsGroup.TLabelframe'
        )
        order_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.merge_order_var = tk.StringVar(value="filename")
        
        ttk.Radiobutton(
            order_frame,
            text="Dosya adına göre",
            variable=self.merge_order_var,
            value="filename"
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            order_frame,
            text="Tarih sırasına göre",
            variable=self.merge_order_var,
            value="date"
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            order_frame,
            text="Manuel sıralama",
            variable=self.merge_order_var,
            value="manual"
        ).pack(anchor='w', padx=10, pady=2)
        
        # Bookmark seçenekleri
        bookmark_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Bookmark Ayarları",
            style='OptionsGroup.TLabelframe'
        )
        bookmark_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.add_bookmarks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            bookmark_frame,
            text="Her dosya için bookmark ekle",
            variable=self.add_bookmarks_var
        ).pack(anchor='w', padx=10, pady=2)
    
    def create_split_options(self):
        """Bölme seçenekleri"""
        # Bölme türü
        split_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Bölme Türü",
            style='OptionsGroup.TLabelframe'
        )
        split_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.split_type_var = tk.StringVar(value="pages")
        
        ttk.Radiobutton(
            split_frame,
            text="Her sayfa ayrı dosya",
            variable=self.split_type_var,
            value="pages"
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            split_frame,
            text="Sayfa aralıkları",
            variable=self.split_type_var,
            value="ranges"
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            split_frame,
            text="Belirli sayfa sayısı",
            variable=self.split_type_var,
            value="count"
        ).pack(anchor='w', padx=10, pady=2)
        
        # Sayfa sayısı (count seçili olduğunda)
        count_frame = ttk.Frame(split_frame)
        count_frame.pack(fill=tk.X, padx=20, pady=2)
        
        ttk.Label(count_frame, text="Sayfa sayısı:").pack(side=tk.LEFT)
        
        self.pages_per_file_var = tk.IntVar(value=1)
        ttk.Spinbox(
            count_frame,
            from_=1,
            to=100,
            textvariable=self.pages_per_file_var,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_compress_options(self):
        """Sıkıştırma seçenekleri"""
        # Kalite seçenekleri
        quality_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Sıkıştırma Kalitesi",
            style='OptionsGroup.TLabelframe'
        )
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.compression_quality_var = tk.StringVar(value="medium")
        
        qualities = [
            ("high", "Yüksek Kalite (az sıkıştırma)"),
            ("medium", "Orta Kalite (dengeli)"),
            ("low", "Düşük Kalite (yüksek sıkıştırma)")
        ]
        
        for value, text in qualities:
            ttk.Radiobutton(
                quality_frame,
                text=text,
                variable=self.compression_quality_var,
                value=value
            ).pack(anchor='w', padx=10, pady=2)
        
        # Gelişmiş seçenekler
        advanced_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Gelişmiş Seçenekler",
            style='OptionsGroup.TLabelframe'
        )
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.optimize_images_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame,
            text="Resimleri optimize et",
            variable=self.optimize_images_var
        ).pack(anchor='w', padx=10, pady=2)
        
        self.remove_metadata_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            advanced_frame,
            text="Metadata bilgilerini kaldır",
            variable=self.remove_metadata_var
        ).pack(anchor='w', padx=10, pady=2)
    
    def create_convert_options(self):
        """Dönüştürme seçenekleri"""
        # Çıktı formatı
        format_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Çıktı Formatı",
            style='OptionsGroup.TLabelframe'
        )
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        format_inner = ttk.Frame(format_frame)
        format_inner.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_inner, text="Format:").pack(side=tk.LEFT)
        
        self.output_format_var = tk.StringVar(value="docx")
        format_combo = ttk.Combobox(
            format_inner,
            textvariable=self.output_format_var,
            values=["docx", "txt", "jpg", "png", "tiff", "html"],
            state="readonly",
            width=15
        )
        format_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # DPI ayarları (resim formatları için)
        dpi_frame = ttk.Frame(format_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dpi_frame, text="DPI:").pack(side=tk.LEFT)
        
        self.output_dpi_var = tk.IntVar(value=300)
        ttk.Spinbox(
            dpi_frame,
            from_=72,
            to=600,
            textvariable=self.output_dpi_var,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_rotate_options(self):
        """Döndürme seçenekleri"""
        # Döndürme açısı
        rotation_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Döndürme Açısı",
            style='OptionsGroup.TLabelframe'
        )
        rotation_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rotation_angle_var = tk.IntVar(value=90)
        
        angles = [(90, "90° (saat yönü)"), (180, "180°"), (270, "270° (saat yönü tersi)")]
        
        for angle, text in angles:
            ttk.Radiobutton(
                rotation_frame,
                text=text,
                variable=self.rotation_angle_var,
                value=angle
            ).pack(anchor='w', padx=10, pady=2)
        
        # Sayfa seçimi
        pages_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Sayfa Seçimi",
            style='OptionsGroup.TLabelframe'
        )
        pages_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rotate_pages_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(
            pages_frame,
            text="Tüm sayfalar",
            variable=self.rotate_pages_var,
            value="all"
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            pages_frame,
            text="Belirli sayfalar",
            variable=self.rotate_pages_var,
            value="specific"
        ).pack(anchor='w', padx=10, pady=2)
        
        # Sayfa numaraları
        specific_frame = ttk.Frame(pages_frame)
        specific_frame.pack(fill=tk.X, padx=20, pady=2)
        
        ttk.Label(specific_frame, text="Sayfalar (örn: 1,3,5-10):").pack(side=tk.LEFT)
        
        self.specific_pages_var = tk.StringVar()
        ttk.Entry(
            specific_frame,
            textvariable=self.specific_pages_var,
            width=20
        ).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_watermark_options(self):
        """Filigran seçenekleri"""
        # Filigran türü
        type_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Filigran Türü",
            style='OptionsGroup.TLabelframe'
        )
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.watermark_type_var = tk.StringVar(value="text")
        
        ttk.Radiobutton(
            type_frame,
            text="Metin filigranı",
            variable=self.watermark_type_var,
            value="text",
            command=self.update_watermark_options
        ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Radiobutton(
            type_frame,
            text="Resim filigranı",
            variable=self.watermark_type_var,
            value="image",
            command=self.update_watermark_options
        ).pack(anchor='w', padx=10, pady=2)
        
        # Dinamik içerik frame
        self.watermark_content_frame = ttk.Frame(self.dynamic_options)
        self.watermark_content_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.update_watermark_options()
        
        # Pozisyon seçenekleri
        position_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Pozisyon",
            style='OptionsGroup.TLabelframe'
        )
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        positions_grid = ttk.Frame(position_frame)
        positions_grid.pack(padx=10, pady=5)
        
        self.watermark_position_var = tk.StringVar(value="center")
        
        positions = [
            ("top-left", "Sol Üst", 0, 0),
            ("top-center", "Üst Orta", 0, 1),
            ("top-right", "Sağ Üst", 0, 2),
            ("center-left", "Sol Orta", 1, 0),
            ("center", "Orta", 1, 1),
            ("center-right", "Sağ Orta", 1, 2),
            ("bottom-left", "Sol Alt", 2, 0),
            ("bottom-center", "Alt Orta", 2, 1),
            ("bottom-right", "Sağ Alt", 2, 2)
        ]
        
        for value, text, row, col in positions:
            ttk.Radiobutton(
                positions_grid,
                text=text,
                variable=self.watermark_position_var,
                value=value
            ).grid(row=row, column=col, padx=5, pady=2, sticky='w')
    
    def update_watermark_options(self):
        """Filigran seçeneklerini güncelle"""
        # Mevcut içeriği temizle
        for widget in self.watermark_content_frame.winfo_children():
            widget.destroy()
        
        if self.watermark_type_var.get() == "text":
            # Metin filigranı seçenekleri
            text_frame = ttk.LabelFrame(
                self.watermark_content_frame,
                text="Metin Ayarları",
                style='OptionsGroup.TLabelframe'
            )
            text_frame.pack(fill=tk.X)
            
            # Metin
            text_input_frame = ttk.Frame(text_frame)
            text_input_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(text_input_frame, text="Metin:").pack(side=tk.LEFT)
            
            self.watermark_text_var = tk.StringVar(value="KOPYA")
            ttk.Entry(
                text_input_frame,
                textvariable=self.watermark_text_var,
                width=30
            ).pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            
            # Font boyutu
            font_frame = ttk.Frame(text_frame)
            font_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(font_frame, text="Font boyutu:").pack(side=tk.LEFT)
            
            self.watermark_font_size_var = tk.IntVar(value=50)
            ttk.Spinbox(
                font_frame,
                from_=10,
                to=200,
                textvariable=self.watermark_font_size_var,
                width=10
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            # Şeffaflık
            opacity_frame = ttk.Frame(text_frame)
            opacity_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(opacity_frame, text="Şeffaflık:").pack(side=tk.LEFT)
            
            self.watermark_opacity_var = tk.DoubleVar(value=0.3)
            opacity_scale = ttk.Scale(
                opacity_frame,
                from_=0.1,
                to=1.0,
                orient=tk.HORIZONTAL,
                variable=self.watermark_opacity_var
            )
            opacity_scale.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            
        else:  # image watermark
            # Resim filigranı seçenekleri
            image_frame = ttk.LabelFrame(
                self.watermark_content_frame,
                text="Resim Ayarları",
                style='OptionsGroup.TLabelframe'
            )
            image_frame.pack(fill=tk.X)
            
            # Resim dosyası
            file_frame = ttk.Frame(image_frame)
            file_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(file_frame, text="Resim dosyası:").pack(side=tk.LEFT)
            
            self.watermark_image_var = tk.StringVar()
            ttk.Entry(
                file_frame,
                textvariable=self.watermark_image_var,
                width=30
            ).pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            
            ttk.Button(
                file_frame,
                text="Seç",
                command=self.select_watermark_image
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            # Boyut
            size_frame = ttk.Frame(image_frame)
            size_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(size_frame, text="Boyut (%):").pack(side=tk.LEFT)
            
            self.watermark_size_var = tk.IntVar(value=20)
            ttk.Spinbox(
                size_frame,
                from_=5,
                to=100,
                textvariable=self.watermark_size_var,
                width=10
            ).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_encrypt_options(self):
        """Şifreleme seçenekleri"""
        # Şifre
        password_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Şifre Ayarları",
            style='OptionsGroup.TLabelframe'
        )
        password_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Kullanıcı şifresi
        user_pwd_frame = ttk.Frame(password_frame)
        user_pwd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(user_pwd_frame, text="Kullanıcı şifresi:").pack(side=tk.LEFT)
        
        self.user_password_var = tk.StringVar()
        ttk.Entry(
            user_pwd_frame,
            textvariable=self.user_password_var,
            show="*",
            width=20
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Sahip şifresi
        owner_pwd_frame = ttk.Frame(password_frame)
        owner_pwd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(owner_pwd_frame, text="Sahip şifresi:").pack(side=tk.LEFT)
        
        self.owner_password_var = tk.StringVar()
        ttk.Entry(
            owner_pwd_frame,
            textvariable=self.owner_password_var,
            show="*",
            width=20
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # İzin ayarları
        permissions_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="İzin Ayarları",
            style='OptionsGroup.TLabelframe'
        )
        permissions_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.allow_printing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            permissions_frame,
            text="Yazdırmaya izin ver",
            variable=self.allow_printing_var
        ).pack(anchor='w', padx=10, pady=2)
        
        self.allow_copying_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            permissions_frame,
            text="Kopyalamaya izin ver",
            variable=self.allow_copying_var
        ).pack(anchor='w', padx=10, pady=2)
        
        self.allow_modification_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            permissions_frame,
            text="Değişiklik yapılmasına izin ver",
            variable=self.allow_modification_var
        ).pack(anchor='w', padx=10, pady=2)
    
    def create_ocr_options(self):
        """OCR seçenekleri"""
        # Dil seçimi
        language_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="OCR Dil Ayarları",
            style='OptionsGroup.TLabelframe'
        )
        language_frame.pack(fill=tk.X, pady=(0, 10))
        
        lang_select_frame = ttk.Frame(language_frame)
        lang_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(lang_select_frame, text="Ana dil:").pack(side=tk.LEFT)
        
        self.ocr_language_var = tk.StringVar(value="tur")
        
        # Mevcut dilleri al
        available_languages = self.ocr_processor.get_available_languages() if self.ocr_processor else ["eng", "tur"]
        
        lang_combo = ttk.Combobox(
            lang_select_frame,
            textvariable=self.ocr_language_var,
            values=available_languages,
            state="readonly",
            width=15
        )
        lang_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Otomatik dil algılama
        self.auto_detect_language_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            language_frame,
            text="Otomatik dil algılama",
            variable=self.auto_detect_language_var
        ).pack(anchor='w', padx=10, pady=2)
        
        # Gelişmiş OCR seçenekleri
        advanced_ocr_frame = ttk.LabelFrame(
            self.dynamic_options,
            text="Gelişmiş Seçenekler",
            style='OptionsGroup.TLabelframe'
        )
        advanced_ocr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # DPI
        dpi_frame = ttk.Frame(advanced_ocr_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dpi_frame, text="DPI:").pack(side=tk.LEFT)
        
        self.ocr_dpi_var = tk.IntVar(value=300)
        ttk.Spinbox(
            dpi_frame,
            from_=150,
            to=600,
            textvariable=self.ocr_dpi_var,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Ön işleme
        self.ocr_preprocessing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_ocr_frame,
            text="Görüntü ön işleme uygula",
            variable=self.ocr_preprocessing_var
        ).pack(anchor='w', padx=10, pady=2)
        
        # Eğim düzeltme
        self.ocr_deskew_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_ocr_frame,
            text="Eğim düzeltme",
            variable=self.ocr_deskew_var
        ).pack(anchor='w', padx=10, pady=2)
    
    def select_watermark_image(self):
        """Filigran resmi seç"""
        filetypes = [
            ('Resim Dosyaları', '*.png *.jpg *.jpeg *.gif *.bmp'),
            ('Tüm Dosyalar', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Filigran Resmi Seçin",
            filetypes=filetypes
        )
        
        if filename:
            self.watermark_image_var.set(filename)
    
    def browse_output_directory(self):
        """Çıktı dizini seç"""
        directory = filedialog.askdirectory(
            title="Çıktı Dizinini Seçin",
            initialdir=self.output_var.get()
        )
        
        if directory:
            self.output_var.set(directory)
            # Konfigürasyona kaydet
            self.config_manager.set('pdf_processing.output_directory', directory)
            self.config_manager.save()
    
    # Processing Methods
    def start_processing(self):
        """İşlemi başlat"""
        if not self.selected_files:
            messagebox.showwarning("Uyarı", "Lütfen önce dosya seçin!")
            return
        
        if self.is_processing:
            messagebox.showinfo("Bilgi", "Zaten bir işlem devam ediyor!")
            return
        
        # Çıktı dizini kontrolü
        output_dir = self.output_var.get()
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror("Hata", "Geçerli bir çıktı dizini seçin!")
            return
        
        # İşlem ayarlarını hazırla
        operation_settings = self.get_operation_settings()
        
        # Progress panel'i göster
        self.show_progress_panel()
        self.is_processing = True
        
        # Process button'ı devre dışı bırak
        self.process_btn.configure(state='disabled', text="İşleniyor...")
        
        # İşlemi thread'de başlat
        processing_thread = threading.Thread(
            target=self.process_files,
            args=(self.selected_files.copy(), operation_settings),
            daemon=True
        )
        processing_thread.start()
    
    def get_operation_settings(self):
        """İşlem ayarlarını al"""
        settings = {
            'operation': self.current_operation,
            'output_directory': self.output_var.get()
        }
        
        # İşleme göre ayarları ekle
        if self.current_operation == 'merge':
            settings.update({
                'order': getattr(self, 'merge_order_var', tk.StringVar()).get(),
                'add_bookmarks': getattr(self, 'add_bookmarks_var', tk.BooleanVar()).get()
            })
        elif self.current_operation == 'split':
            settings.update({
                'split_type': getattr(self, 'split_type_var', tk.StringVar()).get(),
                'pages_per_file': getattr(self, 'pages_per_file_var', tk.IntVar()).get()
            })
        elif self.current_operation == 'compress':
            settings.update({
                'quality': getattr(self, 'compression_quality_var', tk.StringVar()).get(),
                'optimize_images': getattr(self, 'optimize_images_var', tk.BooleanVar()).get(),
                'remove_metadata': getattr(self, 'remove_metadata_var', tk.BooleanVar()).get()
            })
        elif self.current_operation == 'convert':
            settings.update({
                'output_format': getattr(self, 'output_format_var', tk.StringVar()).get(),
                'dpi': getattr(self, 'output_dpi_var', tk.IntVar()).get()
            })
        elif self.current_operation == 'rotate':
            settings.update({
                'angle': getattr(self, 'rotation_angle_var', tk.IntVar()).get(),
                'pages': getattr(self, 'rotate_pages_var', tk.StringVar()).get(),
                'specific_pages': getattr(self, 'specific_pages_var', tk.StringVar()).get()
            })
        elif self.current_operation == 'watermark':
            settings.update({
                'type': getattr(self, 'watermark_type_var', tk.StringVar()).get(),
                'position': getattr(self, 'watermark_position_var', tk.StringVar()).get()
            })
            
            if settings['type'] == 'text':
                settings.update({
                    'text': getattr(self, 'watermark_text_var', tk.StringVar()).get(),
                    'font_size': getattr(self, 'watermark_font_size_var', tk.IntVar()).get(),
                    'opacity': getattr(self, 'watermark_opacity_var', tk.DoubleVar()).get()
                })
            else:
                settings.update({
                    'image_path': getattr(self, 'watermark_image_var', tk.StringVar()).get(),
                    'size': getattr(self, 'watermark_size_var', tk.IntVar()).get()
                })
        elif self.current_operation == 'encrypt':
            settings.update({
                'user_password': getattr(self, 'user_password_var', tk.StringVar()).get(),
                'owner_password': getattr(self, 'owner_password_var', tk.StringVar()).get(),
                'allow_printing': getattr(self, 'allow_printing_var', tk.BooleanVar()).get(),
                'allow_copying': getattr(self, 'allow_copying_var', tk.BooleanVar()).get(),
                'allow_modification': getattr(self, 'allow_modification_var', tk.BooleanVar()).get()
            })
        elif self.current_operation == 'ocr':
            settings.update({
                'language': getattr(self, 'ocr_language_var', tk.StringVar()).get(),
                'auto_detect': getattr(self, 'auto_detect_language_var', tk.BooleanVar()).get(),
                'dpi': getattr(self, 'ocr_dpi_var', tk.IntVar()).get(),
                'preprocessing': getattr(self, 'ocr_preprocessing_var', tk.BooleanVar()).get(),
                'deskew': getattr(self, 'ocr_deskew_var', tk.BooleanVar()).get()
            })
        
        return settings
    
    def process_files(self, files, settings):
        """Dosyaları işle"""
        try:
            results = []
            total_files = len(files)
            
            for i, file_path in enumerate(files):
                if not self.is_processing:  # İptal edildi
                    break
                
                # Progress güncelle
                progress = (i / total_files) * 100
                self.update_progress(progress, f"İşleniyor: {Path(file_path).name}")
                
                # Dosyayı işle
                try:
                    start_time = time.time()
                    result = self.process_single_file(file_path, settings)
                    end_time = time.time()
                    
                    results.append({
                        'file': Path(file_path).name,
                        'operation': settings['operation'],
                        'status': 'Başarılı' if result['success'] else 'Hata',
                        'size': self.format_file_size(result.get('output_size', 0)),
                        'time': f"{end_time - start_time:.1f}s",
                        'output_path': result.get('output_path', ''),
                        'error': result.get('error', '')
                    })
                    
                except Exception as e:
                    results.append({
                        'file': Path(file_path).name,
                        'operation': settings['operation'],
                        'status': 'Hata',
                        'size': '-',
                        'time': '-',
                        'output_path': '',
                        'error': str(e)
                    })
                
                # İstatistikleri güncelle
                self.update_processing_stats(i + 1, total_files, results)
            
            # İşlem tamamlandı
            self.processing_completed(results)
            
        except Exception as e:
            self.processing_error(str(e))
    
    def process_single_file(self, file_path, settings):
        """Tek dosyayı işle"""
        operation = settings['operation']
        
        try:
            if operation == 'merge':
                # Birleştirme işlemi tüm dosyalar için bir kez yapılır
                if file_path == settings.get('first_file'):
                    return self.pdf_processor.merge_pdfs(
                        settings['all_files'],
                        settings['output_directory'],
                        order=settings.get('order', 'filename'),
                        add_bookmarks=settings.get('add_bookmarks', True)
                    )
                else:
                    return {'success': True, 'skipped': True}
                    
            elif operation == 'split':
                return self.pdf_processor.split_pdf(
                    file_path,
                    settings['output_directory'],
                    split_type=settings.get('split_type', 'pages'),
                    pages_per_file=settings.get('pages_per_file', 1)
                )
                
            elif operation == 'compress':
                return self.pdf_processor.compress_pdf(
                    file_path,
                    settings['output_directory'],
                    quality=settings.get('quality', 'medium'),
                    optimize_images=settings.get('optimize_images', True),
                    remove_metadata=settings.get('remove_metadata', False)
                )
                
            elif operation == 'convert':
                return self.pdf_processor.convert_pdf(
                    file_path,
                    settings['output_directory'],
                    output_format=settings.get('output_format', 'docx'),
                    dpi=settings.get('dpi', 300)
                )
                
            elif operation == 'rotate':
                return self.pdf_processor.rotate_pdf(
                    file_path,
                    settings['output_directory'],
                    angle=settings.get('angle', 90),
                    pages=settings.get('pages', 'all'),
                    specific_pages=settings.get('specific_pages', '')
                )
                
            elif operation == 'watermark':
                return self.pdf_processor.add_watermark(
                    file_path,
                    settings['output_directory'],
                    watermark_type=settings.get('type', 'text'),
                    **{k: v for k, v in settings.items() if k not in ['operation', 'output_directory', 'type']}
                )
                
            elif operation == 'encrypt':
                return self.pdf_processor.encrypt_pdf(
                    file_path,
                    settings['output_directory'],
                    user_password=settings.get('user_password', ''),
                    owner_password=settings.get('owner_password', ''),
                    permissions={
                        'printing': settings.get('allow_printing', True),
                        'copying': settings.get('allow_copying', True),
                        'modification': settings.get('allow_modification', False)
                    }
                )
                
            elif operation == 'decrypt':
                return self.pdf_processor.decrypt_pdf(
                    file_path,
                    settings['output_directory'],
                    password=settings.get('password', '')
                )
                
            elif operation == 'ocr':
                return self.ocr_processor.process_pdf(
                    file_path,
                    settings['output_directory'],
                    language=settings.get('language', 'tur'),
                    auto_detect=settings.get('auto_detect', True),
                    dpi=settings.get('dpi', 300),
                    preprocessing=settings.get('preprocessing', True),
                    deskew=settings.get('deskew', True)
                )
                
            elif operation == 'extract_text':
                return self.pdf_processor.extract_text(
                    file_path,
                    settings['output_directory']
                )
                
            elif operation == 'extract_images':
                return self.pdf_processor.extract_images(
                    file_path,
                    settings['output_directory']
                )
                
            elif operation == 'optimize':
                return self.pdf_processor.optimize_pdf(
                    file_path,
                    settings['output_directory']
                )
                
            else:
                return {'success': False, 'error': f'Desteklenmeyen işlem: {operation}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_progress(self, percentage, message):
        """Progress güncelle"""
        def update_ui():
            self.main_progress_var.set(percentage)
            self.progress_text.configure(text=message)
        
        # UI güncellemesini main thread'de yap
        self.after_idle(update_ui)
    
    def update_processing_stats(self, processed, total, results):
        """İşlem istatistiklerini güncelle"""
        def update_ui():
            successful = len([r for r in results if r['status'] == 'Başarılı'])
            errors = len([r for r in results if r['status'] == 'Hata'])
            remaining = total - processed
            
            self.stats_labels['processed'].configure(text=f"İşlenen: {processed}")
            self.stats_labels['remaining'].configure(text=f"Kalan: {remaining}")
            self.stats_labels['errors'].configure(text=f"Hata: {errors}")
            
            # Hız hesapla (basit)
            if processed > 0:
                avg_time = sum([float(r['time'].replace('s', '')) for r in results if r['time'] != '-']) / len([r for r in results if r['time'] != '-'])
                speed = 1.0 / avg_time if avg_time > 0 else 0
                self.stats_labels['speed'].configure(text=f"Hız: {speed:.1f} dosya/s")
                
                # ETA
                if remaining > 0:
                    eta_seconds = remaining * avg_time
                    eta_minutes = int(eta_seconds // 60)
                    eta_seconds = int(eta_seconds % 60)
                    self.stats_labels['eta'].configure(text=f"Tahmini: {eta_minutes:02d}:{eta_seconds:02d}")
        
        self.after_idle(update_ui)
    
    def processing_completed(self, results):
        """İşlem tamamlandığında çağrılır"""
        def update_ui():
            self.is_processing = False
            
            # Progress panel'i gizle
            self.progress_panel.pack_forget()
            
            # Results panel'i göster ve doldur
            self.populate_results(results)
            self.show_results_panel()
            
            # Process button'ı yeniden aktifleştir
            self.process_btn.configure(state='normal', text="🚀 İşlemi Başlat")
            
            # Başarı mesajı
            successful = len([r for r in results if r['status'] == 'Başarılı'])
            total = len(results)
            
            if successful == total:
                self.show_notification(f"✅ Tüm dosyalar başarıyla işlendi! ({successful}/{total})", "success")
            else:
                errors = total - successful
                self.show_notification(f"⚠️ İşlem tamamlandı: {successful} başarılı, {errors} hata", "warning")
        
        self.after_idle(update_ui)
    
    def processing_error(self, error_message):
        """İşlem hatası durumunda çağrılır"""
        def update_ui():
            self.is_processing = False
            
            # Progress panel'i gizle
            self.progress_panel.pack_forget()
            
            # Process button'ı yeniden aktifleştir
            self.process_btn.configure(state='normal', text="🚀 İşlemi Başlat")
            
            # Hata mesajı göster
            messagebox.showerror("İşlem Hatası", f"İşlem sırasında hata oluştu:\n\n{error_message}")
        
        self.after_idle(update_ui)
    
    def cancel_processing(self):
        """İşlemi iptal et"""
        if self.is_processing:
            result = messagebox.askyesno("İptal", "İşlemi iptal etmek istediğinizden emin misiniz?")
            if result:
                self.is_processing = False
                self.show_notification("⏹️ İşlem iptal edildi", "info")
    
    def populate_results(self, results):
        """Sonuçları treeview'a ekle"""
        # Mevcut öğeleri temizle
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Sonuçları ekle
        for result in results:
            if not result.get('skipped', False):
                self.results_tree.insert(
                    '',
                    'end',
                    values=(
                        result['file'],
                        result['operation'],
                        result['status'],
                        result['size'],
                        result['time']
                    ),
                    tags=(result['status'].lower(),)
                )
        
        # Tag renklerini ayarla
        self.results_tree.tag_configure('başarılı', foreground='green')
        self.results_tree.tag_configure('hata', foreground='red')
    
    def on_result_double_click(self, event):
        """Sonuç öğesine çift tıklama"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            values = item['values']
            
            if values[2] == 'Hata':  # Status
                # Hata detaylarını göster
                messagebox.showerror("Hata Detayı", f"Dosya: {values[0]}\nHata: Detay bilgi yok")
            else:
                # Çıktı klasörünü aç
                self.open_output_folder()
    
    def export_results(self):
        """Sonuçları rapor olarak kaydet"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Raporu Kaydet",
                defaultextension=".txt",
                filetypes=[
                    ("Metin Dosyaları", "*.txt"),
                    ("CSV Dosyaları", "*.csv"),
                    ("JSON Dosyaları", "*.json")
                ]
            )
            
            if filename:
                # Basit metin raporu
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"PyPDF-Stirling Tools v2 İşlem Raporu\n")
                    f.write(f"Tarih: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"İşlem: {self.current_operation}\n\n")
                    
                    for child in self.results_tree.get_children():
                        values = self.results_tree.item(child)['values']
                        f.write(f"Dosya: {values[0]}\n")
                        f.write(f"Durum: {values[2]}\n")
                        f.write(f"Boyut: {values[3]}\n")
                        f.write(f"Süre: {values[4]}\n")
                        f.write("-" * 40 + "\n")
                
                self.show_notification("💾 Rapor kaydedildi", "success")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor kaydedilemedi: {e}")
    
    def open_output_folder(self):
        """Çıktı klasörünü aç"""
        output_dir = self.output_var.get()
        if os.path.exists(output_dir):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_dir)
                elif os.name == 'posix':  # macOS/Linux
                    os.system(f'open "{output_dir}"' if sys.platform == 'darwin' else f'xdg-open "{output_dir}"')
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör açılamadı: {e}")
        else:
            messagebox.showwarning("Uyarı", "Çıktı klasörü bulunamadı!")
    
    # Public Methods (Sidebar'dan çağrılacak)
    def set_operation(self, operation_id):
        """İşlemi ayarla"""
        self.current_operation = operation_id
        
        # Eğer dosya listesi görünürse combo'yu güncelle
        if self.selected_files and hasattr(self, 'operation_combo'):
            operations = {
                'merge': '🔗 PDF Birleştir',
                'split': '✂️ PDF Böl',
                'compress': '🗜️ PDF Sıkıştır',
                'convert': '🔄 Format Dönüştür',
                'rotate': '↻ Sayfa Döndür',
                'extract_text': '📄 Metin Çıkar',
                'extract_images': '🖼️ Resim Çıkar',
                'watermark': '💧 Filigran Ekle',
                'encrypt': '🔐 Şifrele',
                'decrypt': '🔓 Şifre Kaldır',
                'ocr': '👁️ OCR Uygula',
                'optimize': '⚡ Optimize Et'
            }
            
            operation_name = operations.get(operation_id, '')
            self.operation_var.set(operation_name)
            self.update_options_panel()
    
    def search_content(self, query):
        """İçerik arama"""
        self.current_search_query = query
        # PDF içinde arama yapacak fonksiyon
        # Şimdilik basit bir implementasyon
        print(f"Aranıyor: {query}")
    
    def clear_search_results(self):
        """Arama sonuçlarını temizle"""
        self.current_search_query = ""
        self.search_results.clear()
    
    def save_current_work(self):
        """Mevcut çalışmayı kaydet"""
        if self.selected_files:
            # Proje dosyası kaydet
            try:
                project_data = {
                    'files': self.selected_files,
                    'operation': self.current_operation,
                    'settings': self.get_operation_settings(),
                    'timestamp': time.time()
                }
                
                filename = filedialog.asksaveasfilename(
                    title="Projeyi Kaydet",
                    defaultextension=".json",
                    filetypes=[("Proje Dosyaları", "*.json")]
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(project_data, f, indent=2, ensure_ascii=False)
                    
                    self.show_notification("💾 Proje kaydedildi", "success")
            
            except Exception as e:
                messagebox.showerror("Hata", f"Proje kaydedilemedi: {e}")
    
    def load_project(self, filename):
        """Proje dosyası yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Dosyaları yükle
            self.selected_files = project_data.get('files', [])
            self.current_operation = project_data.get('operation', 'merge')
            
            # UI'ı güncelle
            if self.selected_files:
                self.update_file_list_display()
                self.show_file_list()
            
            self.show_notification("📁 Proje yüklendi", "success")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Proje yüklenemedi: {e}")
    
    # Advanced Features
    def show_ocr_language_manager(self):
        """OCR dil yöneticisini göster"""
        try:
            from ui.ocr_language_manager import OCRLanguageManager
            manager = OCRLanguageManager(
                parent=self.winfo_toplevel(),
                ocr_processor=self.ocr_processor
            )
            manager.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "OCR dil yöneticisi henüz mevcut değil")
    
    def show_automation_panel(self):
        """Otomasyon panelini göster"""
        try:
            from ui.automation_panel import AutomationPanel
            panel = AutomationPanel(
                parent=self.winfo_toplevel(),
                app_instance=self.app_instance
            )
            panel.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Otomasyon paneli henüz mevcut değil")
    
    def show_script_editor(self):
        """Script editörünü göster"""
        try:
            from ui.script_editor import ScriptEditor
            editor = ScriptEditor(
                parent=self.winfo_toplevel(),
                app_instance=self.app_instance
            )
            editor.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Script editörü henüz mevcut değil")
    
    def cleanup(self):
        """Temizlik işlemleri"""
        # İşlemi durdur
        self.is_processing = False
        
        # Geçici dosyaları temizle
        if hasattr(self.pdf_processor, 'cleanup'):
            self.pdf_processor.cleanup()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Modern Content Area
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import json
import time

class ModernContent(ttk.Frame):
    """
    Modern content area with drag-drop, progress tracking, and real-time updates
    """
    
    def __init__(self, parent, config_manager, theme_manager, pdf_processor, ocr_processor, app_instance):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.pdf_processor = pdf_processor
        self.ocr_processor = ocr_processor
        self.app_instance = app_instance
        
        # Content state
        self.current_operation = None
        self.selected_files = []
        self.output_directory = None
        self.processing_queue = []
        self.is_processing = False
        
        # UI components
        self.drop_zone = None
        self.file_list_frame = None
        self.options_panel = None
        self.progress_panel = None
        self.results_panel = None
        
        # Search functionality
        self.search_results = []
        self.current_search_query = ""
        
        self.create_content_area()
        self.setup_drag_and_drop()
    
    def create_content_area(self):
        """Content area'yı oluştur"""
        self.configure(style='Content.TFrame')
        
        # Ana container
        main_container = ttk.Frame(self, style='ContentContainer.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Üst bölüm - Drop zone ve file list
        self.create_upper