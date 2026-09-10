"""
BigSeller Parser - khusus format PDF BigSeller Order Summary.

Format BigSeller:
  [Product Name - could be multi-line]
  [SKU Code]
  Default Shelf | --
  [Quantity]
  [*OrderCode : qty] ... (order codes, skip these)

Handles:
- Line wrapping (e.g., "DeoPinkWonde" + "r" → "DeoPinkWonder")
- Bundle splitting (SKU1+SKU2 → split qty to each SKU)
- Freebie exclusion (Stickerpack, GelangCouple, Tester)
"""
import re
import sys
from collections import defaultdict
from pathlib import Path


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
    if not s or len(s) > 50:
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


def is_freebie_item(sku: str, nama: str) -> bool:
    """Cek apakah item adalah freebie/gift yang harus di-exclude."""
    keywords = _load_freebie_keywords()
    sku_lower = sku.lower()
    nama_lower = nama.lower()

    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in sku_lower or kw_lower in nama_lower:
            return True

    return False


def _load_freebie_keywords() -> list[str]:
    """Load freebie keywords dari file eksternal atau fallback ke default."""
    default = ["stickerpack", "gelangcouple", "tester", "freebiest",
               "free claim", "freegelang", "freesticker"]

    # Cari file di folder yang sama dengan EXE atau source
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent

    keywords_file = base / "freebie_keywords.txt"

    if keywords_file.exists():
        try:
            with open(keywords_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                if lines:
                    return lines
        except Exception:
            pass

    # Fallback ke config.py
    try:
        from config import FREEBIE_KEYWORDS
        return FREEBIE_KEYWORDS
    except ImportError:
        pass

    return default


def _fix_line_wrapping(lines: list[str]) -> list[str]:
    """
    Fix line wrapping issue.
    Contoh: "Allofme100mL+DeoPinkWonde" diikuti "r" → "Allofme100mL+DeoPinkWonder"
    Contoh: "PouchDetEmerald+PouchDetE" diikuti "merald" → "PouchDetEmerald+PouchDetEmerald"
    Contoh: "DeepClean+Beach+Lap2+Spon" diikuti "s" → "DeepClean+Beach+Lap2+Spons"
    """
    fixed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if this looks like a truncated SKU (has +, next line is continuation)
        # Must be a REAL SKU line (no spaces = compact code), not a product description
        if (i + 1 < len(lines)
                and is_possible_sku(line)
                and "+" in line
                and " " not in line):
            next_line = lines[i + 1].strip()
            # If next line looks like a continuation fragment (not a new SKU block)
            if (next_line
                    and len(next_line) <= 30
                    and is_possible_sku(next_line)
                    and not is_quantity_line(next_line)
                    and next_line not in ("Default Shelf", "--")):
                # Don't join if next line is a FULL standalone SKU without +
                # (i.e., next line has no + AND is followed by Default Shelf or --)
                if ("+" not in next_line
                        and not next_line[0].isupper()):
                    # Lowercase start = likely continuation fragment, join
                    combined = line + next_line
                    fixed.append(combined)
                    i += 2
                    continue
                elif "+" in next_line:
                    # Has + = could be continuation of multi-SKU bundle, join
                    combined = line + next_line
                    fixed.append(combined)
                    i += 2
                    continue

        fixed.append(lines[i])
        i += 1

    return fixed


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


def _split_bundle_sku(sku: str) -> list[str]:
    """
    Split bundle SKU menjadi individual SKUs.
    Contoh: "Allofme100mL+City100mL" → ["Allofme100mL", "City100mL"]
    """
    if "+" in sku:
        parts = sku.split("+")
        return [p.strip() for p in parts if p.strip()]
    return [sku]


def detect_bigseller_format(text: str) -> bool:
    """Deteksi apakah teks berasal dari format BigSeller."""
    markers = ["Default Shelf", "Informasi Produk", "Jumlah Paket"]
    found = sum(1 for m in markers if m in text)
    return found >= 2


def parse_bigseller(text: str) -> list[dict]:
    """
    Parse teks PDF format BigSeller.

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "qty": int}, ...]
    """
    results = []
    lines = text.splitlines()

    # Fix line wrapping first
    lines = _fix_line_wrapping(lines)

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

        # Handle "SKU --" pattern (bundle marker on same line)
        if sku_candidate.endswith(" --"):
            sku_candidate = sku_candidate[:-3].strip()

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
                nama = " ".join(name_lines) if name_lines else sku_candidate
                results.append({"sku": sku_candidate, "nama": nama, "qty": qty})
                i += 3
                continue

        # Bundle product: SKU, --, Quantity
        elif next_line == "--":
            if i + 2 < n and is_quantity_line(lines[i + 2].strip()):
                qty = int(lines[i + 2].strip())
                name_lines = _collect_name_before(lines, i)
                nama = " ".join(name_lines) if name_lines else sku_candidate
                results.append({"sku": sku_candidate, "nama": nama, "qty": qty})
                i += 3
                continue

        # Bundle product: SKU --, Quantity (bundle marker on same line as SKU)
        elif is_quantity_line(next_line) and "+" in sku_candidate:
            qty = int(next_line)
            name_lines = _collect_name_before(lines, i)
            nama = " ".join(name_lines) if name_lines else sku_candidate
            results.append({"sku": sku_candidate, "nama": nama, "qty": qty})
            i += 2
            continue

        i += 1

    return results


def split_bundles(data: list[dict]) -> list[dict]:
    """
    Split bundle SKU dan distribusi quantity ke masing-masing SKU.
    Contoh: {"sku": "Allofme100mL+City100mL", "qty": 5}
    → [{"sku": "Allofme100mL", "qty": 5}, {"sku": "City100mL", "qty": 5}]
    """
    expanded = []
    for item in data:
        sku = item["sku"]
        parts = _split_bundle_sku(sku)

        if len(parts) > 1:
            # It's a bundle - split to individual SKUs
            for part in parts:
                expanded.append({
                    "sku": part,
                    "nama": item["nama"],
                    "qty": item["qty"]
                })
        else:
            # Single SKU - keep as is
            expanded.append(item)

    return expanded


def merge_duplicates(data: list[dict]) -> list[dict]:
    """Merge item dengan SKU yang sama (case-insensitive), jumlahkan quantity."""
    merged = {}
    for item in data:
        sku = item["sku"]
        sku_key = sku.upper()  # Case-insensitive key

        if sku_key not in merged:
            merged[sku_key] = {"sku": sku, "nama": item["nama"], "qty": 0}
        merged[sku_key]["qty"] += item["qty"]

    return list(merged.values())


def validate_bigseller_data(data: list[dict]) -> list[dict]:
    """Validasi data hasil parse BigSeller."""
    valid = []
    for item in data:
        sku = item.get("sku", "").strip()
        qty = item.get("qty", 0)
        if not sku or qty <= 0:
            continue

        # Skip non-product items
        skip_skus = {"BUBBLEWRAP+KARDUS", "EXTRA PACKING WAJIB"}
        if sku in skip_skus:
            continue

        # Skip by name keywords
        nama = item.get("nama", "").lower()
        skip_keywords = ["extra packing", "bubblewrap", "kardus"]
        if any(kw in nama for kw in skip_keywords):
            continue

        # Skip freebie items
        if is_freebie_item(sku, item.get("nama", "")):
            continue

        valid.append(item)

    return valid


def parse_bigseller_full(text: str) -> list[dict]:
    """Full pipeline: parse + split bundles + validate + merge."""
    raw = parse_bigseller(text)
    expanded = split_bundles(raw)
    valid = validate_bigseller_data(expanded)
    merged = merge_duplicates(valid)
    merged.sort(key=lambda x: x["qty"], reverse=True)
    return merged
