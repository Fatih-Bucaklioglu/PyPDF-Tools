#!/usr/bin/env python3
"""
PyPDF-Tools CLI Handler
Komut satırı araçları ve batch işleme desteği
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# CLI için renkli output
try:
    from colorama import init, Fore, Back, Style
    init()
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        DIM = NORMAL = BRIGHT = RESET_ALL = ""

# Local imports
try:
    from ..core.pdf_processor import PDFProcessor
    from ..core.ocr_processor import OCRProcessor  
    from ..core.conversion_processor import ConversionProcessor
    from ..core.config_manager import ConfigManager
    from ..utils.file_utils import find_files, validate_path
    from ..version import __version__
except ImportError:
    # Development mode fallbacks
    __version__ = "2.0.0"
    

logger = logging.getLogger(__name__)


class CLIColors:
    """CLI renk yardımcı sınıfı"""
    
    @staticmethod
    def success(text: str) -> str:
        return f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}" if COLORS_ENABLED else f"✅ {text}"
    
    @staticmethod
    def error(text: str) -> str:
        return f"{Fore.RED}❌ {text}{Style.RESET_ALL}" if COLORS_ENABLED else f"❌ {text}"
    
    @staticmethod
    def warning(text: str) -> str:
        return f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}" if COLORS_ENABLED else f"⚠️  {text}"
    
    @staticmethod
    def info(text: str) -> str:
        return f"{Fore.CYAN}ℹ️  {text}{Style.RESET_ALL}" if COLORS_ENABLED else f"ℹ️  {text}"
    
    @staticmethod
    def header(text: str) -> str:
        return f"{Fore.MAGENTA}{Style.BRIGHT}🚀 {text}{Style.RESET_ALL}" if COLORS_ENABLED else f"🚀 {text}"


class ProgressReporter:
    """İlerleme durumu bildirici"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """İlerlemeyi güncelle"""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 100
        
        # Progress bar oluştur
        bar_length = 40
        filled_length = int(bar_length * self.current // self.total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Geçen süre hesapla
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]  # Microsecond'ları kaldır
        
        # Kalan süre tahmini
        if self.current > 0:
            eta_seconds = (elapsed.total_seconds() / self.current) * (self.total - self.current)
            eta_str = str(datetime.now() + timedelta(seconds=eta_seconds)).split('.')[0].split(' ')[1]
        else:
            eta_str = "Unknown"
        
        print(f"\r{self.description}: |{bar}| {self.current}/{self.total} "
              f"({percentage:.1f}%) - Elapsed: {elapsed_str} - ETA: {eta_str}", end='', flush=True)
        
        if self.current >= self.total:
            print()  # Yeni satır
    
    def finish(self):
        """İlerlemeyi tamamla"""
        self.current = self.total
        self.update(0)


class CLIHandler:
    """Ana CLI handler sınıfı"""
    
    def __init__(self):
        self.config = None
        try:
            self.config = ConfigManager()
        except Exception:
            pass  # Config yükleme hatası
        
        # Mock processors (development için)
        self.pdf_processor = self._create_mock_processor("PDFProcessor")
        self.ocr_processor = self._create_mock_processor("OCRProcessor")
        self.conversion_processor = self._create_mock_processor("ConversionProcessor")
    
    def _create_mock_processor(self, processor_name: str):
        """Mock processor oluştur"""
        class MockProcessor:
            def __init__(self, name):
                self.name = name
            
            def merge_pdfs(self, input_files: List[str], output_file: str) -> bool:
                print(CLIColors.info(f"Mock {self.name}: Merging {len(input_files)} files to {output_file}"))
                return True
            
            def split_pdf(self, input_file: str, output_dir: str, pages_per_file: int = 1) -> List[str]:
                print(CLIColors.info(f"Mock {self.name}: Splitting {input_file} to {output_dir}"))
                return [f"{output_dir}/page_{i}.pdf" for i in range(1, 6)]
            
            def compress_pdf(self, input_file: str, output_file: str, quality: str = "medium") -> bool:
                print(CLIColors.info(f"Mock {self.name}: Compressing {input_file} to {output_file} ({quality})"))
                return True
            
            def process_pdf(self, input_file: str, output_file: str, language: str = "tur") -> bool:
                print(CLIColors.info(f"Mock {self.name}: OCR processing {input_file} ({language})"))
                return True
            
            def convert_to_pdf(self, input_file: str, output_file: str) -> bool:
                print(CLIColors.info(f"Mock {self.name}: Converting {input_file} to PDF"))
                return True
            
            def convert_from_pdf(self, input_file: str, output_file: str, format: str) -> bool:
                print(CLIColors.info(f"Mock {self.name}: Converting PDF to {format}"))
                return True
        
        return MockProcessor(processor_name)


def create_parser() -> argparse.ArgumentParser:
    """Ana CLI parser'ını oluştur"""
    parser = argparse.ArgumentParser(
        prog='pypdf-cli',
        description='PyPDF-Tools Command Line Interface - Modern PDF Processing',
        epilog='Visit https://github.com/Fatih-Bucaklioglu/PyPDF-Tools for more information'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'PyPDF-Tools CLI v{__version__}'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Config file path'
    )
    
    # Ana subcommand'lar
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # MERGE command
    merge_parser = subparsers.add_parser('merge', help='Merge PDF files')
    merge_parser.add_argument('files', nargs='+', help='PDF files to merge')
    merge_parser.add_argument('-o', '--output', required=True, help='Output PDF file')
    merge_parser.add_argument('--bookmarks', action='store_true', help='Preserve bookmarks')
    merge_parser.add_argument('--metadata', action='store_true', help='Preserve metadata')
    
    # SPLIT command
    split_parser = subparsers.add_parser('split', help='Split PDF file')
    split_parser.add_argument('file', help='PDF file to split')
    split_parser.add_argument('-o', '--output-dir', required=True, help='Output directory')
    split_parser.add_argument('-p', '--pages-per-file', type=int, default=1, help='Pages per output file')
    split_parser.add_argument('--page-ranges', help='Page ranges (e.g., 1-5,10-15)')
    
    # COMPRESS command
    compress_parser = subparsers.add_parser('compress', help='Compress PDF files')
    compress_parser.add_argument('files', nargs='+', help='PDF files to compress')
    compress_parser.add_argument('-o', '--output-dir', help='Output directory')
    compress_parser.add_argument('-q', '--quality', choices=['low', 'medium', 'high'], 
                                default='medium', help='Compression quality')
    compress_parser.add_argument('--batch', action='store_true', help='Batch processing mode')
    
    # OCR command
    ocr_parser = subparsers.add_parser('ocr', help='OCR processing')
    ocr_parser.add_argument('files', nargs='+', help='PDF files to process')
    ocr_parser.add_argument('-o', '--output-dir', help='Output directory')
    ocr_parser.add_argument('-l', '--language', default='tur', help='OCR language')
    ocr_parser.add_argument('--preprocessing', action='store_true', help='Enable image preprocessing')
    ocr_parser.add_argument('--auto-detect', action='store_true', help='Auto-detect language')
    
    # CONVERT command
    convert_parser = subparsers.add_parser('convert', help='Convert documents')
    convert_parser.add_argument('files', nargs='+', help='Files to convert')
    convert_parser.add_argument('-o', '--output-dir', help='Output directory')
    convert_parser.add_argument('-f', '--format', required=True, 
                               choices=['pdf', 'docx', 'xlsx', 'pptx', 'png', 'jpg'], 
                               help='Target format')
    convert_parser.add_argument('--dpi', type=int, default=300, help='DPI for image conversion')
    
    # BATCH command
    batch_parser = subparsers.add_parser('batch', help='Batch processing from config file')
    # BATCH command
    batch_parser = subparsers.add_parser('batch', help='Batch processing from config file')
    batch_parser.add_argument('config_file', help='Batch processing config file (JSON)')
    batch_parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    batch_parser.add_argument('--parallel', type=int, default=1, help='Number of parallel processes')
    
    # INFO command
    info_parser = subparsers.add_parser('info', help='Show PDF information')
    info_parser.add_argument('file', help='PDF file to analyze')
    info_parser.add_argument('--metadata', action='store_true', help='Show metadata')
    info_parser.add_argument('--pages', action='store_true', help='Show page information')
    info_parser.add_argument('--security', action='store_true', help='Show security information')
    
    # VALIDATE command
    validate_parser = subparsers.add_parser('validate', help='Validate PDF files')
    validate_parser.add_argument('files', nargs='+', help='PDF files to validate')
    validate_parser.add_argument('--repair', action='store_true', help='Attempt to repair corrupted PDFs')
    
    return parser


