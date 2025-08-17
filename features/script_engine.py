#!/usr/bin/env python3
"""
Script Motoru - Python 3.11 tabanlı script sistemi
Kullanıcıların kendi PDF işleme scriptlerini yazabileceği gelişmiş sistem
"""

import os
import sys
import ast
import types
import inspect
import logging
import threading
import traceback
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QSplitter, QTabWidget, QFileDialog,
    QMessageBox, QProgressBar, QLabel, QComboBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QMenuBar
)

logger = logging.getLogger(__name__)


class ScriptSandbox:
    """Güvenli script çalışma ortamı"""
    
    def __init__(self):
        self.allowed_modules = {
            # Standard kütüphaneler
            'os', 'sys', 'math', 'json', 'csv', 'datetime', 're', 
            'pathlib', 'collections', 'itertools', 'functools',
            
            # PDF işleme
            'PyPDF2', 'reportlab', 'fitz', 'pymupdf',
            
            # Görüntü işleme
            'PIL', 'cv2', 'numpy',
            
            # PyPDF-Tools API
            'pypdf_tools',
        }
        
        self.forbidden_functions = {
            'exec', 'eval', 'compile', '__import__', 'open', 
            'input', 'raw_input', 'exit', 'quit',
        }
        
        self.restricted_attributes = {
            '__globals__', '__locals__', '__builtins__',
            '__code__', '__dict__', '__class__',
        }
    
    def is_safe(self, code: str) -> tuple[bool, str]:
        """
        Kod güvenliğini kontrol et
        
        Args:
            code: Kontrol edilecek Python kodu
            
        Returns:
            tuple: (güvenli_mi, hata_mesajı)
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Import kontrolü
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.allowed_modules:
                            return False, f"Yasaklı modül: {alias.name}"
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in self.allowed_modules:
                        return False, f"Yasaklı modül: {node.module}"
                
                # Fonksiyon çağrısı kontrolü
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.forbidden_functions:
                            return False, f"Yasaklı fonksiyon: {node.func.id}"
                
                # Attribute erişimi kontrolü
                elif isinstance(node, ast.Attribute):
                    if node.attr in self.restricted_attributes:
                        return False, f"Yasaklı attribute: {node.attr}"
            
            return True, ""
            
        except SyntaxError as e:
            return False, f"Söz dizimi hatası: {e}"
        except Exception as e:
            return False, f"Analiz hatası: {e}"


class ScriptExecutor(QThread):
    """Script çalıştırma thread'i"""
    
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, script_code: str, script_globals: Dict[str, Any]):
        super().__init__()
        self.script_code = script_code
        self.script_globals = script_globals
        self.is_cancelled = False
        self.sandbox = ScriptSandbox()
    
    def cancel(self):
        """Script'i iptal et"""
        self.is_cancelled = True
        self.terminate()
    
    def run(self):
        """Script'i çalıştır"""
        try:
            # Güvenlik kontrolü
            is_safe, error_msg = self.sandbox.is_safe(self.script_code)
            if not is_safe:
                self.error_signal.emit(f"Güvenlik hatası: {error_msg}")
                self.finished_signal.emit(False, error_msg)
                return
            
            # Global değişkenleri hazırla
            globals_dict = {
                '__builtins__': {
                    'print': self._safe_print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'min': min,
                    'max': max,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                },
                **self.script_globals
            }
            
            # Script'i çalıştır
            exec(self.script_code, globals_dict)
            
            if not self.is_cancelled:
                self.finished_signal.emit(True, "Script başarıyla tamamlandı")
                
        except Exception as e:
            error_msg = f"Script hatası: {str(e)}\n{traceback.format_exc()}"
            self.error_signal.emit(error_msg)
            self.finished_signal.emit(False, error_msg)
    
    def _safe_print(self, *args, **kwargs):
        """Güvenli print fonksiyonu"""
        output = " ".join(str(arg) for arg in args)
        self.output_signal.emit(output)


