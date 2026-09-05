# Rekap SKU PDF Scanner

**Version: 2.0.0**

Aplikasi desktop Python untuk memindai file PDF, mengekstrak data produk (SKU, Nama, Quantity), mengelompokkan berdasarkan SKU, dan mengekspor hasil rekap ke Excel.

## Download (EXE)

**Untuk user yang tidak paham coding, langsung download:**

1. Buka [Releases](https://github.com/syahrilardiansyah/Rekap_SKU_PDF/releases)
2. Download `RekapSKU-v2.0.0.zip`
3. Extract ke sembarang folder
4. Double-click `RekapSKU.exe`
5. Langsung pakai - tidak perlu install apapun!

**Penting:**
- Folder `tesseract/` harus tetap satu folder dengan `RekapSKU.exe`
- Jangan hapus folder `tesseract/`

## Cara Pakai

1. Buka aplikasi `RekapSKU.exe`
2. Klik **Pilih PDF** → pilih file PDF
3. Pilih mode baca (auto/text/ocr)
4. Klik **Proses PDF**
5. Lihat hasil rekap di tabel
6. Klik **Export ke Excel** → pilih lokasi simpan

## Fitur

- **BigSeller Auto-Detect** — otomatis deteksi format PDF BigSeller
- **Split Bundle** — bundle SKU otomatis di-split per komponen produk
- **PDF Text Reader** — membaca PDF berbasis teks langsung
- **OCR Engine** — membaca PDF scan/gambar via Tesseract OCR
- **Configurable Parser** — regex pattern bisa disesuaikan dengan format PDF
- **Rekap SKU** — mengelompokkan data dan menjumlahkan quantity per SKU
- **Export Excel** — output ke file `.xlsx` dengan format rapi
- **Remote Kill Switch** — kontrol akses via GitHub Gist

## Keamanan

| Aspek | Status | Keterangan |
|-------|--------|------------|
| Data tetap lokal | Aman | Tidak ada data yang dikirim ke internet |
| Tidak ada tracking | Aman | Tidak ada analytics atau telemetry |
| Source code public | Aman | Bisa di-review di GitHub |
| Open source libraries | Aman | PyMuPDF, Tesseract, Pandas sudah trusted |
| EXE tidak di-sign | Warning | Windows mungkin tampilkan warning pertama kali |

**Catatan penting:**
- Aplikasi ini **offline** — semua proses terjadi di komputer user
- **Tidak ada data** yang dikirim ke server manapun
- File PDF dan Excel tetap di komputer user
- Windows SmartScreen mungkin warning karena EXE tidak di-sign certificate — klik "More info" → "Run anyway"

## Tech Stack

| Komponen | Library |
|----------|---------|
| PDF Reader | PyMuPDF |
| OCR | Tesseract + pytesseract |
| Parser | Regex (configurable) |
| Data Processing | pandas |
| Export | openpyxl |
| UI | CustomTkinter |

## Instalasi (Developer)

### Prerequisites

- Python 3.10+
- Tesseract OCR ([install](https://github.com/UB-Mannheim/tesseract/wiki))
  - Pastikan path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Install bahasa Indonesia: download `ind.traineddata` ke folder `tessdata`

### Setup

```bash
# Clone repo
git clone https://github.com/syahrilardiansyah/Rekap_SKU_PDF.git
cd Rekap_SKU_PDF

# Install dependencies
pip install -r requirements.txt
```

### Jalankan

```bash
python run.py
```

### Build ke EXE

```bash
# Jalankan script build
build.bat
```

Output: `dist/RekapSKU.exe`

## Konfigurasi

Edit `config.py` untuk menyesuaikan:

```python
# Format PDF: "auto", "generic", "bigseller"
PDF_FORMAT = "auto"

# Regex pattern untuk extract data (generic format)
LINE_PATTERN = r"^(.+?)\s{2,}(.+?)\s{2,}(\d+)\s*$"

# Mode baca PDF: "auto", "text", "ocr"
PDF_READ_MODE = "auto"

# Bahasa OCR
OCR_LANGUAGES = "ind+eng"
```

## Struktur Project

```
Rekap_SKU_PDF/
├── run.py                  # Entry point
├── config.py               # Konfigurasi
├── build.bat               # Script build ke EXE
├── requirements.txt        # Dependencies
├── LICENSE                  # Lisensi
└── app/
    ├── main.py             # UI (CustomTkinter)
    ├── pdf_reader.py       # PDF text reader
    ├── ocr_engine.py       # OCR engine
    ├── parser.py           # Extract SKU/Nama/Qty (auto-detect format)
    ├── bigseller_parser.py # Parser khusus format BigSeller
    ├── rekap.py            # Group by SKU + split bundle
    ├── export.py           # Export to Excel
    └── kill_switch.py      # Remote shutdown
```

## License

MIT License — lihat [LICENSE](LICENSE) untuk detail.