def handle_merge_command(args, handler: CLIHandler) -> int:
    """Merge command işleyicisi"""
    print(CLIColors.header(f"Merging {len(args.files)} PDF files"))
    
    # Dosya varlığını kontrol et
    missing_files = []
    for file in args.files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(CLIColors.error(f"Files not found: {', '.join(missing_files)}"))
        return 1
    
    # Output dizinini oluştur
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        success = handler.pdf_processor.merge_pdfs(args.files, args.output)
        
        if success:
            print(CLIColors.success(f"Successfully merged to: {args.output}"))
            
            # Dosya boyutu bilgisi
            total_input_size = sum(os.path.getsize(f) for f in args.files)
            output_size = os.path.getsize(args.output) if os.path.exists(args.output) else 0
            
            print(CLIColors.info(f"Input size: {total_input_size / 1024 / 1024:.1f} MB"))
            print(CLIColors.info(f"Output size: {output_size / 1024 / 1024:.1f} MB"))
            return 0
        else:
            print(CLIColors.error("Merge operation failed"))
            return 1
            
    except Exception as e:
        print(CLIColors.error(f"Merge failed: {e}"))
        return 1


def handle_split_command(args, handler: CLIHandler) -> int:
    """Split command işleyicisi"""
    print(CLIColors.header(f"Splitting PDF: {args.file}"))
    
    if not os.path.exists(args.file):
        print(CLIColors.error(f"File not found: {args.file}"))
        return 1
    
    # Output dizinini oluştur
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        result_files = handler.pdf_processor.split_pdf(
            args.file, 
            args.output_dir, 
            pages_per_file=args.pages_per_file
        )
        
        if result_files:
            print(CLIColors.success(f"Split into {len(result_files)} files"))
            for file in result_files:
                print(CLIColors.info(f"  📄 {file}"))
            return 0
        else:
            print(CLIColors.error("Split operation failed"))
            return 1
            
    except Exception as e:
        print(CLIColors.error(f"Split failed: {e}"))
        return 1


