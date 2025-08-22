#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools Setup Configuration
Hibrit PDF yönetim uygulaması için setuptools yapılandırması
"""

import os
from setuptools import setup, find_packages

# Proje dizin yolu
here = os.path.abspath(os.path.dirname(__file__))

# README dosyasını oku
with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# Version dosyasından sürüm bilgisini oku
version_dict = {}
with open(os.path.join(here, 'src', 'pypdf_tools', '_version.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), version_dict)

setup(
    name="pypdf-tools",
    version=version_dict['__version__'],
    author="Fatih Bucaklıoğlu",
    author_email="fatih.bucaklioglu@example.com",  # Gerçek email adresi ile değiştirin
    description="Hibrit masaüstü PDF yönetim ve düzenleme uygulaması",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fatih-Bucaklioglu/PyPDF-Tools",
    project_urls={
        "Bug Reports": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/issues",
        "Source": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools",
        "Documentation": "https://github.com/Fatih-Bucaklioglu/PyPDF-Tools/docs",
    },
    
    # Paket yapılandırması
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # React build dosyalarını dahil et
    package_data={
        "pypdf_tools": [
            "web/build/*",
            "web/build/static/css/*",
            "web/build/static/js/*",
            "web/build/static/media/*",
            "resources/*",
            "assets/*"
        ]
    },
    include_package_data=True,
    
    # Python sürüm gereksinimleri
    python_requires=">=3.8",
    
    # Temel bağımlılıklar
    install_requires=[
        # PyQt6 ve WebEngine
        "PyQt6>=6.4.0",
        "PyQt6-WebEngine>=6.4.0",
        
        # PDF işleme kütüphaneleri
        "PyPDF2>=3.0.0",
        "pypdf>=3.0.0",
        "reportlab>=4.0.0",
        "Pillow>=9.0.0",
        
        # CLI ve yapılandırma
        "click>=8.0.0",
        "pyyaml>=6.0",
        "toml>=0.10.0",
        
        # İsteğe bağlı özellikler için
        "requests>=2.28.0",
        "cryptography>=3.4.8",
    ],
    
    # Ek bağımlılıklar (opsiyonel özellikler)
    extras_require={
        "ai": [
            "openai>=0.27.0",
            "transformers>=4.21.0",
            "torch>=1.12.0"
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "opencv-python>=4.6.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950"
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "wheel>=0.37.0"
        ]
    },
    
    # Komut satırı araçları
    entry_points={
        "console_scripts": [
            "pypdf-tools=pypdf_tools.main:main",
            "pypdf=pypdf_tools.cli.cli_handler:cli_main",
        ],
        "gui_scripts": [
            "pypdf-tools-gui=pypdf_tools.main:main_gui",
        ]
    },
    
    # Sınıflandırma
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: JavaScript",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: General",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Environment :: X11 Applications :: Qt",
        "Framework :: Qt"
    ],
    
    # Lisans
    license="MIT",
    
    # Anahtar kelimeler
    keywords="pdf, editor, viewer, annotation, merge, split, gui, desktop, qt, react",
    
    # Zip dosyası olarak kurulum
    zip_safe=False,
)