class ScriptManager:
    """Script yönetimi ve şablon sistemi"""
    
    def __init__(self, scripts_dir: str = None):
        self.scripts_dir = Path(scripts_dir) if scripts_dir else Path.cwd() / "scripts"
        self.scripts_dir.mkdir(exist_ok=True)
        
        self.templates_dir = self.scripts_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        self.user_scripts_dir = self.scripts_dir / "user"
        self.user_scripts_dir.mkdir(exist_ok=True)
        
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Varsayılan script şablonlarını oluştur"""
        templates = {
            "pdf_merge_template.py": '''#!/usr/bin/env python3
"""
PDF Birleştirme Şablonu
Birden fazla PDF dosyasını birleştirmek için örnek script
"""

import pypdf_tools

def merge_pdfs(input_files, output_file):
    """PDF dosyalarını birleştir"""
    print(f"Birleştiriliyor: {len(input_files)} dosya")
    
    processor = pypdf_tools.PDFProcessor()
    success = processor.merge_pdfs(input_files, output_file)
    
    if success:
        print(f"✅ Başarılı: {output_file}")
    else:
        print("❌ Birleştirme başarısız")
    
    return success

# Örnek kullanım
if __name__ == "__main__":
    input_files = [
        "document1.pdf",
        "document2.pdf", 
        "document3.pdf"
    ]
    
    output_file = "merged_document.pdf"
    merge_pdfs(input_files, output_file)
''',
            
            "pdf_split_template.py": '''#!/usr/bin/env python3
"""
PDF Bölme Şablonu
PDF dosyasını sayfa bazında böler
"""

import pypdf_tools

def split_pdf(input_file, output_dir, pages_per_file=1):
    """PDF dosyasını böl"""
    print(f"Bölünüyor: {input_file}")
    print(f"Sayfa per dosya: {pages_per_file}")
    
    processor = pypdf_tools.PDFProcessor()
    result = processor.split_pdf(input_file, output_dir, pages_per_file)
    
    if result:
        print(f"✅ {len(result)} dosya oluşturuldu")
        for file in result:
            print(f"  📄 {file}")
    else:
        print("❌ Bölme başarısız")
    
    return result

# Örnek kullanım
if __name__ == "__main__":
    input_file = "large_document.pdf"
    output_dir = "split_pages"
    pages_per_file = 2
    
    split_pdf(input_file, output_dir, pages_per_file)
''',
            
            "batch_compress_template.py": '''#!/usr/bin/env python3
"""
Toplu Sıkıştırma Şablonu
Klasördeki tüm PDF'leri sıkıştırır
"""

import os
import pypdf_tools
from pathlib import Path

def batch_compress(input_dir, output_dir, quality="medium"):
    """Klasördeki PDF'leri toplu sıkıştır"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    processor = pypdf_tools.PDFProcessor()
    pdf_files = list(input_path.glob("*.pdf"))
    
    print(f"Sıkıştırılacak dosya sayısı: {len(pdf_files)}")
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        print(f"Sıkıştırılıyor: {pdf_file.name}")
        
        output_file = output_path / f"compressed_{pdf_file.name}"
        
        try:
            success = processor.compress_pdf(
                str(pdf_file),
                str(output_file), 
                quality=quality
            )
            
            if success:
                successful += 1
                print(f"  ✅ Başarılı")
                
                # Boyut karşılaştırması
                original_size = pdf_file.stat().st_size
                compressed_size = output_file.stat().st_size
                ratio = (1 - compressed_size / original_size) * 100
                print(f"  📊 Sıkıştırma: %{ratio:.1f}")
            else:
                failed += 1
                print(f"  ❌ Başarısız")
                
        except Exception as e:
            failed += 1
            print(f"  ❌ Hata: {e}")
    
    print(f"\\n📊 Özet:")
    print(f"Başarılı: {successful}")
    print(f"Başarısız: {failed}")
    
    return successful, failed

# Örnek kullanım
if __name__ == "__main__":
    input_directory = "input_pdfs"
    output_directory = "compressed_pdfs"
    quality_level = "high"  # low, medium, high
    
    batch_compress(input_directory, output_directory, quality_level)
''',
            
            "ocr_batch_template.py": '''#!/usr/bin/env python3
"""
Toplu OCR Şablonu
Taranmış PDF'leri aranabilir hale getirir
"""

import pypdf_tools
from pathlib import Path