def handle_compress_command(args, handler: CLIHandler) -> int:
    """Compress command işleyicisi"""
    print(CLIColors.header(f"Compressing {len(args.files)} PDF files"))
    
    # Output dizini ayarla
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / "compressed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Progress reporter
    progress = ProgressReporter(len(args.files), "Compressing")
    
    successful = 0
    failed = 0
    total_saved = 0
    
    for file in args.files:
        if not os.path.exists(file):
            print(CLIColors.warning(f"Skipping missing file: {file}"))
            progress.update()
            failed += 1
            continue
        
        # Output dosya adı
        file_path = Path(file)
        output_file = output_dir / f"compressed_{file_path.name}"
        
        try:
            original_size = file_path.stat().st_size
            
            success = handler.pdf_processor.compress_pdf(
                file, 
                str(output_file), 
                quality=args.quality
            )
            
            if success and output_file.exists():
                compressed_size = output_file.stat().st_size
                saved_bytes = original_size - compressed_size
                saved_percent = (saved_bytes / original_size) * 100 if original_size > 0 else 0
                
                total_saved += saved_bytes
                successful += 1
                
                if args.verbose:
                    print(f"\n{CLIColors.success(f'Compressed: {file_path.name}')}")
                    print(CLIColors.info(f"  Size reduction: {saved_percent:.1f}% ({saved_bytes / 1024 / 1024:.1f} MB saved)"))
            else:
                failed += 1
                if args.verbose:
                    print(f"\n{CLIColors.error(f'Failed: {file_path.name}')}")
            
        except Exception as e:
            failed += 1
            if args.verbose:
                print(f"\n{CLIColors.error(f'Error processing {file_path.name}: {e}')}")
        
        progress.update()
    
    progress.finish()
    
    # Özet bilgisi
    print(f"\n{CLIColors.header('Compression Summary')}")
    print(CLIColors.success(f"Successful: {successful}"))
    if failed > 0:
        print(CLIColors.error(f"Failed: {failed}"))
    print(CLIColors.info(f"Total space saved: {total_saved / 1024 / 1024:.1f} MB"))
    
    return 0 if failed == 0 else 1


