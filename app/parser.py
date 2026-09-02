"""
Parser - extract SKU, Nama Produk, Quantity dari teks PDF.
Mendukung format generic (regex) dan BigSeller (auto-detect).
"""
import re
from config import LINE_PATTERN, PDF_FORMAT
from app.bigseller_parser import (
    detect_bigseller_format,
    parse_bigseller_full,
)


def parse_lines(text: str, pattern: str = None) -> list[dict]:
    """
    Parse teks PDF menjadi list data produk (generic format).

    Args:
        text: Teks hasil dari PDF reader atau OCR
        pattern: Regex pattern (default dari config)

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "qty": int}, ...]
    """
    if pattern is None:
        pattern = LINE_PATTERN

    results = []
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line)
        if match:
            sku = match.group(1).strip()
            nama = match.group(2).strip()
            try:
                qty = int(match.group(3).strip())
            except ValueError:
                continue

            results.append({
                "sku": sku,
                "nama": nama,
                "qty": qty,
            })

    return results


def parse_with_multiple_patterns(text: str, patterns: list[str] = None) -> list[dict]:
    """
    Coba beberapa pattern, kumpulkan semua hasil.
    Berguna jika format PDF tidak 100% konsisten.
    """
    if patterns is None:
        patterns = [
            # Pattern 1: spasi/tab sebagai pemisah
            r"^(.+?)\s{2,}(.+?)\s{2,}(\d+)\s*$",
            # Pattern 2: pipe sebagai pemisah
            r"^(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*$",
            # Pattern 3: koma sebagai pemisah
            r"^(.+?)\s*,\s*(.+?)\s*,\s*(\d+)\s*$",
        ]

    all_results = []
    seen = set()

    for pattern in patterns:
        results = parse_lines(text, pattern=pattern)
        for r in results:
            # Deduplicate berdasarkan (sku, nama, qty)
            key = (r["sku"], r["nama"], r["qty"])
            if key not in seen:
                seen.add(key)
                all_results.append(r)

    return all_results


def validate_data(data: list[dict]) -> list[dict]:
    """
    Validasi data hasil parse.
    Hapus data yang tidak valid.
    """
    valid = []
    for item in data:
        # SKU tidak boleh kosong
        if not item.get("sku"):
            continue
        # Qty harus > 0
        if item.get("qty", 0) <= 0:
            continue
        valid.append(item)
    return valid


def parse_auto(text: str) -> list[dict]:
    """
    Auto-detect format PDF dan parse sesuai format.
    - BigSeller → gunakan bigseller_parser
    - Generic → gunakan regex patterns

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "qty": int}, ...]
    """
    # Check config override
    if PDF_FORMAT == "bigseller":
        return parse_bigseller_full(text)
    elif PDF_FORMAT == "generic":
        raw = parse_with_multiple_patterns(text)
        return validate_data(raw)

    # Auto-detect: coba BigSeller dulu
    if detect_bigseller_format(text):
        return parse_bigseller_full(text)

    # Fallback ke generic parser
    raw = parse_with_multiple_patterns(text)
    return validate_data(raw)
