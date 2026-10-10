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
    """Cek apakah item adalah freebie/gift yang harus di-exclude.

    Keyword hanya dicocokkan ke SKU, bukan ke nama produk.
    Nama produk sering menyebut freebie di deskripsi marketing
    (contoh: "Free Crystal Sticker") padahal produknya legit.
    """
    keywords = _load_freebie_keywords()
    sku_lower = sku.lower()

    for kw in keywords:
        if kw.lower() in sku_lower:
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
    Gabungkan SKU yang terpotong line-wrapping.

    Pola di PDF BigSeller:
        Lily250mL+CottonBlanket250m
        L
        --

    Baris SKU selalu ditutup shelf marker ("--" / "Default Shelf"),
    jadi kita anchor dari situ: kumpulkan baris ke atas selama tanpa
    spasi (nama produk selalu punya spasi), lalu gabung jadi satu.
    """
    shelf_markers = ("Default Shelf", "--")
    joins = {}    # indeks awal SKU -> string gabungan
    skip = set()  # indeks fragment sisanya

    i = 0
    while i < len(lines):
        if lines[i].strip() in shelf_markers:
            j = i - 1
            block = []  # (indeks, teks), diurutkan dari atas
            while j >= 0:
                s = lines[j].strip()
                if not s or " " in s or not is_possible_sku(s):
                    break
                block.insert(0, (j, s))
                j -= 1

            if len(block) > 1:
                # Potong dari atas: kata terakhir product name (contoh
                # "Spons", "Deskripsi") ikut ke-block karena tanpa spasi.
                # SKU bundle selalu mengandung "+", jadi mulai dari baris
                # "+" pertama dari atas.
                plus = [k for k, (_, t) in enumerate(block) if "+" in t]
                if plus:
                    sku_block = block[plus[0]:]
                    if len(sku_block) > 1:
                        joins[sku_block[0][0]] = "".join(t for _, t in sku_block)
                        skip.update(idx for idx, _ in sku_block[1:])
        i += 1

    fixed = []
    for idx, line in enumerate(lines):
        if idx in skip:
            continue
        fixed.append(joins.get(idx, line))
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
    BUBBLEWRAP+KARDUS → ["BUBBLEWRAP+KARDUS"] (tidak dipecah)
    """
    if sku.upper() in _DONT_SPLIT:
        return [sku]
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


_DONT_SPLIT = {"BUBBLEWRAP+KARDUS"}


def split_bundles(data: list[dict]) -> list[dict]:
    """
    Split bundle SKU dan distribusi quantity ke masing-masing SKU.
    Contoh: {"sku": "Allofme100mL+City100mL", "qty": 5}
    → [{"sku": "Allofme100mL", "qty": 5}, {"sku": "City100mL", "qty": 5}]
    """
    expanded = []
    for item in data:
        sku = item["sku"]

        if sku.upper() in _DONT_SPLIT:
            expanded.append(item)
            continue

        parts = _split_bundle_sku(sku)

        if len(parts) > 1:
            for part in parts:
                expanded.append({
                    "sku": part,
                    "nama": item["nama"],
                    "qty": item["qty"]
                })
        else:
            expanded.append(item)

    return expanded


_SKU_ALIASES = {
    "ALLFOME100ML": "Allofme100mL",
    "ALLOFME100ML": "Allofme100mL",
    "CHARMKUNING": "CharmSilky",
    "CHARMSILKY": "CharmSilky",
    "DEEPCLEAN": "DeepClean",
    "DEEPCLEAN1500GR": "DeepClean",
    "LAP2": "LapMicrofiber2",
    "LAPMICROFIBER2": "LapMicrofiber2",
    "SPONS": "SponsRandom",
    "SPONSR": "SponsRandom",
    "SPONSRANDOM": "SponsRandom",
}


def merge_duplicates(data: list[dict]) -> list[dict]:
    """Merge item dengan SKU yang sama (case-insensitive + alias), jumlahkan quantity."""
    merged = {}
    for item in data:
        sku = item["sku"]
        sku_key = sku.upper()
        alias = _SKU_ALIASES.get(sku_key)

        if alias is not None:
            merge_key = alias.upper()
        else:
            merge_key = sku_key

        if merge_key not in merged:
            merged[merge_key] = {"sku": alias or sku, "nama": item["nama"], "qty": 0}
        merged[merge_key]["qty"] += item["qty"]

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
        skip_skus = {"EXTRA PACKING WAJIB"}
        if sku in skip_skus:
            continue

        # Skip by name keywords (SKU material packing tetap dihitung)
        nama = item.get("nama", "").lower()
        skip_keywords = ["extra packing"]
        is_packaging_sku = any(k in sku.upper() for k in ("BUBBLEWRAP", "KARDUS"))
        if not is_packaging_sku and any(kw in nama for kw in skip_keywords):
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
