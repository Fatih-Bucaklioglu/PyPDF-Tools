#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools - Hibrit PDF Yönetim ve Düzenleme Uygulaması

Bu paket, PyQt6 ve React teknolojilerini kullanarak modern bir hibrit 
masaüstü PDF uygulaması sağlar.

Author: Fatih Bucaklıoğlu
License: MIT
"""

from pypdf_tools._version import (
    __version__,
    __version_tuple__,
    APP_NAME,
    APP_DISPLAY_NAME,
    APP_DESCRIPTION,
    APP_AUTHOR,
    APP_URL
)

# Ana bileşenleri export et
from pypdf_tools.main import MainWindow, create_app
from pypdf_tools.features.pdf_viewer import (
    PDFViewerWidget, 
    PDFViewerContainer,
    PDFJSBridge
)

# CLI handler
from pypdf_tools.cli.cli_handler import cli

# Public API
__all__ = [
    # Version info
    '__version__',
    '__version_tuple__',
    'APP_NAME',
    'APP_DISPLAY_NAME', 
    'APP_DESCRIPTION',
    'APP_AUTHOR',
    'APP_URL',
    
    # Main classes
    'MainWindow',
    'create_app',
    'PDFViewerWidget',
    'PDFViewerContainer',
    'PDFJSBridge',
    
    # CLI
    'cli'
]

# Package metadata
__title__ = APP_NAME
__summary__ = APP_DESCRIPTION
__author__ = APP_AUTHOR
__email__ = 'fatih.bucaklioglu@example.com'
__license__ = 'MIT'
__copyright__ = f'2024 {APP_AUTHOR}'
__url__ = APP_URL

# Compatibility check
import sys

if sys.version_info < (3, 8):
    raise RuntimeError(
        f"{APP_DISPLAY_NAME} requires Python 3.8 or higher. "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# PyQt6 availability check
try:
    from PyQt6.QtCore import QT_VERSION_STR
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    _QT_AVAILABLE = True
    _QT_VERSION = QT_VERSION_STR
except ImportError as e:
    _QT_AVAILABLE = False
    _QT_VERSION = None
    _QT_IMPORT_ERROR = str(e)

def get_version_info():
    """Paket sürüm ve bağımlılık bilgilerini döndür."""
    import platform
    
    info = {
        'pypdf_tools_version': __version__,
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
    }
    
    if _QT_AVAILABLE:
        info['qt_version'] = _QT_VERSION
        info['pyqt6_available'] = True
    else:
        info['pyqt6_available'] = False
        info['pyqt6_error'] = _QT_IMPORT_ERROR
    
    # PDF processing libraries
    try:
        import pypdf
        info['pypdf_version'] = pypdf.__version__
    except ImportError:
        info['pypdf_version'] = None
    
    try:
        import PyPDF2
        info['pypdf2_version'] = PyPDF2.__version__
    except ImportError:
        info['pypdf2_version'] = None
    
    return info

def check_dependencies():
    """Bağımlılıkları kontrol et ve eksikleri bildir."""
    missing_deps = []
    warnings = []
    
    # Critical dependencies
    if not _QT_AVAILABLE:
        missing_deps.append(('PyQt6 & PyQt6-WebEngine', 'GUI functionality'))
    
    try:
        import pypdf
    except ImportError:
        try:
            import PyPDF2
            warnings.append('PyPDF2 found but pypdf recommended for better performance')
        except ImportError:
            missing_deps.append(('pypdf or PyPDF2', 'PDF processing'))
    
    try:
        import click
    except ImportError:
        missing_deps.append(('click', 'CLI functionality'))
    
    # Optional dependencies
    try:
        import PIL
    except ImportError:
        warnings.append('Pillow not found - image processing may be limited')
    
    return {
        'missing_critical': missing_deps,
        'warnings': warnings,
        'all_good': len(missing_deps) == 0
    }

# İlk import sırasında temel kontroller
_dep_check = check_dependencies()
if not _dep_check['all_good']:
    import warnings as _warnings
    for dep, purpose in _dep_check['missing_critical']:
        _warnings.warn(
            f"Missing dependency: {dep} (needed for {purpose})",
            ImportWarning,
            stacklevel=2
        )

# Module-level convenience functions
def create_application():
    """PyQt uygulamasını oluştur ve döndür."""
    if not _QT_AVAILABLE:
        raise ImportError("PyQt6 is required to create GUI application")
    return create_app()

def launch_gui(file_path=None):
    """GUI uygulamasını başlat."""
    if not _QT_AVAILABLE:
        raise ImportError("PyQt6 is required for GUI functionality")
    
    app = create_application()
    main_window = MainWindow()
    
    if file_path:
        main_window.load_pdf(file_path)
    
    main_window.show()
    return app.exec()

def run_cli():
    """CLI uygulamasını çalıştır."""
    from pypdf_tools.cli.cli_handler import cli_main
    return cli_main()

# Development helpers
def _development_info():
    """Development ortamı için debug bilgileri."""
    import os
    import subprocess
    
    try:
        # Git bilgisi
        git_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], 
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL
        ).decode().strip()[:8]
    except:
        git_commit = 'unknown'
    
    return {
        'git_commit': git_commit,
        'debug_mode': os.environ.get('PYPDF_DEBUG', '0') == '1',
        'package_path': os.path.dirname(__file__),
    }
