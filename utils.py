#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2 - Utility Classes - DÜZELTILMIŞ
Eksik import'lar ve hata düzeltmeleri
"""

import os
import sys  # ✅ EKLENEN IMPORT
import json
import logging
import shutil
import tempfile
import platform  # ✅ EKLENEN IMPORT
from pathlib import Path
from typing import Any, Dict, Optional, Union, List  # ✅ List eklendi
import threading
import time
from datetime import datetime, timedelta

# İsteğe bağlı importlar - güvenli
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests modülü bulunamadı - güncelleme kontrolü devre dışı")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil modülü bulunamadı - sistem bilgileri sınırlı")

# Windows specific imports
if os.name == 'nt':
    try:
        import winreg
        WINREG_AVAILABLE = True
    except ImportError:
        WINREG_AVAILABLE = False

class ConfigManager:
    """
    Uygulama konfigürasyon yöneticisi - DÜZELTILMIŞ
    """
    
    def __init__(self, app_name="PyPDF Tools v2"):
        self.app_name = app_name
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "config.json"
        self.config_lock = threading.Lock()
        
        # Varsayılan konfigürasyon
        self.default_config = {
            "app": {
                "version": "2.0.0",
                "first_run": True,
                "last_run": None,
                "run_count": 0
            },
            "appearance": {
                "theme": "light",
                "language": "tr",
                "window_size": {"width": 1200, "height": 800},
                "window_position": {"x": -1, "y": -1}
            },
            "privacy": {
                "save_cache": False,
                "save_logs": False,
                "auto_cleanup": True
            },
            "pdf_processing": {
                "default_output_dir": str(Path.home() / "Desktop" / "PyPDF_Output"),
                "default_quality": "medium",
                "default_dpi": 300
            },
            "ocr": {
                "default_language": "tur",
                "installed_languages": ["eng", "tur"],
                "auto_detect_language": True,
                "preprocessing": True
            }
        }
        
        self.config = {}
        self.load()
    
    def _get_config_directory(self) -> Path:
        """Platform-specific config directory - DÜZELTİLMİŞ"""
        try:
            if os.name == 'nt':  # Windows
                config_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / self.app_name
            elif platform.system() == 'Darwin':  # macOS
                config_dir = Path.home() / 'Library' / 'Application Support' / self.app_name
            else:  # Linux
                config_dir = Path.home() / '.config' / self.app_name
            
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir
            
        except Exception as e:
            # Fallback
            fallback_dir = Path.home() / f'.{self.app_name.lower().replace(" ", "_")}'
            fallback_dir.mkdir(parents=True, exist_ok=True)
            print(f"⚠️ Config dizin hatası, fallback kullanılıyor: {fallback_dir}")
            return fallback_dir
    
    def load(self):
        """Konfigürasyonu yükle - hata korumalı"""
        try:
            with self.config_lock:
                if self.config_file.exists():
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_config = json.load(f)
                    self.config = self._merge_configs(self.default_config, loaded_config)
                else:
                    self.config = self.default_config.copy()
                    self.save()
                
                self.config['app']['run_count'] = self.config.get('app', {}).get('run_count', 0) + 1
                self.config['app']['last_run'] = datetime.now().isoformat()
                
        except Exception as e:
            print(f"⚠️ Konfigürasyon yükleme hatası: {e}, varsayılanlar kullanılıyor")
            self.config = self.default_config.copy()
    
    def save(self):
        """Konfigürasyonu kaydet - hata korumalı"""
        try:
            with self.config_lock:
                # Backup oluştur
                if self.config_file.exists():
                    backup_file = self.config_file.with_suffix('.json.bak')
                    shutil.copy2(self.config_file, backup_file)
                
                # Geçici dosyaya yaz, sonra taşı (atomic operation)
                temp_file = self.config_file.with_suffix('.json.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                
                # Atomic move
                temp_file.replace(self.config_file)
                
        except Exception as e:
            print(f"⚠️ Konfigürasyon kaydetme hatası: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Konfigürasyon değeri al - güvenli"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except:
            return default
    
    def set(self, key: str, value: Any):
        """Konfigürasyon değeri ayarla - güvenli"""
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
        except Exception as e:
            print(f"⚠️ Konfigürasyon ayarlama hatası: {e}")
    
    def _merge_configs(self, default: dict, loaded: dict) -> dict:
        """İki konfigürasyonu birleştir"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result