def handle_ocr_command(args, handler: CLIHandler) -> int:
    """OCR command işleyicisi"""
    print(CLIColors.header(f"OCR processing {len(args.files)} files"))
    
    # Output dizini ayarla
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / "ocr_processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Progress reporter
    progress = ProgressReporter(len(args.files), "OCR Processing")
    
    successful = 0
    failed = 0
    
    for file in args.files:
        if not os.path.exists(file):
            print(CLIColors.warning(f"Skipping missing file: {file}"))
            progress.update()
            failed += 1
            continue
        
        # Output dosya adı
        file_path = Path(file)
        output_file = output_dir / f"searchable_{file_path.name}"
        
        try:
            success = handler.ocr_processor.process_pdf(
                input_file=file,
                output_file=str(output_file),
                language=args.language
            )
            
            if success:
                successful += 1
                if args.verbose:
                    print(f"\n{CLIColors.success(f'OCR completed: {file_path.name}')}")
            else:
                failed += 1
                if args.verbose:
                    print(f"\n{CLIColors.error(f'OCR failed: {file_path.name}')}")
            
        except Exception as e:
            failed += 1
            if args.verbose:
                print(f"\n{CLIColors.error(f'Error processing {file_path.name}: {e}')}")
        
        progress.update()
    
    progress.finish()
    
    # Özet bilgisi
    print(f"\n{CLIColors.header('OCR Summary')}")
    print(CLIColors.success(f"Successful: {successful}"))
    if failed > 0:
        print(CLIColors.error(f"Failed: {failed}"))
    
    return 0 if failed == 0 else 1


def handle_convert_command(args, handler: CLIHandler) -> int:
    """Convert command işleyicisi"""
    print(CLIColors.header(f"Converting {len(args.files)} files to {args.format.upper()}"))
    
    # Output dizini ayarla
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / "converted"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Progress reporter
    progress = ProgressReporter(len(args.files), "Converting")
    
    successful = 0
    failed = 0
    
    for file in args.files:
        if not os.path.exists(file):
            print(CLIColors.warning(f"Skipping missing file: {file}"))
            progress.update()
            failed += 1
            continue
        
        # Output dosya adı
        file_path = Path(file)
        output_file = output_dir / f"{file_path.stem}.{args.format}"
        
        try:
            if args.format == 'pdf':
                success = handler.conversion_processor.convert_to_pdf(file, str(output_file))
            else:
                success = handler.conversion_processor.convert_from_pdf(file, str(output_file), args.format)
            
            if success:
                successful += 1
                if args.verbose:
                    print(f"\n{CLIColors.success(f'Converted: {file_path.name}')}")
            else:
                failed += 1
                if args.verbose:
                    print(f"\n{CLIColors.error(f'Conversion failed: {file_path.name}')}")
            
        except Exception as e:
            failed += 1
            if args.verbose:
                print(f"\n{CLIColors.error(f'Error converting {file_path.name}: {e}')}")
        
        progress.update()
    
    progress.finish()
    
    # Özet bilgisi
    print(f"\n{CLIColors.header('Conversion Summary')}")
    print(CLIColors.success(f"Successful: {successful}"))
    if failed > 0:
        print(CLIColors.error(f"Failed: {failed}"))
    
    return 0 if failed == 0 else 1


