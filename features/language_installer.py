"""
OCR Dil Paketi Yöneticisi
PyPDF-Tools projesi için Tesseract OCR dil paketlerinin kurulumu ve yönetimi
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from urllib.parse import urljoin

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LanguagePackage:
    """Dil paketi bilgilerini tutan sınıf"""
    code: str
    name: str
    english_name: str
    size: str
    version: str
    url: str
    installed: bool = False

class LanguageInstaller:
    """OCR dil paketlerinin kurulumu ve yönetimini sağlar"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.tesseract_path = self._find_tesseract()
        self.data_path = self._get_tessdata_path()
        self.cache_dir = self._get_cache_dir()
        self.config_file = self._get_config_file()
        
        # Tesseract dil paketleri listesi
        self.available_languages = self._load_language_list()
        
        # Cache dizinini oluştur
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _find_tesseract(self) -> Optional[str]:
        """Tesseract OCR kurulumunu bulur"""
        tesseract_paths = []
        
        if self.system == "windows":
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Tools\tesseract\tesseract.exe"
            ]
        elif self.system == "darwin":  # macOS
            tesseract_paths = [
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
                "/usr/bin/tesseract"
            ]
        else:  # Linux
            tesseract_paths = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
                "/opt/tesseract/bin/tesseract"
            ]
        
        # PATH'te arama
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            return tesseract_path
        
        # Belirli yollarda arama
        for path in tesseract_paths:
            if os.path.isfile(path):
                return path
        
        logger.warning("Tesseract OCR bulunamadı!")
        return None
    
    def _get_tessdata_path(self) -> Optional[str]:
        """Tesseract veri dizinini bulur"""
        if not self.tesseract_path:
            return None
        
        try:
            # Tesseract --print-parameters ile veri dizinini öğren
            result = subprocess.run(
                [self.tesseract_path, "--print-parameters"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'tessdata' in line and 'dir' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
            
            # Varsayılan yolları dene
            tesseract_dir = os.path.dirname(self.tesseract_path)
            possible_paths = [
                os.path.join(tesseract_dir, "tessdata"),
                os.path.join(os.path.dirname(tesseract_dir), "share", "tessdata"),
                "/usr/share/tesseract-ocr/4.00/tessdata",
                "/usr/share/tesseract-ocr/tessdata"
            ]
            
            for path in possible_paths:
                if os.path.isdir(path):
                    return path
            
        except Exception as e:
            logger.error(f"Tessdata dizini bulunamadı: {e}")
        
        return None
    
    def _get_cache_dir(self) -> str:
        """Cache dizini yolunu döndürür"""
        if self.system == "windows":
            cache_dir = os.path.join(os.getenv("APPDATA", ""), "PyPDF Tools v2", "cache", "ocr")
        elif self.system == "darwin":
            cache_dir = os.path.expanduser("~/Library/Application Support/PyPDF Tools v2/cache/ocr")
        else:
            cache_dir = os.path.expanduser("~/.config/PyPDF Tools v2/cache/ocr")
        
        return cache_dir
    
    def _get_config_file(self) -> str:
        """Yapılandırma dosyası yolunu döndürür"""
        if self.system == "windows":
            config_dir = os.path.join(os.getenv("APPDATA", ""), "PyPDF Tools v2")
        elif self.system == "darwin":
            config_dir = os.path.expanduser("~/Library/Application Support/PyPDF Tools v2")
        else:
            config_dir = os.path.expanduser("~/.config/PyPDF Tools v2")
        
        return os.path.join(config_dir, "ocr_languages.json")
    
    def _load_language_list(self) -> List[LanguagePackage]:
        """Mevcut dil paketlerinin listesini yükler"""
        languages = [
            LanguagePackage("tur", "Türkçe", "Turkish", "2.1 MB", "4.1.0", 
                          "https://github.com/tesseract-ocr/tessdata/raw/main/tur.traineddata"),
            LanguagePackage("eng", "İngilizce", "English", "10.1 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata"),
            LanguagePackage("deu", "Almanca", "German", "2.3 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"),
            LanguagePackage("fra", "Fransızca", "French", "2.4 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata"),
            LanguagePackage("spa", "İspanyolca", "Spanish", "2.2 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata"),
            LanguagePackage("ita", "İtalyanca", "Italian", "2.5 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/ita.traineddata"),
            LanguagePackage("por", "Portekizce", "Portuguese", "2.3 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata"),
            LanguagePackage("rus", "Rusça", "Russian", "4.2 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata"),
            LanguagePackage("ara", "Arapça", "Arabic", "2.8 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata"),
            LanguagePackage("chi_sim", "Çince (Basit)", "Chinese (Simplified)", "11.2 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata"),
            LanguagePackage("chi_tra", "Çince (Geleneksel)", "Chinese (Traditional)", "15.1 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/chi_tra.traineddata"),
            LanguagePackage("jpn", "Japonca", "Japanese", "7.8 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata"),
            LanguagePackage("kor", "Korece", "Korean", "6.9 MB", "4.1.0",
                          "https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata"),
        ]
        
        # Kurulu dilleri kontrol et
        for lang in languages:
            lang.installed = self.is_language_installed(lang.code)
        
        return languages
    
    def is_language_installed(self, lang_code: str) -> bool:
        """Belirtilen dil paketinin kurulu olup olmadığını kontrol eder"""
        if not self.data_path:
            return False
        
        traineddata_file = os.path.join(self.data_path, f"{lang_code}.traineddata")
        return os.path.isfile(traineddata_file)
    
    def get_installed_languages(self) -> List[str]:
        """Kurulu dil paketlerinin listesini döndürür"""
        if not self.data_path:
            return []
        
        installed = []
        for lang in self.available_languages:
            if self.is_language_installed(lang.code):
                installed.append(lang.code)
        
        return installed
    
    def get_available_languages(self) -> List[LanguagePackage]:
        """Mevcut dil paketlerinin listesini döndürür"""
        return self.available_languages
    
    def download_language(self, lang_code: str, progress_callback=None) -> bool:
        """Dil paketini indirir"""
        lang_pack = None
        for lang in self.available_languages:
            if lang.code == lang_code:
                lang_pack = lang
                break
        
        if not lang_pack:
            logger.error(f"Dil paketi bulunamadı: {lang_code}")
            return False
        
        if not self.data_path:
            logger.error("Tesseract veri dizini bulunamadı!")
            return False
        
        try:
            # Dosyayı cache dizinine indir
            cache_file = os.path.join(self.cache_dir, f"{lang_code}.traineddata")
            
            logger.info(f"{lang_pack.name} dil paketi indiriliyor...")
            
            response = requests.get(lang_pack.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            logger.info(f"{lang_pack.name} dil paketi başarıyla indirildi!")
            return True
            
        except Exception as e:
            logger.error(f"Dil paketi indirme hatası: {e}")
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return False
    
    def install_language(self, lang_code: str, progress_callback=None) -> bool:
        """Dil paketini kurar"""
        if self.is_language_installed(lang_code):
            logger.info(f"Dil paketi zaten kurulu: {lang_code}")
            return True
        
        # Önce indir
        if not self.download_language(lang_code, progress_callback):
            return False
        
        try:
            # Cache'den tessdata dizinine kopyala
            cache_file = os.path.join(self.cache_dir, f"{lang_code}.traineddata")
            target_file = os.path.join(self.data_path, f"{lang_code}.traineddata")
            
            if progress_callback:
                progress_callback(90)
            
            shutil.copy2(cache_file, target_file)
            
            # İzinleri ayarla (Linux/macOS için)
            if self.system != "windows":
                os.chmod(target_file, 0o644)
            
            # Cache dosyasını temizle
            os.remove(cache_file)
            
            # Kurulum durumunu güncelle
            for lang in self.available_languages:
                if lang.code == lang_code:
                    lang.installed = True
                    break
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"Dil paketi başarıyla kuruldu: {lang_code}")
            return True
            
        except Exception as e:
            logger.error(f"Dil paketi kurulum hatası: {e}")
            return False
    
    def uninstall_language(self, lang_code: str) -> bool:
        """Dil paketini kaldırır"""
        if not self.is_language_installed(lang_code):
            logger.info(f"Dil paketi zaten kurulu değil: {lang_code}")
            return True
        
        # İngilizce paketini kaldırmaya izin verme
        if lang_code == "eng":
            logger.warning("İngilizce dil paketi kaldırılamaz!")
            return False
        
        try:
            target_file = os.path.join(self.data_path, f"{lang_code}.traineddata")
            os.remove(target_file)
            
            # Kurulum durumunu güncelle
            for lang in self.available_languages:
                if lang.code == lang_code:
                    lang.installed = False
                    break
            
            logger.info(f"Dil paketi başarıyla kaldırıldı: {lang_code}")
            return True
            
        except Exception as e:
            logger.error(f"Dil paketi kaldırma hatası: {e}")
            return False
    
    def install_multiple_languages(self, lang_codes: List[str], progress_callback=None) -> Dict[str, bool]:
        """Birden fazla dil paketini kurar"""
        results = {}
        total_langs = len(lang_codes)
        
        for i, lang_code in enumerate(lang_codes):
            def lang_progress(progress):
                if progress_callback:
                    overall_progress = (i / total_langs) * 100 + (progress / total_langs)
                    progress_callback(overall_progress)
            
            results[lang_code] = self.install_language(lang_code, lang_progress)
        
        return results
    
    def validate_installation(self, lang_code: str) -> bool:
        """Dil paketi kurulumunu doğrular"""
        if not self.tesseract_path or not self.is_language_installed(lang_code):
            return False
        
        try:
            # Tesseract ile dil paketini test et
            result = subprocess.run(
                [self.tesseract_path, "--list-langs"],
                capture_output=True,
                text=True
            )
            
            return lang_code in result.stdout
            
        except Exception as e:
            logger.error(f"Dil paketi doğrulama hatası: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, str]:
        """Sistem bilgilerini döndürür"""
        info = {
            "system": self.system,
            "tesseract_path": self.tesseract_path or "Bulunamadı",
            "tessdata_path": self.data_path or "Bulunamadı",
            "cache_dir": self.cache_dir,
        }
        
        if self.tesseract_path:
            try:
                result = subprocess.run(
                    [self.tesseract_path, "--version"],
                    capture_output=True,
                    text=True
                )
                version_line = result.stdout.split('\n')[0]
                info["tesseract_version"] = version_line
            except:
                info["tesseract_version"] = "Sürüm bilgisi alınamadı"
        
        return info
    
    def save_config(self):
        """Yapılandırmayı dosyaya kaydeder"""
        config = {
            "installed_languages": self.get_installed_languages(),
            "last_update": str(os.path.getmtime(__file__))
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

def main():
    """Test ve demo amaçlı ana fonksiyon"""
    installer = LanguageInstaller()
    
    print("=== OCR Dil Paketi Yöneticisi ===\n")
    
    # Sistem bilgileri
    info = installer.get_system_info()
    print("Sistem Bilgileri:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nMevcut Dil Paketleri:")
    for lang in installer.get_available_languages():
        status = "✓" if lang.installed else "✗"
        print(f"  {status} {lang.code}: {lang.name} ({lang.size})")
    
    print(f"\nKurulu Diller: {', '.join(installer.get_installed_languages())}")

if __name__ == "__main__":
    main()
