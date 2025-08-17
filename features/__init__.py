#!/usr/bin/env python3
"""
Gelişmiş Özellikler Paketi
PyPDF-Tools v2.0 gelişmiş fonksiyonları
"""

__version__ = "2.0.0"
__author__ = "Fatih Bucaklıoğlu"
__email__ = "fatih@pypdf-tools.com"

# Ana modüller
from .script_engine import ScriptEngine, ScriptManager
from .automation_engine import AutomationEngine, AutomationRule
from .pdf_viewer import PDFViewer, PDFViewerWidget
from .language_installer import LanguageInstaller, OCRLanguageManager

# Hızlı erişim için sınıfları expose et
__all__ = [
    # Script Engine
    'ScriptEngine',
    'ScriptManager',
    
    # Automation System
    'AutomationEngine', 
    'AutomationRule',
    
    # PDF Viewer
    'PDFViewer',
    'PDFViewerWidget',
    
    # Language Management
    'LanguageInstaller',
    'OCRLanguageManager',
]

# Feature flags - özellik kontrolü için
FEATURES = {
    'script_engine': True,
    'automation_system': True, 
    'pdf_viewer': True,
    'language_installer': True,
    'advanced_ocr': True,
    'batch_processing': True,
    'cloud_integration': False,  # v2.1 için planlanmış
    'ai_features': False,        # v2.2 için planlanmış
}

def is_feature_enabled(feature_name: str) -> bool:
    """
    Özelliğin aktif olup olmadığını kontrol et
    
    Args:
        feature_name: Özellik adı
        
    Returns:
        bool: Özellik aktif mi?
    """
    return FEATURES.get(feature_name, False)

def get_available_features():
    """
    Kullanılabilir özelliklerin listesini döndür
    
    Returns:
        list: Aktif özellikler listesi
    """
    return [name for name, enabled in FEATURES.items() if enabled]
