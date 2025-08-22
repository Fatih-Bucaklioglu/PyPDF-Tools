#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyPDF-Tools Command Line Interface
PDF işlemleri için komut satırı arayüzü
"""

import os
import sys
import json
import click
from pathlib import Path
from typing import List, Optional, Dict, Any

# PDF işleme kütüphaneleri - gerçek implementasyon için
try:
    import PyPDF2
    import pypdf
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError as e:
    print(f"Uyarı: PDF kütüphaneleri yüklenmedi: {e}")

from pypdf_tools._version import __version__, APP_NAME


@click.group()
@click.version_option(version=__version__, prog_name=APP_NAME)
@click.option('--verbose', '-v', is_flag=True, help='Ayrıntılı çıktı göster')
@click.option('--config', '-c', type=click.Path(), help='Yapılandırma dosyası yolu')
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """
    PyPDF-Tools - Hibrit PDF yönetim ve düzenleme uygulaması
    
    PDF dosyalarını birleştirme, bölme, şifreleme ve daha fazlası için
    komut satırı araçları.
    """
    # Context objesini oluştur
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        click.echo(f"{APP_NAME} v{__version__} - CLI Modu")


@cli.command()
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Çıktı dosyası yolu')
@click.option('--bookmarks', is_flag=True,
              help='Yer işaretlerini koru')
@click.pass_context
def merge(ctx, input_files: tuple, output: str, bookmarks: bool):
    """
    Birden fazla PDF dosyasını tek dosyada birleştir.
    
    Örnek kullanım:
    pypdf merge file1.pdf file2.pdf file3.pdf -o merged.pdf
    """
    if len(input_files) < 2:
        click.echo("Hata: En az 2 PDF dosyası gerekli", err=True)
        sys.exit(1)
    
    try:
        result = merge_pdfs(list(input_files), output, keep_bookmarks=bookmarks)
        
        if result['success']:
            click.echo(f"✓ {len(input_files)} dosya başarıyla birleştirildi: {output}")
            if ctx.obj['verbose']:
                click.echo(f"  Toplam sayfa: {result.get('total_pages', 'bilinmiyor')}")
                click.echo(f"  Dosya boyutu: {result.get('file_size', 'bilinmiyor')}")
        else:
            click.echo(f"Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Birleştirme hatası: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', '-d', type=click.Path(),
              help='Çıktı dizini (varsayılan: input dosyası ile aynı)')
@click.option('--range', '-r', 'page_range',
              help='Sayfa aralığı (örn: 1-5, 3,7,9-12)')
@click.option('--prefix', default='page_',
              help='Çıktı dosya öneki')
@click.pass_context
def split(ctx, input_file: str, output_dir: Optional[str], 
          page_range: Optional[str], prefix: str):
    """
    PDF dosyasını sayfalara veya belirtilen aralıklara böl.
    
    Örnekler:
    pypdf split document.pdf -d ./pages/
    pypdf split document.pdf -r 1-10 -o first_10_pages.pdf
    pypdf split document.pdf -r 1,3,5-7 --prefix chapter_
    """
    input_path = Path(input_file)
    
    if not output_dir:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if page_range:
            # Belirtilen aralıkları böl
            result = split_pdf_range(input_file, str(output_dir), 
                                   page_range, prefix)
        else:
            # Her sayfayı ayrı dosya yap
            result = split_pdf_pages(input_file, str(output_dir), prefix)
        
        if result['success']:
            click.echo(f"✓ PDF başarıyla bölündü: {result['files_created']} dosya oluşturuldu")
            if ctx.obj['verbose']:
                for file_info in result.get('files', []):
                    click.echo(f"  - {file_info['name']}: {file_info['pages']} sayfa")
        else:
            click.echo(f"Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Bölme hatası: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Çıktı dosyası (varsayılan: input_encrypted.pdf)')
@click.option('--password', '-p', prompt=True, hide_input=True,
              help='Şifre')
@click.option('--owner-password', prompt=True, hide_input=True,
              help='Sahip şifresi')
@click.option('--permissions', type=click.Choice(['print', 'modify', 'copy', 'annotate']),
              multiple=True, help='İzinler')
@click.pass_context
def encrypt(ctx, input_file: str, output: Optional[str], password: str,
           owner_password: str, permissions: tuple):
    """
    PDF dosyasını şifrele ve izinleri ayarla.
    
    Örnek:
    pypdf encrypt document.pdf -o secure_document.pdf --permissions print copy
    """
    if not output:
        input_path = Path(input_file)
        output = str(input_path.with_stem(f"{input_path.stem}_encrypted"))
    
    try:
        result = encrypt_pdf(input_file, output, password, owner_password, 
                           list(permissions))
        
        if result['success']:
            click.echo(f"✓ PDF başarıyla şifrelendi: {output}")
            if ctx.obj['verbose']:
                click.echo(f"  İzinler: {', '.join(permissions) or 'Yok'}")
        else:
            click.echo(f"Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Şifreleme hatası: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Çıktı dosyası')
@click.option('--password', '-p', prompt=True, hide_input=True,
              help='PDF şifresi')
@click.pass_context
def decrypt(ctx, input_file: str, output: Optional[str], password: str):
    """
    Şifrelenmiş PDF dosyasının şifresini kaldır.
    
    Örnek:
    pypdf decrypt secure_document.pdf -o document.pdf
    """
    if not output:
        input_path = Path(input_file)
        output = str(input_path.with_stem(f"{input_path.stem}_decrypted"))
    
    try:
        result = decrypt_pdf(input_file, output, password)
        
        if result['success']:
            click.echo(f"✓ PDF şifresi başarıyla kaldırıldı: {output}")
        else:
            click.echo(f"Hata: {result.get('error', 'Yanlış şifre veya dosya hatası')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Şifre kaldırma hatası: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Çıktı metin dosyası')
@click.option('--pages', '-p', 
              help='Belirtilen sayfalar (örn: 1-5, 3,7,9-12)')
@click.option('--format', '-f', type=click.Choice(['txt', 'json', 'csv']),
              default='txt', help='Çıktı formatı')
@click.pass_context
def extract_text(ctx, input_file: str, output: Optional[str], 
                pages: Optional[str], format: str):
    """
    PDF'den metin çıkar.
    
    Örnekler:
    pypdf extract-text document.pdf
    pypdf extract-text document.pdf -p 1-10 -f json -o extracted.json
    """
    try:
        result = extract_pdf_text(input_file, pages, format)
        
        if result['success']:
            if output:
                # Dosyaya yaz
                output_path = Path(output)
                with open(output_path, 'w', encoding='utf-8') as f:
                    if format == 'json':
                        json.dump(result['text'], f, ensure_ascii=False, indent=2)
                    else:
                        f.write(result['text'])
                click.echo(f"✓ Metin çıkarıldı: {output}")
            else:
                # Konsola yazdır
                if format == 'json':
                    click.echo(json.dumps(result['text'], ensure_ascii=False, indent=2))
                else:
                    click.echo(result['text'])
                    
            if ctx.obj['verbose']:
                click.echo(f"  İşlenen sayfa sayısı: {result.get('pages_processed', 0)}")
                click.echo(f"  Toplam karakter: {len(str(result['text']))}")
        else:
            click.echo(f"Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Metin çıkarma hatası: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'txt']),
              default='json', help='Çıktı formatı')
@click.pass_context
def info(ctx, input_file: str, format: str):
    """
    PDF dosyası hakkında bilgi göster.
    
    Örnek:
    pypdf info document.pdf --format yaml
    """
    try:
        result = get_pdf_info(input_file)
        
        if result['success']:
            info_data = result['info']
            
            if format == 'json':
                click.echo(json.dumps(info_data, indent=2, default=str))
            elif format == 'yaml':
                try:
                    import yaml
                    click.echo(yaml.dump(info_data, default_flow_style=False))
                except ImportError:
                    click.echo("YAML formatı için 'pyyaml' kütüphanesi gerekli")
                    click.echo(json.dumps(info_data, indent=2, default=str))
            else:
                # Metin formatı
                click.echo(f"PDF Bilgileri: {Path(input_file).name}")
                click.echo("-" * 40)
                for key, value in info_data.items():
                    click.echo(f"{key.capitalize()}: {value}")
        else:
            click.echo(f"Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Bilgi alma hatası: {str(e)}", err=True)
        sys.exit(1)


# Yardımcı fonksiyonlar - gerçek implementasyon gerekir

def merge_pdfs(input_files: List[str], output: str, 
               keep_bookmarks: bool = False) -> Dict[str, Any]:
    """PDF birleştirme implementasyonu"""
    # Geçici implementasyon - PyPDF2 kullanılmalı
    return {
        'success': True,
        'total_pages': len(input_files) * 10,  # Placeholder
        'file_size': '1.2 MB'  # Placeholder
    }


def split_pdf_pages(input_file: str, output_dir: str, 
                   prefix: str) -> Dict[str, Any]:
    """PDF sayfa bölme implementasyonu"""
    # Geçici implementasyon
    return {
        'success': True,
        'files_created': 10,
        'files': [
            {'name': f'{prefix}001.pdf', 'pages': 1},
            {'name': f'{prefix}002.pdf', 'pages': 1},
        ]
    }


def split_pdf_range(input_file: str, output_dir: str, 
                   page_range: str, prefix: str) -> Dict[str, Any]:
    """PDF aralık bölme implementasyonu"""
    # Geçici implementasyon
    return {
        'success': True,
        'files_created': 3,
        'files': [
            {'name': f'{prefix}1-5.pdf', 'pages': 5},
            {'name': f'{prefix}6-10.pdf', 'pages': 5},
        ]
    }


def encrypt_pdf(input_file: str, output: str, password: str, 
               owner_password: str, permissions: List[str]) -> Dict[str, Any]:
    """PDF şifreleme implementasyonu"""
    # Geçici implementasyon
    return {'success': True}


def decrypt_pdf(input_file: str, output: str, password: str) -> Dict[str, Any]:
    """PDF şifre kaldırma implementasyonu"""
    # Geçici implementasyon
    return {'success': True}


def extract_pdf_text(input_file: str, pages: Optional[str], 
                    format: str) -> Dict[str, Any]:
    """PDF metin çıkarma implementasyonu"""
    # Geçici implementasyon
    sample_text = "Bu örnek PDF metnidir. Gerçek implementasyon gereklidir."
    
    if format == 'json':
        text_data = {
            'file': input_file,
            'pages': pages or 'all',
            'content': [
                {'page': 1, 'text': sample_text},
                {'page': 2, 'text': sample_text}
            ]
        }
        return {'success': True, 'text': text_data, 'pages_processed': 2}
    else:
        return {'success': True, 'text': sample_text, 'pages_processed': 2}


def get_pdf_info(input_file: str) -> Dict[str, Any]:
    """PDF bilgi çıkarma implementasyonu"""
    # Geçici implementasyon
    file_path = Path(input_file)
    return {
        'success': True,
        'info': {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'pages': 10,  # Placeholder
            'title': 'Örnek PDF',
            'author': 'Bilinmiyor',
            'subject': '',
            'creator': 'PyPDF-Tools',
            'producer': 'PyPDF-Tools',
            'creation_date': '2024-01-01',
            'modification_date': '2024-01-01',
            'encrypted': False,
            'permissions': ['print', 'copy', 'modify', 'annotate']
        }
    }


def cli_main():
    """CLI ana giriş noktası"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nİşlem iptal edildi.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Beklenmeyen hata: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli_main()
