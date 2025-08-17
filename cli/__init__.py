#!/usr/bin/env python3
"""
PyPDF-Tools CLI Package
Command Line Interface for PyPDF-Tools
"""

__version__ = "2.0.0"
__author__ = "Fatih Bucaklıoğlu"
__email__ = "fatih@pypdf-tools.com"

from .cli_handler import main, CLIHandler, CLIColors

__all__ = [
    'main',
    'CLIHandler', 
    'CLIColors'
]
