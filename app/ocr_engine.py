"""
OCR Engine - konversi PDF scan/gambar ke teks menggunakan Tesseract.
Support PyInstaller bundled mode.
"""
import sys
import tempfile
from pathlib import Path

import pymupdf as fitz
import pytesseract
from PIL import Image

from config import OCR_LANGUAGES


def _get_tesseract_path() -> str:
    r"""
    Cari Tesseract executable.
    Priority:
    1. PyInstaller bundle (dist/tesseract/tesseract.exe)
    2. Default install (C:\Program Files\Tesseract-OCR\tesseract.exe)
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as EXE - look in bundle directory
        bundle_dir = Path(sys.executable).parent
        bundled_tesseract = bundle_dir / "tesseract" / "tesseract.exe"
        if bundled_tesseract.exists():
            return str(bundled_tesseract)

    # Check default install path
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(default_path).exists():
        return default_path

    # Try PATH
    return "tesseract"


TESSERACT_PATH = _get_tesseract_path()
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def pdf_to_images(pdf_path: str, dpi: int = 300) -> list[Image.Image]:
    """
    Konversi setiap halaman PDF menjadi gambar (PIL Image).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {pdf_path}")

    doc = fitz.open(str(path))
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render page ke gambar dengan DPI tertentu
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        # Convert ke PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    doc.close()
    return images


def ocr_image(image: Image.Image, lang: str = None) -> str:
    """
    OCR satu gambar, return teks hasil OCR.
    """
    if lang is None:
        lang = OCR_LANGUAGES

    text = pytesseract.image_to_string(image, lang=lang)
    return text


def ocr_pdf(pdf_path: str, lang: str = None) -> str:
    """
    OCR seluruh halaman PDF, gabungkan teks semua halaman.
    """
    if lang is None:
        lang = OCR_LANGUAGES

    images = pdf_to_images(pdf_path)
    all_text = []

    for i, img in enumerate(images, 1):
        text = ocr_image(img, lang=lang)
        all_text.append(f"--- Halaman {i} ---\n{text}")

    return "\n\n".join(all_text)
