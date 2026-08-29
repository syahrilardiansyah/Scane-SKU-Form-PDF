"""
Rekap - group by SKU, hitung total quantity.
"""
import pandas as pd


def rekap_sku(data: list[dict]) -> list[dict]:
    """
    Kelompokkan data berdasarkan SKU, jumlahkan quantity.

    Args:
        data: List of dict dari parser [{"sku": "...", "nama": "...", "qty": int}, ...]

    Returns:
        List of dict: [{"sku": "...", "nama": "...", "total_qty": int}, ...]
    """
    if not data:
        return []

    # Gunakan pandas untuk groupby + sum
    df = pd.DataFrame(data)
    grouped = df.groupby(["sku", "nama"], as_index=False)["qty"].sum()
    grouped.columns = ["sku", "nama", "total_qty"]

    # Sort by total_qty descending
    grouped = grouped.sort_values("total_qty", ascending=False)

    return grouped.to_dict("records")


def rekap_to_dataframe(data: list[dict]) -> pd.DataFrame:
    """
    Konversi data rekap ke DataFrame untuk export.
    """
    rekap = rekap_sku(data)
    if not rekap:
        return pd.DataFrame(columns=["SKU", "Nama Produk", "Total Quantity"])

    df = pd.DataFrame(rekap)
    df.columns = ["SKU", "Nama Produk", "Total Quantity"]
    return df
