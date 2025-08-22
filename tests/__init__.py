#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools Test Suite

Bu paket uygulamanın tüm test dosyalarını içerir.
"""

import os
import sys

# Test ortamı konfigürasyonu
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('PYPDF_TEST_MODE', '1')

# Test için gerekli path'leri ekle
test_dir = os.path.dirname(__file__)
src_dir = os.path.join(os.path.dirname(test_dir), 'src')

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