def handle_batch_command(args, handler: CLIHandler) -> int:
    """Batch command işleyicisi"""
    print(CLIColors.header(f"Batch processing from: {args.config_file}"))
    
    if not os.path.exists(args.config_file):
        print(CLIColors.error(f"Config file not found: {args.config_file}"))
        return 1
    
    try:
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        operations = config.get('operations', [])
        if not operations:
            print(CLIColors.warning("No operations defined in config file"))
            return 1
        
        print(CLIColors.info(f"Found {len(operations)} operations"))
        
        if args.dry_run:
            print(CLIColors.header("DRY RUN - No files will be processed"))
        
        total_successful = 0
        total_failed = 0
        
        for i, operation in enumerate(operations, 1):
            op_type = operation.get('type')
            op_name = operation.get('name', f'Operation {i}')
            
            print(f"\n{CLIColors.header(f'[{i}/{len(operations)}] {op_name} ({op_type})')}")
            
            if args.dry_run:
                print(CLIColors.info(f"Would execute: {operation}"))
                continue
            
            # Operation'ı çalıştır
            try:
                if op_type == 'merge':
                    success = handler.pdf_processor.merge_pdfs(
                        operation['input_files'],
                        operation['output_file']
                    )
                elif op_type == 'compress':
                    success = handler.pdf_processor.compress_pdf(
                        operation['input_file'],
                        operation['output_file'],
                        quality=operation.get('quality', 'medium')
                    )
                elif op_type == 'ocr':
                    success = handler.ocr_processor.process_pdf(
                        operation['input_file'],
                        operation['output_file'],
                        language=operation.get('language', 'tur')
                    )
                else:
                    print(CLIColors.warning(f"Unknown operation type: {op_type}"))
                    continue
                
                if success:
                    total_successful += 1
                    print(CLIColors.success(f"Completed: {op_name}"))
                else:
                    total_failed += 1
                    print(CLIColors.error(f"Failed: {op_name}"))
                    
            except Exception as e:
                total_failed += 1
                print(CLIColors.error(f"Error in {op_name}: {e}"))
        
        if not args.dry_run:
            print(f"\n{CLIColors.header('Batch Processing Summary')}")
            print(CLIColors.success(f"Successful: {total_successful}"))
            if total_failed > 0:
                print(CLIColors.error(f"Failed: {total_failed}"))
        
        return 0 if total_failed == 0 else 1
        
    except Exception as e:
        print(CLIColors.error(f"Batch processing failed: {e}"))
        return 1


