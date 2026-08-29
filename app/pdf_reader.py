"""
PDF Reader - baca PDF berbasis teks menggunakan PyMuPDF.
"""
import pymupdf as fitz
from pathlib import Path


def read_pdf_text(pdf_path: str) -> str:
    """
    Baca teks dari PDF berbasis teks.
    Return seluruh teks dari semua halaman.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {pdf_path}")

    doc = fitz.open(str(path))
    full_text = []

    for page in doc:
        text = page.get_text()
        full_text.append(text)

    doc.close()
    return "\n".join(full_text)


def read_pdf_text_per_page(pdf_path: str) -> list[dict]:
    """
    Baca teks per halaman.
    Return list of dict: [{"page": 1, "text": "..."}, ...]
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {pdf_path}")

    doc = fitz.open(str(path))
    pages = []

    for i, page in enumerate(doc, 1):
        text = page.get_text()
        pages.append({"page": i, "text": text})

    doc.close()
    return pages


def pdf_has_text(pdf_path: str) -> bool:
    """Cek apakah PDF memiliki teks yang bisa dibaca (bukan pure gambar)."""
    text = read_pdf_text(pdf_path)
    return len(text.strip()) > 0
