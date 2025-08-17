#!/usr/bin/env python3
"""
PyPDF-Tools setup.py
Modern, Güçlü ve Kullanıcı Dostu PDF İşleme Uygulaması
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Python version check
if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or higher is required")

# Read version from __init__.py
def get_version():
    """Versiyon bilgisini __init__.py dosyasından okur."""
    version_file = Path("src/pypdf_tools/__init__.py")
    if not version_file.exists():
        return "2.0.0"  # Fallback version
    
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "2.0.0"

# Read README.md for long description
def get_long_description():
    """README.md dosyasını okur."""
    readme_file = Path("README.md")
    if readme_file.exists():
        with open(readme_file, encoding='utf-8') as f:
            return f.read()
    return "Modern PDF processing application inspired by Stirling-PDF"

# Read requirements
def get_requirements(filename):
    """Requirements dosyasını okur."""
    req_file = Path(filename)
    if not req_file.exists():
        return []
    
    with open(req_file, encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements

# Platform-specific requirements
def get_platform_requirements():
    """Platform-specific requirements."""
    requirements = []
    
    # Windows specific
    if sys.platform == "win32":
        requirements.extend([
            "pywin32>=306",
            "winsound",
        ])
    
    # macOS specific  
    elif sys.platform == "darwin":
        requirements.extend([
            "pyobjc-framework-Cocoa>=9.0",
        ])
    
    # Linux specific
    elif sys.platform.startswith("linux"):
        requirements.extend([
            "python3-gi",
        ])
    
    return requirements

# Core requirements
CORE_REQUIREMENTS = [
    # GUI Framework
    "PyQt6>=6.5.0",
    "PyQt6-Qt6>=6.5.0",
    
    # PDF Processing
    "PyPDF2>=3.0.0",
    "pymupdf>=1.23.0",
    "reportlab>=4.0.0",
    
    # Image Processing
    "Pillow>=10.0.0",
    "opencv-python>=4.8.0",
    
    # OCR
    "pytesseract>=0.3.10",
    "tesseract>=0.1.3",
    
    # Document Conversion
    "python-docx>=1.0.0",
    "openpyxl>=3.1.0",
    "python-pptx>=0.6.21",
    
    # Utilities
    "psutil>=5.9.0",
    "requests>=2.31.0",
    "packaging>=23.0",
    "appdirs>=1.4.4",
    "send2trash>=1.8.2",
    
    # Logging & Config
    "colorlog>=6.7.0",
    "pyyaml>=6.0",
    "toml>=0.10.2",
    
    # Threading & Async
    "concurrent-futures>=3.1.1",
    
    # Compression
    "zstandard>=0.21.0",
    
    # Encryption
    "cryptography>=41.0.0",
]

# Development requirements
DEV_REQUIREMENTS = [
    # Testing
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "pytest-qt>=4.2.0",
    "pytest-xvfb>=3.0.0",
    "pytest-timeout>=2.1.0",
    
    # Code Quality
    "black>=23.7.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "pylint>=2.17.0",
    "mypy>=1.5.0",
    
    # Pre-commit
    "pre-commit>=3.3.0",
    
    # Documentation
    "sphinx>=7.1.0",
    "sphinx-rtd-theme>=1.3.0",
    "sphinx-autodoc-typehints>=1.24.0",
    
    # Build tools
    "build>=0.10.0",
    "wheel>=0.41.0",
    "twine>=4.0.0",
]

# Optional requirements for specific features
EXTRA_REQUIREMENTS = {
    'ocr': [
        "easyocr>=1.7.0",
        "paddlepaddle>=2.5.0",
        "paddleocr>=2.7.0",
    ],
    'ai': [
        "transformers>=4.33.0",
        "torch>=2.0.0",
        "opencv-python>=4.8.0",
    ],
    'cloud': [
        "boto3>=1.28.0",
        "google-cloud-storage>=2.10.0",
        "dropbox>=11.36.0",
    ],
    'dev': DEV_REQUIREMENTS,
    'all': DEV_REQUIREMENTS + [
        "easyocr>=1.7.0",
        "transformers>=4.33.0",
        "boto3>=1.28.0",
    ]
}

# Entry points
ENTRY_POINTS = {
    'console_scripts': [
        'pypdf-tools=pypdf_tools.main:main',
        'pypdf-cli=pypdf_tools.cli.cli_handler:main',
        'pypdf-setup=pypdf_tools.setup:setup_wizard',
    ],
    'gui_scripts': [
        'pypdf-tools-gui=pypdf_tools.main:main_gui',
    ]
}

# Classifiers
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business",
    "Topic :: Utilities",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Text Processing",
    "Environment :: X11 Applications :: Qt",
    "Environment :: Win32 (MS Windows)",
    "Environment :: MacOS X",
]

# Keywords
KEYWORDS = [
    "pdf", "merge", "split", "compress", "ocr", "convert", 
    "gui", "desktop", "tool", "utility", "document", 
    "processing", "qt6", "cross-platform", "stirling-pdf"
]

# Package data
PACKAGE_DATA = {
    'pypdf_tools': [
        'ui/themes/*.qss',
        'ui/icons/*.png',
        'ui/icons/*.svg',
        'ui/icons/*.ico',
        'ui/translations/*.qm',
        'ui/translations/*.ts',
        'templates/*.py',
        'configs/*.yaml',
        'configs/*.json',
        'resources/*',
    ]
}

# Data files for system integration
DATA_FILES = []

# Linux desktop integration
if sys.platform.startswith('linux'):
    DATA_FILES.extend([
        ('share/applications', ['packages/linux/pypdf-tools-v2.desktop']),
        ('share/icons/hicolor/48x48/apps', ['icons/app_icon.png']),
        ('share/icons/hicolor/scalable/apps', ['icons/app_icon.svg']),
        ('share/pixmaps', ['icons/app_icon.png']),
    ])

# Setup configuration
setup(
    # Basic info
    name="pypdf-tools",
    version=get_version(),
    description="Modern, Powerful and User-Friendly PDF Processing Application",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # URLs and author info
    url="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools",
    project_urls={
        "Bug Reports": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues",
        "Feature Requests": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues/new?template=feature_request.md",
        "Source": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools",
        "Documentation": "https://pypdf-tools.readthedocs.io/",
        "Changelog": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/blob/main/CHANGELOG.md",
        "Discord": "https://discord.gg/pypdf-tools",
        "Telegram": "https://t.me/pypdf_tools",
    },
    
    author="Fatih Bucaklıoğlu",
    author_email="fatih@pypdf-tools.com",
    maintainer="Fatih Bucaklıoğlu",
    maintainer_email="fatih@pypdf-tools.com",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=PACKAGE_DATA,
    data_files=DATA_FILES,
    include_package_data=True,
    zip_safe=False,
    
    # Requirements
    python_requires=">=3.8",
    install_requires=CORE_REQUIREMENTS + get_platform_requirements(),
    extras_require=EXTRA_REQUIREMENTS,
    
    # Entry points
    entry_points=ENTRY_POINTS,
    
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=" ".join(KEYWORDS),
    license="MIT",
    platforms=["Windows", "macOS", "Linux"],
    
    # Options
    options={
        'build_py': {
            'compile': True,
            'optimize': 2,
        },
        'bdist_wheel': {
            'universal': False,
        },
        'egg_info': {
            'tag_build': None,
            'tag_date': False,
        }
    },
    
    # Additional metadata
    download_url="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/archive/v{}.tar.gz".format(get_version()),
    
    # Security
    obsoletes_dist=["old-pypdf-tools"],
)

# Post-install message
def post_install_message():
    """Kurulum sonrası mesaj gösterir."""
    print("\n" + "="*60)
    print("🎉 PyPDF-Tools v{} başarıyla kuruldu!".format(get_version()))
    print("="*60)
    print("\n📋 Kullanım:")
    print("  GUI Modu    : pypdf-tools")  
    print("  CLI Modu    : pypdf-cli --help")
    print("  Kurulum     : pypdf-setup")
    print("\n🔗 Bağlantılar:")
    print("  GitHub      : https://github.com/Fatih-Bucaklioglu/PyPDF-Tools")
    print("  Dokümantasyon: https://pypdf-tools.readthedocs.io/")
    print("  Discord     : https://discord.gg/pypdf-tools")
    print("\n💡 İlk kez kullanıyorsanız:")
    print("  pypdf-setup komutunu çalıştırarak kurulum sihirbazını başlatın!")
    print("\n" + "="*60 + "\n")

# Run post-install message if this is being run directly
if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "install":
    import atexit
    atexit.register(post_install_message)
