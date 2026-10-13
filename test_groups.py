"""
Self-check konfigurasi & logika grup SKU. Jalankan: python test_groups.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.sku_group import _parse, combine_groups
from app.export import export_excel_path, export_to_excel


def test_parse_multiplier():
    g = _parse("A = A1*1, A2*2\nB = A2*3")
    assert g["A"] == [("A1", 1), ("A2", 2)]
    assert g["B"] == [("A2", 3)]


def test_duplicate_name_merges():
    g = _parse("G = X*1\nG = Y*2")
    assert g["G"] == [("X", 1), ("Y", 2)]


def test_bad_multiplier_skipped():
    g = _parse("G = X*1, Y*abc, Z*0")
    assert g["G"] == [("X", 1)]


def test_combine_multi_group():
    groups = {"Lap": [("Lap2", 2)], "Box": [("Lap2", 1)]}
    out = combine_groups([{"sku": "Lap2", "total_qty": 10}], groups=groups)
    by = {r["sku"]: r["total_qty"] for r in out}
    assert by == {"Lap": 20, "Box": 10}


def test_combine_keeps_others_and_group_row():
    groups = {"Body": [("Body1", 1), ("Body2", 2)]}
    rows = [
        {"sku": "Body1", "total_qty": 5},
        {"sku": "Body2", "total_qty": 2},
        {"sku": "Body", "total_qty": 3},    # baris mentah bernama sama grup → x1
        {"sku": "Sikat", "total_qty": 7},   # bukan anggota grup
    ]
    out = combine_groups(rows, groups=groups)
    by = {r["sku"]: r["total_qty"] for r in out}
    assert by == {"Body": 12, "Sikat": 7}
    breakdown = next(r["breakdown"] for r in out if r["sku"] == "Body")
    assert breakdown == "Body1 (5x1) + Body2 (2x2) + Body (3x1)"


def test_empty_and_no_groups():
    assert combine_groups([], groups={"G": [("X", 1)]}) == []
    rows = [{"sku": "X", "total_qty": 1}]
    assert combine_groups(rows, groups={}) == rows


def test_export_path():
    p = export_excel_path(r"C:\pdf\FO 12 SHP.pdf")
    assert p.parent.name == "export excel"
    assert p.name == "FO 12 SHP.xlsx"
    assert export_excel_path(Path("a/b/TT GC TODAY.pdf")).name == "TT GC TODAY.xlsx"


def test_export_layout():
    import tempfile
    from openpyxl import load_workbook
    with tempfile.TemporaryDirectory() as td:
        out = export_to_excel(
            [{"sku": "A1", "total_qty": 2}, {"sku": "B1", "total_qty": 3}],
            output_path=str(Path(td) / "t.xlsx"),
            pdf_name="REKAP BS TES",
        )
        ws = load_workbook(out).active
        assert [c.value for c in ws[1]] == ["Nama", "SKU", "Total Quantity", "Breakdown"]
        assert ws["A2"].value == "REKAP BS TES"
        assert "A2:A3" in {str(r) for r in ws.merged_cells.ranges}
        assert ws["B2"].value == "A1" and ws["C3"].value == 3
        assert ws["B2"].alignment.horizontal != "right" and ws["C2"].alignment.horizontal == "right"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"semua lulus ({len(tests)} tes)")
