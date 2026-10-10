"""
Export - generate file Excel dari data rekap.
"""
from pathlib import Path
import pandas as pd
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

from config import OUTPUT_FILENAME, EXCEL_SHEET_NAME


def export_to_excel(data: list[dict], output_path: str = None) -> str:
    """
    Export data rekap ke file Excel.

    Args:
        data: List of dict dari rekap [{"sku": "...", "nama": "...", "total_qty": int}, ...]
        output_path: Path file output (default: hasil_rekap.xlsx)

    Returns:
        Path file Excel yang dihasilkan
    """
    if output_path is None:
        output_path = OUTPUT_FILENAME

    # Konversi ke DataFrame (kontrak: SKU, Total Quantity, Breakdown)
    columns = ["SKU", "Total Quantity", "Breakdown"]
    if data:
        df = pd.DataFrame([
            {
                "SKU": item.get("SKU", item.get("sku", "")),
                "Total Quantity": item.get("Total Quantity", item.get("total_qty", 0)),
                "Breakdown": item.get("Breakdown", item.get("breakdown", "")) or "",
            }
            for item in data
        ])
    else:
        df = pd.DataFrame(columns=columns)

    # Write ke Excel
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=EXCEL_SHEET_NAME)

        # Format worksheet
        ws = writer.sheets[EXCEL_SHEET_NAME]
        _format_worksheet(ws, len(df))

    return str(Path(output_path).resolve())


def _format_worksheet(ws, data_rows: int):
    """Format Excel worksheet agar lebih rapi."""
    # Header style
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # Format header
    for cell in ws[1]:
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border

    # Format data rows
    for row in ws.iter_rows(min_row=2, max_row=data_rows + 1, max_col=3):
        for cell in row:
            cell.border = thin_border
            # Qty column (kolom 2) rata kanan, sisanya rata kiri
            if cell.column == 2:
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")

    # Auto-width columns (dibatasi biar kolom Breakdown nggak kepanjangan)
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_length + 3, 60)
