"""
Rekap - group by SKU, hitung total quantity.
Mendukung mode normal (per SKU) dan mode split (per komponen produk).
"""
import pandas as pd

from app import bigseller_parser
from app.sku_group import combine_groups


def rekap_sku(data: list[dict], split_bundles: bool = True) -> list[dict]:
    """
    Kelompokkan data berdasarkan SKU, jumlahkan quantity.

    Args:
        data: List of dict dari parser [{"sku": "...", "nama": "...", "qty": int}, ...]
        split_bundles: Jika True, bundle "BEACH+WATERMELON" di-split jadi BEACH & WATERMELON

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "total_qty": int}, ...]
    """
    if not data:
        return []

    # Expand bundles jika diminta (aturan split + BUBBLEWRAP+KARDUS ada di parser)
    if split_bundles:
        data = bigseller_parser.split_bundles(data)

    # Gunakan pandas untuk groupby + sum
    df = pd.DataFrame(data)
    grouped = df.groupby("sku", as_index=False)["qty"].sum()
    grouped.columns = ["sku", "total_qty"]

    # Gabungkan SKU multi-PCS (BodyMask1/2/3 -> BodyMask)
    records = combine_groups(grouped.to_dict("records"))

    # Sort by total_qty descending
    records.sort(key=lambda r: r.get("total_qty", 0), reverse=True)

    return records


def rekap_to_dataframe(data: list[dict], split_bundles: bool = True) -> pd.DataFrame:
    """
    Konversi data rekap ke DataFrame untuk export.
    """
    rekap = rekap_sku(data, split_bundles=split_bundles)
    if not rekap:
        return pd.DataFrame(columns=["SKU", "Total Quantity", "Breakdown"])

    df = pd.DataFrame(rekap)
    if "breakdown" not in df.columns:
        df["breakdown"] = ""
    df["breakdown"] = df["breakdown"].fillna("")
    df = df[["sku", "total_qty", "breakdown"]]
    df.columns = ["SKU", "Total Quantity", "Breakdown"]
    return df
