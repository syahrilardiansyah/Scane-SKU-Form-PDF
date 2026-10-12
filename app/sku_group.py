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
            # nama grup sama muncul 2x di config → digabung, bukan ditimpa
            groups.setdefault(name, []).extend(parsed)
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


def combine_groups(rows: list[dict], groups: dict | None = None) -> list[dict]:
    """
    Gabungkan baris hasil groupby sesuai konfigurasi grup.

    Lebih dari satu grup boleh memakai SKU anggota yang sama, contoh:
      LapMicrofiber = LapMicrofiber2*2
      BoxMicrofiber = LapMicrofiber2*1
    keduanya dihitung dari baris LapMicrofiber2 yang sama.

    Args:
        rows: [{"sku": ..., "total_qty": int}, ...]
        groups: Konfigurasi grup (default: baca sku_groups.txt)

    Returns:
        Baris anggota grup diganti baris hasil gabungan (qty x multiplier +
        field "breakdown"), baris lain tetap.
    """
    if not rows:
        return rows

    if groups is None:
        groups = load_groups()
    if not groups:
        return rows

    member_skus = {m.upper() for members in groups.values() for m, _ in members}
    group_names = {name.upper() for name in groups}

    member_qty: dict[str, int] = {}
    extra_qty: dict[str, int] = {}
    others: list[dict] = []

    for row in rows:
        sku_upper = str(row.get("sku", "")).upper()
        qty = int(row.get("total_qty", 0) or 0)
        if sku_upper in member_skus:
            member_qty[sku_upper] = member_qty.get(sku_upper, 0) + qty
        elif sku_upper in group_names:
            extra_qty[sku_upper] = extra_qty.get(sku_upper, 0) + qty
        else:
            others.append(row)

    out: list[dict] = []
    for name, members in groups.items():
        parts: list[str] = []
        total = 0
        for member, multiplier in members:
            qty = member_qty.get(member.upper(), 0)
            if qty <= 0:
                continue
            total += qty * multiplier
            parts.append(f"{member} ({qty}x{multiplier})")

        bonus = extra_qty.get(name.upper(), 0)
        if bonus:
            total += bonus
            parts.append(f"{name} ({bonus}x1)")

        if parts:
            out.append({
                "sku": name,
                "total_qty": total,
                "breakdown": " + ".join(parts),
            })

    out.extend(others)
    return out