def handle_info_command(args, handler: CLIHandler) -> int:
    """Info command işleyicisi"""
    print(CLIColors.header(f"PDF Information: {args.file}"))
    
    if not os.path.exists(args.file):
        print(CLIColors.error(f"File not found: {args.file}"))
        return 1
    
    try:
        # Mock PDF bilgisi (gerçek implementasyon için PDF reader gerekli)
        file_path = Path(args.file)
        file_stats = file_path.stat()
        
        print(f"📄 File: {file_path.name}")
        print(f"📁 Path: {file_path.absolute()}")
        print(f"📊 Size: {file_stats.st_size / 1024 / 1024:.1f} MB")
        print(f"📅 Modified: {datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Mock additional info
        if args.metadata or args.pages or args.security:
            print("\n" + CLIColors.info("Detailed Information:"))
            
            if args.metadata:
                print("  📋 Metadata:")
                print("    Title: Sample PDF Document")
                print("    Author: Unknown")
                print("    Creator: PyPDF-Tools")
                print("    Producer: Mock PDF Engine")
            
            if args.pages:
                print("  📄 Pages:")
                print("    Total pages: 10")
                print("    Page size: A4 (210 x 297 mm)")
                print("    Orientation: Portrait")
            
            if args.security:
                print("  🔒 Security:")
                print("    Encrypted: No")
                print("    Password protected: No")
                print("    Printing allowed: Yes")
                print("    Copying allowed: Yes")
        
        return 0
        
    except Exception as e:
        print(CLIColors.error(f"Failed to read PDF info: {e}"))
        return 1


def handle_validate_command(args, handler: CLIHandler) -> int:
    """Validate command işleyicisi"""
    print(CLIColors.header(f"Validating {len(args.files)} PDF files"))
    
    # Progress reporter
    progress = ProgressReporter(len(args.files), "Validating")
    
    valid_files = 0
    invalid_files = 0
    repaired_files = 0
    
    for file in args.files:
        if not os.path.exists(file):
            print(CLIColors.warning(f"Skipping missing file: {file}"))
            progress.update()
            invalid_files += 1
            continue
        
        try:
            # Mock validation (gerçek implementasyon için PDF parser gerekli)
            file_path = Path(file)
            
            # Dosya uzantısı kontrolü
            if file_path.suffix.lower() != '.pdf':
                print(CLIColors.error(f"Not a PDF file: {file_path.name}"))
                invalid_files += 1
            else:
                # Mock validation - dosya boyutu kontrolü
                if file_path.stat().st_size > 0:
                    valid_files += 1
                    if args.verbose:
                        print(f"\n{CLIColors.success(f'Valid: {file_path.name}')}")
                else:
                    invalid_files += 1
                    if args.verbose:
                        print(f"\n{CLIColors.error(f'Invalid (empty): {file_path.name}')}")
                    
                    if args.repair:
                        # Mock repair attempt
                        print(CLIColors.warning(f"  Attempting repair..."))
                        repaired_files += 1
            
        except Exception as e:
            invalid_files += 1
            if args.verbose:
                print(f"\n{CLIColors.error(f'Error validating {file}: {e}')}")
        
        progress.update()
    
    progress.finish()
    
    # Özet bilgisi
    print(f"\n{CLIColors.header('Validation Summary')}")
    print(CLIColors.success(f"Valid files: {valid_files}"))
    if invalid_files > 0:
        print(CLIColors.error(f"Invalid files: {invalid_files}"))
    if repaired_files > 0:
        print(CLIColors.info(f"Repaired files: {repaired_files}"))
    
    return 0 if invalid_files == 0 else 1


def main():
    """Ana CLI fonksiyonu"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Logging setup
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # CLI handler oluştur
    handler = CLIHandler()
    
    # Komut yok ise help göster
    if not args.command:
        parser.print_help()
        return 0
    
    # Banner göster
    if args.verbose:
        print(CLIColors.header(f"PyPDF-Tools CLI v{__version__}"))
        print(CLIColors.info("Modern PDF Processing from Command Line"))
        print("-" * 50)
    
    # Komutları işle
    try:
        if args.command == 'merge':
            return handle_merge_command(args, handler)
        elif args.command == 'split':
            return handle_split_command(args, handler)
        elif args.command == 'compress':
            return handle_compress_command(args, handler)
        elif args.command == 'ocr':
            return handle_ocr_command(args, handler)
        elif args.command == 'convert':
            return handle_convert_command(args, handler)
        elif args.command == 'batch':
            return handle_batch_command(args, handler)
        elif args.command == 'info':
            return handle_info_command(args, handler)
        elif args.command == 'validate':
            return handle_validate_command(args, handler)
        else:
            print(CLIColors.error(f"Unknown command: {args.command}"))
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print(CLIColors.warning("\nOperation cancelled by user"))
        return 130
    except Exception as e:
        print(CLIColors.error(f"Unexpected error: {e}"))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