class CacheManager:
    """Cache yönetim sistemi - DÜZELTİLMİŞ"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.cache_dir = self._get_cache_directory()
        self.cache_lock = threading.Lock()
        
        if self.enabled:
            try:
                self._create_cache_directories()
            except Exception as e:
                print(f"⚠️ Cache dizinleri oluşturulamadı: {e}")
                self.enabled = False
    
    def _get_cache_directory(self) -> Path:
        """Cache dizini - hata korumalı"""
        try:
            if os.name == 'nt':  # Windows
                cache_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'PyPDF Tools v2' / 'Cache'
            elif platform.system() == 'Darwin':  # macOS
                cache_dir = Path.home() / 'Library' / 'Caches' / 'PyPDF Tools v2'
            else:  # Linux
                cache_dir = Path.home() / '.cache' / 'pypdf-tools-v2'
            
            return cache_dir
        except Exception:
            return Path.home() / '.pypdf-cache'
    
    def _create_cache_directories(self):
        """Cache dizinlerini oluştur"""
        self.categories = {
            'thumbnails': self.cache_dir / 'thumbnails',
            'processed': self.cache_dir / 'processed',
            'temp': self.cache_dir / 'temp',
            'ocr': self.cache_dir / 'ocr'
        }
        
        for category_path in self.categories.values():
            category_path.mkdir(parents=True, exist_ok=True)
    
    def set_enabled(self, enabled: bool):
        """Cache durumunu ayarla"""
        self.enabled = enabled
        if enabled:
            try:
                self._create_cache_directories()
            except Exception as e:
                print(f"⚠️ Cache etkinleştirilemedi: {e}")
                self.enabled = False
        elif not enabled:
            self.clear_all()
    
    def clear_all(self):
        """Tüm cache'i temizle - güvenli"""
        try:
            if hasattr(self, 'cache_dir') and self.cache_dir.exists():
                shutil.rmtree(self.cache_dir, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Cache temizleme hatası: {e}")

class LogManager:
    """Loglama sistemi - DÜZELTİLMİŞ"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.logger = None
        
        if self.enabled:
            try:
                self.log_dir = self._get_log_directory()
                self.setup_logger()
            except Exception as e:
                print(f"⚠️ Log sistemi başlatılamadı: {e}")
                self.enabled = False
    
    def _get_log_directory(self) -> Path:
        """Log dizini - güvenli"""
        try:
            if os.name == 'nt':  # Windows
                log_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'PyPDF Tools v2' / 'Logs'
            elif platform.system() == 'Darwin':  # macOS
                log_dir = Path.home() / 'Library' / 'Logs' / 'PyPDF Tools v2'
            else:  # Linux
                log_dir = Path.home() / '.local' / 'share' / 'pypdf-tools-v2' / 'logs'
            
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir
        except Exception:
            return Path.home() / '.pypdf-logs'
    
    def setup_logger(self):
        """Logger kurulumu - hata korumalı"""
        try:
            self.logger = logging.getLogger('PyPDFToolsV2')
            self.logger.setLevel(logging.DEBUG)
            
            # Mevcut handler'ları temizle
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # File handler
            log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"⚠️ Logger kurulum hatası: {e}")
            self.logger = None
    
    def _log(self, level: str, message: str):
        """Güvenli loglama"""
        try:
            if self.enabled and self.logger:
                getattr(self.logger, level.lower())(message)
        except:
            pass  # Sessizce geç
    
    def debug(self, message: str):
        self._log('DEBUG', message)
    
    def info(self, message: str):
        self._log('INFO', message)
    
    def warning(self, message: str):
        self._log('WARNING', message)
    
    def error(self, message: str):
        self._log('ERROR', message)
    
    def set_level(self, level):
        if self.logger:
            self.logger.setLevel(level)

class ThemeManager:
    """Tema yönetim sistemi - DÜZELTİLMİŞ"""
    
    def __init__(self):
        self.current_theme = 'light'
        self.themes = {
            'light': {
                'name': 'Aydınlık',
                'colors': {
                    'bg_primary': '#ffffff',
                    'bg_secondary': '#f8fafc',
                    'text_primary': '#0f172a',
                    'text_secondary': '#475569',
                    'accent': '#3b82f6'
                }
            },
            'dark': {
                'name': 'Karanlık',
                'colors': {
                    'bg_primary': '#0f172a',
                    'bg_secondary': '#1e293b',
                    'text_primary': '#f8fafc',
                    'text_secondary': '#cbd5e1',
                    'accent': '#60a5fa'
                }
            },
            'neon': {
                'name': 'Neon',
                'colors': {
                    'bg_primary': '#0a0a0a',
                    'bg_secondary': '#1a1a1a',
                    'text_primary': '#ffffff',
                    'text_secondary': '#a3a3a3',
                    'accent': '#00ffff'
                }
            },
            'midnight': {
                'name': 'Gece Yarısı',
                'colors': {
                    'bg_primary': '#0c1426',
                    'bg_secondary': '#162544',
                    'text_primary': '#e2e8f0',
                    'text_secondary': '#94a3b8',
                    'accent': '#0ea5e9'
                }
            }
        }
    
    def get_available_themes(self) -> List[str]:
        return list(self.themes.keys())
    
    def apply_theme(self, theme_name: str, root_widget):
        """Tema uygula - hata korumalı"""
        try:
            if theme_name not in self.themes:
                theme_name = 'light'
            
            self.current_theme = theme_name
            theme = self.themes[theme_name]
            colors = theme['colors']
            
            # Temel renk ayarları
            root_widget.configure(bg=colors['bg_primary'])
            
            # TTK stilleri (varsa)
            try:
                import tkinter.ttk as ttk
                style = ttk.Style()
                
                # Temel stiller
                style.configure('TFrame', background=colors['bg_primary'])
                style.configure('TLabel', background=colors['bg_primary'], 
                               foreground=colors['text_primary'])
                style.configure('TButton', background=colors['bg_secondary'])
                
            except Exception:
                pass  # TTK mevcut değilse geç
            
        except Exception as e:
            print(f"⚠️ Tema uygulama hatası: {e}")

# Utility fonksiyonları - DÜZELTİLMİŞ

def get_resource_path(relative_path: str) -> Path:
    """Kaynak dosya yolu - PyInstaller uyumlu - DÜZELTİLMİŞ"""
    try:
        # PyInstaller kontrolü
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = Path(__file__).parent
        
        return Path(base_path) / relative_path
    except Exception:
        return Path(__file__).parent / relative_path

def ensure_single_instance():
    """Tek instance kontrolü - cross-platform"""
    try:
        lock_file = Path(tempfile.gettempdir()) / 'pypdf_tools_v2.lock'
        
        if os.name == 'nt':  # Windows
            try:
                # Windows için basit dosya kontrolü
                if lock_file.exists():
                    return False, None
                lock_file.touch()
                return True, lock_file
            except:
                return True, None
        else:  # Unix-like
            try:
                import fcntl
                lock_handle = open(lock_file, 'w')
                fcntl.lockf(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True, lock_handle
            except (ImportError, IOError):
                return True, None
    except:
        return True, None

def validate_email(email: str) -> bool:
    """E-posta doğrulama - basit"""
    try:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
        return bool(re.match(pattern, email))
    except:
        return False

def format_duration(seconds: float) -> str:
    """Süre formatlama"""
    try:
        if seconds < 60:
            return f"{seconds:.1f} saniye"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}:{secs:02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}:{minutes:02d}:00"
    except:
        return "Bilinmiyor"

class UpdateChecker:
    """Güncelleme kontrolü - REQUESTS_AVAILABLE kontrolü ile"""
    
    def __init__(self, current_version: str, check_url: str = None):
        self.current_version = current_version
        self.check_url = check_url or "https://api.github.com/repos/Fatih-Bucaklioglu/PyPDF-Tools-v2/releases/latest"
    
    def check_for_updates(self) -> Dict:
        """Güncelleme kontrol et"""
        if not REQUESTS_AVAILABLE:
            return {'update_available': False, 'error': 'requests modülü mevcut değil'}
        
        try:
            import requests
            response = requests.get(self.check_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', '').lstrip('v')
                
                return {
                    'update_available': self._compare_versions(latest_version, self.current_version) > 0,
                    'latest_version': latest_version,
                    'current_version': self.current_version,
                    'download_url': data.get('html_url', '')
                }
        except Exception as e:
            return {'update_available': False, 'error': str(e)}
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Versiyon karşılaştır"""
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except:
            return 0

# Singleton pattern
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

# Export edilenler - DÜZELTİLMİŞ
__all__ = [
    'ConfigManager',
    'CacheManager', 
    'LogManager',
    'ThemeManager',
    'UpdateChecker',
    'singleton',
    'ensure_single_instance',
    'get_resource_path',
    'format_duration',
    'validate_email',
    'REQUESTS_AVAILABLE',
    'PSUTIL_AVAILABLE'
]

# Modül testi
if __name__ == "__main__":
    print("🧪 Utils modül testi")
    print("-" * 30)
    
    # ConfigManager testi
    try:
        config = ConfigManager()
        print("✅ ConfigManager: OK")
    except Exception as e:
        print(f"❌ ConfigManager: {e}")
    
    # LogManager testi
    try:
        log = LogManager(enabled=False)
        print("✅ LogManager: OK")
    except Exception as e:
        print(f"❌ LogManager: {e}")
    
    # ThemeManager testi
    try:
        theme = ThemeManager()
        print(f"✅ ThemeManager: OK ({len(theme.get_available_themes())} tema)")
    except Exception as e:
        print(f"❌ ThemeManager: {e}")
    
    print(f"\n📦 İsteğe bağlı modüller:")
    print(f"   requests: {'✅' if REQUESTS_AVAILABLE else '❌'}")
    print(f"   psutil: {'✅' if PSUTIL_AVAILABLE else '❌'}")