def batch_ocr(input_dir, output_dir, language="tur"):
    """Klasördeki PDF'lere toplu OCR uygula"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    ocr_processor = pypdf_tools.OCRProcessor()
    pdf_files = list(input_path.glob("*.pdf"))
    
    print(f"OCR uygulanacak dosya sayısı: {len(pdf_files)}")
    print(f"Dil: {language}")
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        print(f"OCR işleniyor: {pdf_file.name}")
        
        output_file = output_path / f"searchable_{pdf_file.name}"
        
        try:
            success = ocr_processor.process_pdf(
                input_file=str(pdf_file),
                output_file=str(output_file),
                language=language,
                auto_deskew=True,
                preprocessing=True
            )
            
            if success:
                successful += 1
                print(f"  ✅ OCR tamamlandı")
            else:
                failed += 1
                print(f"  ❌ OCR başarısız")
                
        except Exception as e:
            failed += 1
            print(f"  ❌ Hata: {e}")
    
    print(f"\\n📊 OCR Özeti:")
    print(f"Başarılı: {successful}")
    print(f"Başarısız: {failed}")
    
    return successful, failed

# Örnek kullanım
if __name__ == "__main__":
    input_directory = "scanned_pdfs"
    output_directory = "searchable_pdfs"
    ocr_language = "tur"  # tur, eng, deu, fra vb.
    
    batch_ocr(input_directory, output_directory, ocr_language)
'''
        }
        
        # Template dosyalarını oluştur
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def get_templates(self) -> List[Dict[str, str]]:
        """Kullanılabilir şablonları listele"""
        templates = []
        
    def get_templates(self) -> List[Dict[str, str]]:
        """Kullanılabilir şablonları listele"""
        templates = []
        
        for template_file in self.templates_dir.glob("*.py"):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Dosyadan açıklama çıkar
            description = "Açıklama bulunamadı"
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') and i < 10:
                    desc_lines = []
                    for j in range(i+1, len(lines)):
                        if lines[j].strip().endswith('"""'):
                            break
                        desc_lines.append(lines[j].strip())
                    description = '\n'.join(desc_lines)
                    break
            
            templates.append({
                'name': template_file.stem,
                'filename': template_file.name,
                'path': str(template_file),
                'description': description,
                'content': content
            })
        
        return templates
    
    def get_user_scripts(self) -> List[Dict[str, str]]:
        """Kullanıcı scriptlerini listele"""
        scripts = []
        
        for script_file in self.user_scripts_dir.glob("*.py"):
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            scripts.append({
                'name': script_file.stem,
                'filename': script_file.name,
                'path': str(script_file),
                'content': content,
                'modified': datetime.fromtimestamp(script_file.stat().st_mtime)
            })
        
        return sorted(scripts, key=lambda x: x['modified'], reverse=True)
    
    def save_script(self, name: str, content: str) -> str:
        """Script'i kaydet"""
        if not name.endswith('.py'):
            name += '.py'
        
        script_path = self.user_scripts_dir / name
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Script saved: {script_path}")
        return str(script_path)
    
    def delete_script(self, name: str) -> bool:
        """Script'i sil"""
        if not name.endswith('.py'):
            name += '.py'
            
        script_path = self.user_scripts_dir / name
        
        if script_path.exists():
            script_path.unlink()
            logger.info(f"Script deleted: {script_path}")
            return True
        
        return False


