"""
BigSeller Parser - khusus format PDF BigSeller Order Summary.

Format BigSeller:
  [Product Name - could be multi-line]
  [SKU Code]
  Default Shelf | --
  [Quantity]
  [*OrderCode : qty] ... (order codes, skip these)
"""
import re
from collections import defaultdict


def is_order_code(line: str) -> bool:
    """Cek apakah baris adalah order code (*XXXX : N)."""
    return bool(re.match(r"^\*[A-Z0-9]{3,6}\s*:\s*\d+\s*$", line.strip()))


def is_quantity_line(line: str) -> bool:
    """Cek apakah baris hanya berisi angka (quantity)."""
    return bool(re.match(r"^\d+$", line.strip()))


def is_possible_sku(line: str) -> bool:
    """
    Cek apakah baris KEMUNGKINAN adalah SKU code.
    SKU biasanya: 2-30 chars, single word, alphanumeric + few special chars.
    """
    s = line.strip()
    if not s or len(s) > 30:
        return False
    if is_order_code(s):
        return False
    if is_quantity_line(s):
        return False
    if s in ("Default Shelf", "--"):
        return False
    # Must contain at least one letter
    if not re.search(r"[A-Za-z]", s):
        return False
    return True


def is_non_product_line(line: str) -> bool:
    """Cek apakah baris BUKAN product name (header, metadata, dll)."""
    s = line.strip()
    if not s:
        return True
    skip_starts = [
        "Informasi Produk", "Nomor Rak", "Jumlah",
        "Waktu Dicetak", "Summary List", "No.",
        "SKU", "Default Shelf",
    ]
    for pat in skip_starts:
        if s.startswith(pat):
            return True
    skip_contains = [
        "Jumlah Paket", "Jumlah SKU", "Jumlah Produk",
        "BigSeller", "bigseller.com", "EXTRA PACKING",
        "Menampilkan", "https://", "Default Shelf",
    ]
    for pat in skip_contains:
        if pat in s:
            return True
    if re.match(r"^SL\d+", s):
        return True
    if re.match(r"^\d{2}/\d{2}/\d{4}", s):
        return True
    if re.match(r"^\d+/\d+$", s):
        return True
    # "No. 1 2 3 4 ..." pattern (page numbers)
    if re.match(r"^No\.?\s+[\d\s]+$", s):
        return True
    return False


def clean_product_name(name: str, sku: str = "") -> str:
    """Bersihkan nama produk, ambil bagian penting saja."""
    name = re.sub(r"\s+", " ", name).strip()
    # Hapus prefix [Wifey Project-...]
    name = re.sub(r"^\[.*?\]\s*", "", name)
    # Hapus SKU dari nama jika ada
    if sku and sku in name:
        name = name.replace(sku, "").strip(" -+")
    # Hapus brand names di awal
    for brand in ("BEACH", "FIVESTAR", "MIDNIGHT", "MANGO", "WATERMELON"):
        if name.startswith(brand):
            name = name[len(brand):].strip(" -+")
    # Hapus trailing "99" atau angka yang terpotong
    name = re.sub(r"\s*\|\s*\d{1,2}$", "", name)
    # Batasi panjang nama
    if len(name) > 80:
        name = name[:77] + "..."
    return name.strip() if name else sku


def detect_bigseller_format(text: str) -> bool:
    """Deteksi apakah teks berasal dari format BigSeller."""
    markers = ["Default Shelf", "Informasi Produk", "Jumlah Paket"]
    found = sum(1 for m in markers if m in text)
    return found >= 2


def _collect_name_before(lines: list[str], sku_idx: int) -> list[str]:
    """Kumpulkan baris product name sebelum SKU line."""
    name_lines = []
    j = sku_idx - 1
    while j >= 0:
        prev = lines[j].strip()
        if not prev:
            break
        if is_order_code(prev):
            break
        if is_non_product_line(prev):
            break
        # Stop jika ketemu SKU lain atau shelf marker
        if is_possible_sku(prev) and prev not in ("--",):
            if j + 1 < len(lines):
                next_l = lines[j + 1].strip()
                if next_l in ("Default Shelf", "--"):
                    break
        if prev in ("Default Shelf", "--"):
            break
        name_lines.insert(0, prev)
        j -= 1
    return name_lines


def parse_bigseller(text: str) -> list[dict]:
    """
    Parse teks PDF format BigSeller.

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "qty": int}, ...]
    """
    results = []
    lines = text.splitlines()
    n = len(lines)
    i = 0

    while i < n:
        line = lines[i].strip()

        # Skip empty, order codes, quantity-only
        if not line or is_order_code(line) or is_quantity_line(line):
            i += 1
            continue

        # Skip non-product lines
        if is_non_product_line(line):
            i += 1
            continue

        # Check if this could be a SKU line
        if not is_possible_sku(line):
            i += 1
            continue

        # Found possible SKU line
        sku_candidate = line

        # Look ahead: is next line "Default Shelf" or "--"?
        if i + 1 >= n:
            i += 1
            continue

        next_line = lines[i + 1].strip()

        # Regular product: SKU, Default Shelf, Quantity
        if next_line == "Default Shelf":
            if i + 2 < n and is_quantity_line(lines[i + 2].strip()):
                qty = int(lines[i + 2].strip())
                name_lines = _collect_name_before(lines, i)
                nama = clean_product_name(" ".join(name_lines), sku_candidate) if name_lines else sku_candidate
                results.append({"sku": sku_candidate, "nama": nama, "qty": qty})
                i += 3
                continue

        # Bundle product: SKU, --, Quantity
        elif next_line == "--":
            if i + 2 < n and is_quantity_line(lines[i + 2].strip()):
                qty = int(lines[i + 2].strip())
                name_lines = _collect_name_before(lines, i)
                nama = clean_product_name(" ".join(name_lines), sku_candidate) if name_lines else sku_candidate
                results.append({"sku": sku_candidate, "nama": nama, "qty": qty})
                i += 3
                continue

        i += 1

    return results


def merge_duplicates(data: list[dict]) -> list[dict]:
    """Merge item dengan SKU yang sama, jumlahkan quantity."""
    merged = defaultdict(lambda: {"sku": "", "nama": "", "qty": 0})
    for item in data:
        sku = item["sku"]
        if not merged[sku]["sku"]:
            merged[sku]["sku"] = sku
            merged[sku]["nama"] = item["nama"]
        merged[sku]["qty"] += item["qty"]
    return list(merged.values())


def validate_bigseller_data(data: list[dict]) -> list[dict]:
    """Validasi data hasil parse BigSeller."""
    valid = []
    for item in data:
        sku = item.get("sku", "").strip()
        qty = item.get("qty", 0)
        if not sku or qty <= 0:
            continue
        skip_skus = {"BUBBLEWRAP+KARDUS", "EXTRA PACKING WAJIB"}
        if sku in skip_skus:
            continue
        # Skip non-product items by name
        nama = item.get("nama", "").lower()
        skip_keywords = ["extra packing", "bubblewrap", "kardus", "pengiriman"]
        if any(kw in nama for kw in skip_keywords):
            continue
        valid.append(item)
    return valid


def parse_bigseller_full(text: str) -> list[dict]:
    """Full pipeline: parse + validate + merge."""
    raw = parse_bigseller(text)
    valid = validate_bigseller_data(raw)
    merged = merge_duplicates(valid)
    merged.sort(key=lambda x: x["qty"], reverse=True)
    return merged
