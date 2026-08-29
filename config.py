"""
Konfigurasi parser PDF.
Adjust regex pattern sesuai format PDF kamu.
"""

# Regex pattern untuk extract data dari satu baris PDF
# Grup 1: SKU, Grup 2: Nama Produk, Grup 3: Quantity
# Contoh baris: "Bodymask2  Body Mask Whitening  5"
# Atau: "Bodymask2 | Body Mask Whitening | 5"

# Pattern default - pisahkan dengan spasi atau tab
# Adjust sesuai format PDF asli kamu
LINE_PATTERN = r"^(.+?)\s{2,}(.+?)\s{2,}(\d+)\s*$"

# Alternatif: jika dipisah dengan pipe |
# LINE_PATTERN = r"^(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*$"

# PDF reader mode: "text" atau "ocr" atau "auto"
# "text" = coba baca teks dulu
# "ocr" = pakai OCR langsung
# "auto" = coba teks, jika kosong pakai OCR
PDF_READ_MODE = "auto"

# OCR language (ISO 639-2 codes, + untuk tambah)
# "ind" = Indonesia, "eng" = Inggris
OCR_LANGUAGES = "ind+eng"

# Output filename
OUTPUT_FILENAME = "hasil_rekap.xlsx"

# Sheet name di Excel
EXCEL_SHEET_NAME = "Rekap SKU"

# ============================================================
# KILL SWITCH - Remote Shutdown via GitHub Gist
# ============================================================
# Cara setup:
# 1. Buat GitHub Gist baru (https://gist.github.com)
# 2. Isi dengan JSON: {"active": true, "message": "", "shutdown_at": null}
# 3. Set Gist sebagai Public
# 4. Copy Gist ID dari URL: https://gist.github.com/user/GIST_ID
# 5. Paste Gist ID di bawah ini
#
# Untuk mematikan app:
# - Edit Gist → set "active": false
# - Atau set "shutdown_at": "2026-08-22T18:00:00"
# ============================================================

KILL_SWITCH_ENABLED = True
KILL_SWITCH_GIST_ID = "YOUR_GIST_ID_HERE"