class ScriptEngine(QObject):
    """Ana script motoru sınıfı"""
    
    script_started = pyqtSignal(str)
    script_output = pyqtSignal(str, str)  # script_name, output
    script_error = pyqtSignal(str, str)   # script_name, error
    script_finished = pyqtSignal(str, bool, str)  # script_name, success, message
    
    def __init__(self):
        super().__init__()
        self.manager = ScriptManager()
        self.running_scripts = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # PyPDF-Tools API'sini hazırla
        self.pypdf_api = self._create_pypdf_api()
    
    def _create_pypdf_api(self) -> Dict[str, Any]:
        """PyPDF-Tools API objesini oluştur"""
        # Bu kısım gerçek implementasyonda core modüllerden import edilecek
        api = {
            'PDFProcessor': type('PDFProcessor', (), {
                'merge_pdfs': lambda self, files, output: self._mock_operation("merge", files, output),
                'split_pdf': lambda self, file, output_dir, pages=1: self._mock_operation("split", file, output_dir),
                'compress_pdf': lambda self, input_file, output, quality="medium": self._mock_operation("compress", input_file, output),
            }),
            
            'OCRProcessor': type('OCRProcessor', (), {
                'process_pdf': lambda self, input_file, output_file, language="tur", **kwargs: self._mock_operation("ocr", input_file, output_file),
            }),
            
            'ConversionProcessor': type('ConversionProcessor', (), {
                'pdf_to_word': lambda self, pdf_file, word_file: self._mock_operation("convert", pdf_file, word_file),
                'word_to_pdf': lambda self, word_file, pdf_file: self._mock_operation("convert", word_file, pdf_file),
            }),
        }
        
        return api
    
    def _mock_operation(self, operation: str, *args) -> bool:
        """Mock işlem (gerçek implementasyonda kaldırılacak)"""
        logger.info(f"Mock {operation} operation with args: {args}")
        return True
    
    def execute_script(self, name: str, script_code: str) -> str:
        """
        Script'i çalıştır
        
        Args:
            name: Script adı
            script_code: Python kodu
            
        Returns:
            str: Execution ID
        """
        execution_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Global değişkenleri hazırla
        script_globals = {
            'pypdf_tools': type('pypdf_tools', (), self.pypdf_api),
            '__name__': '__main__',
            '__file__': f'<script:{name}>',
        }
        
        # Script executor'ı oluştur ve başlat
        executor = ScriptExecutor(script_code, script_globals)
        
        # Sinyalleri bağla
        executor.output_signal.connect(lambda msg: self.script_output.emit(name, msg))
        executor.error_signal.connect(lambda msg: self.script_error.emit(name, msg))
        executor.finished_signal.connect(lambda success, msg: self._on_script_finished(name, execution_id, success, msg))
        
        # Çalışan scriptler listesine ekle
        self.running_scripts[execution_id] = {
            'name': name,
            'executor': executor,
            'start_time': datetime.now()
        }
        
        executor.start()
        self.script_started.emit(name)
        
        return execution_id
    
    def cancel_script(self, execution_id: str) -> bool:
        """Script'i iptal et"""
        if execution_id in self.running_scripts:
            executor = self.running_scripts[execution_id]['executor']
            executor.cancel()
            executor.wait(timeout=5000)  # 5 saniye bekle
            
            del self.running_scripts[execution_id]
            return True
        
        return False
    
    def _on_script_finished(self, name: str, execution_id: str, success: bool, message: str):
        """Script tamamlandığında çalışır"""
        if execution_id in self.running_scripts:
            del self.running_scripts[execution_id]
        
        self.script_finished.emit(name, success, message)
    
    def get_running_scripts(self) -> Dict[str, Dict]:
        """Çalışan scriptleri döndür"""
        return self.running_scripts.copy()
    
    def stop_all_scripts(self):
        """Tüm çalışan scriptleri durdur"""
        for execution_id in list(self.running_scripts.keys()):
            self.cancel_script(execution_id)


