"""
SKU group - gabungkan SKU multi-PCS jadi satu baris rekap.

Contoh: BodyMask1 (1 pcs) + BodyMask2 (isi 2 pcs) + BodyMask3 (isi 3 pcs)
        → BodyMask = BodyMask1*1 + BodyMask2*2 + BodyMask3*3

Konfigurasi dibaca dari sku_groups.txt (sebelah freebie_keywords.txt).
"""
import sys
from pathlib import Path

_DEFAULT_CONFIG = "BodyMask = BodyMask1*1, BodyMask2*2, BodyMask3*3"


def _config_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def _parse(text: str) -> dict[str, list[tuple[str, int]]]:
    groups: dict[str, list[tuple[str, int]]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, members = line.split("=", 1)
        name = name.strip()
        parsed: list[tuple[str, int]] = []
        for chunk in members.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "*" in chunk:
                sku, mult = chunk.rsplit("*", 1)
                try:
                    multiplier = int(mult)
                except ValueError:
                    continue
            else:
                sku, multiplier = chunk, 1
            sku = sku.strip()
            if sku and multiplier > 0:
                parsed.append((sku, multiplier))
        if name and parsed:
            groups[name] = parsed
    return groups


def load_groups() -> dict[str, list[tuple[str, int]]]:
    """Baca sku_groups.txt. Kalau tidak ada / gagal, pakai default bawaan."""
    path = _config_base() / "sku_groups.txt"
    text = ""
    if path.exists():
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            text = ""
    if not text.strip():
        text = _DEFAULT_CONFIG
    return _parse(text)


def _owner_of(sku_upper: str, groups: dict) -> str | None:
    """SKU ini anggota grup mana? (None kalau bukan anggota grup manapun)."""
    for name, members in groups.items():
        for member, _ in members:
            if member.upper() == sku_upper:
                return name
    return None


def combine_groups(rows: list[dict]) -> list[dict]:
    """
    Gabungkan baris hasil groupby sesuai konfigurasi grup.

    Args:
        rows: [{"sku": ..., "total_qty": int}, ...]

    Returns:
        List yang sama, tapi baris anggota grup diganti 1 baris gabungan
        berisi qty total x multiplier + field "breakdown" cara hitungnya.
    """
    if not rows:
        return rows

    groups = load_groups()
    if not groups:
        return rows

    by_upper: dict[str, dict] = {}
    for row in rows:
        by_upper[str(row.get("sku", "")).upper()] = row

    # Baris yang namanya persis nama grup dianggap anggota tambahan (x1)
    group_names = {name.upper() for name in groups}
    extras: dict[str, int] = {}
    for name in group_names:
        row = by_upper.get(name)
        if row:
            extras[name] = int(row.get("total_qty", 0) or 0)

    out: list[dict] = []
    emitted: set[str] = set()

    for row in rows:
        sku = str(row.get("sku", ""))
        sku_upper = sku.upper()
        owner = _owner_of(sku_upper, groups)

        if owner is None:
            if sku_upper not in group_names:
                out.append(row)
            continue

        if owner.upper() in emitted:
            continue
        emitted.add(owner.upper())

        parts: list[str] = []
        total = 0
        for member, multiplier in groups[owner]:
            member_row = by_upper.get(member.upper())
            if not member_row:
                continue
            qty = int(member_row.get("total_qty", 0) or 0)
            if qty <= 0:
                continue
            total += qty * multiplier
            parts.append(f"{member} ({qty}x{multiplier})")

        extra_qty = extras.get(owner.upper(), 0)
        if extra_qty:
            total += extra_qty
            parts.append(f"{owner} ({extra_qty}x1)")

        if not parts:
            continue

        out.append({"sku": owner, "total_qty": total, "breakdown": " + ".join(parts)})

    return out