class ScriptEditorWidget(QWidget):
    """Script editör widget'ı - Syntax highlighting ve auto-completion ile"""
    
    script_executed = pyqtSignal(str, str)  # name, code
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.script_manager = ScriptManager()
        self.current_script_name = ""
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """UI'yi kurulum"""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("📄 Yeni")
        self.open_btn = QPushButton("📂 Aç")
        self.save_btn = QPushButton("💾 Kaydet")
        self.save_as_btn = QPushButton("💾 Farklı Kaydet")
        self.run_btn = QPushButton("▶️ Çalıştır")
        
        # Template seçici
        self.template_combo = QComboBox()
        self.template_combo.addItem("Şablon Seç...")
        templates = self.script_manager.get_templates()
        for template in templates:
            self.template_combo.addItem(template['name'], template)
        
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.save_as_btn)
        toolbar_layout.addWidget(QLabel("|"))
        toolbar_layout.addWidget(self.template_combo)
        toolbar_layout.addWidget(QLabel("|"))
        toolbar_layout.addWidget(self.run_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Ana editör alanı
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Dosya browser
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Scriptler")
        self.file_tree.setMaximumWidth(250)
        self._populate_file_tree()
        
        # Sağ panel - Editör
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()
        
        # Script adı
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Script Adı:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("script_name.py")
        name_layout.addWidget(self.name_edit)
        editor_layout.addLayout(name_layout)
        
        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                font-family: 'Consolas', monospace;
            }
        """)
        
        # Örnek kod
        self.code_editor.setPlainText('''#!/usr/bin/env python3
"""
Yeni PyPDF-Tools Scripti
"""

import pypdf_tools

def main():
    """Ana fonksiyon"""
    print("PyPDF-Tools Script başlatıldı!")
    
    # PDF işlemcisini oluştur
    processor = pypdf_tools.PDFProcessor()
    
    # Buraya kendi kodunuzu yazın
    pass

if __name__ == "__main__":
    main()
''')
        
        editor_layout.addWidget(self.code_editor)
        editor_widget.setLayout(editor_layout)
        
        splitter.addWidget(self.file_tree)
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def _setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.new_btn.clicked.connect(self._new_script)
        self.open_btn.clicked.connect(self._open_script)
        self.save_btn.clicked.connect(self._save_script)
        self.save_as_btn.clicked.connect(self._save_as_script)
        self.run_btn.clicked.connect(self._run_script)
        
        self.template_combo.currentTextChanged.connect(self._load_template)
        self.file_tree.itemDoubleClicked.connect(self._open_from_tree)
    
    def _populate_file_tree(self):
        """Dosya ağacını doldur"""
        self.file_tree.clear()
        
        # Templates
        templates_item = QTreeWidgetItem(["📚 Şablonlar"])
        self.file_tree.addTopLevelItem(templates_item)
        
        for template in self.script_manager.get_templates():
            item = QTreeWidgetItem([template['name']])
            item.setData(0, Qt.ItemDataRole.UserRole, ('template', template))
            templates_item.addChild(item)
        
        templates_item.setExpanded(True)
        
        # User scripts
        scripts_item = QTreeWidgetItem(["👤 Scriptlerim"])
        self.file_tree.addTopLevelItem(scripts_item)
        
        for script in self.script_manager.get_user_scripts():
            item = QTreeWidgetItem([script['name']])
            item.setData(0, Qt.ItemDataRole.UserRole, ('user', script))
            scripts_item.addChild(item)
        
        scripts_item.setExpanded(True)
    
    def _new_script(self):
        """Yeni script oluştur"""
        self.current_script_name = ""
        self.name_edit.clear()
        self.code_editor.clear()
        self.code_editor.setPlainText('''#!/usr/bin/env python3
"""
Yeni PyPDF-Tools Scripti
"""

import pypdf_tools

def main():
    """Ana fonksiyon"""
    print("Script başlatıldı!")
    
    # Kodunuzu buraya yazın
    pass

if __name__ == "__main__":
    main()
''')
    
    def _open_script(self):
        """Script aç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Script Aç",
            str(self.script_manager.user_scripts_dir),
            "Python Files (*.py)"
        )
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_script_name = Path(file_path).stem
            self.name_edit.setText(self.current_script_name + '.py')
            self.code_editor.setPlainText(content)
    
    def _save_script(self):
        """Script'i kaydet"""
        if not self.current_script_name:
            self._save_as_script()
            return
        
        content = self.code_editor.toPlainText()
        self.script_manager.save_script(self.current_script_name + '.py', content)
        
        QMessageBox.information(self, "Başarılı", "Script kaydedildi!")
        self._populate_file_tree()
    
    def _save_as_script(self):
        """Script'i farklı kaydet"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyarı", "Script adı giriniz!")
            return
        
        if not name.endswith('.py'):
            name += '.py'
        
        content = self.code_editor.toPlainText()
        script_path = self.script_manager.save_script(name, content)
        
        self.current_script_name = Path(script_path).stem
        QMessageBox.information(self, "Başarılı", f"Script kaydedildi: {script_path}")
        self._populate_file_tree()
    
    def _run_script(self):
        """Script'i çalıştır"""
        name = self.name_edit.text().strip() or "untitled"
        code = self.code_editor.toPlainText()
        
        if not code.strip():
            QMessageBox.warning(self, "Uyarı", "Script kodu boş!")
            return
        
        self.script_executed.emit(name, code)
    
    def _load_template(self, template_name: str):
        """Şablon yükle"""
        if template_name == "Şablon Seç...":
            return
        
        templates = self.script_manager.get_templates()
        for template in templates:
            if template['name'] == template_name:
                self.code_editor.setPlainText(template['content'])
                self.name_edit.setText("")
                self.current_script_name = ""
                break
        
        # Combo'yu sıfırla
        self.template_combo.setCurrentIndex(0)
    
    def _open_from_tree(self, item: QTreeWidgetItem):
        """Ağaçtan script aç"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        data_type, script_data = data
        
        if data_type == 'template':
            self.code_editor.setPlainText(script_data['content'])
            self.name_edit.setText("")
            self.current_script_name = ""
        elif data_type == 'user':
            self.code_editor.setPlainText(script_data['content'])
            self.name_edit.setText(script_data['filename'])
            self.current_script_name = script_data['name']


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test için widget'ı göster
    editor = ScriptEditorWidget()
    editor.setWindowTitle("PyPDF-Tools Script Editor")
    editor.resize(1000, 700)
    editor.show()
    
    sys.exit(app.exec())
