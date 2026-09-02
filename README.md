# Rekap SKU PDF Scanner

**Version: 2.0.0**

Aplikasi desktop Python untuk memindai file PDF, mengekstrak data produk (SKU, Nama, Quantity), mengelompokkan berdasarkan SKU, dan mengekspor hasil rekap ke Excel.

## Fitur

- **BigSeller Auto-Detect** — otomatis deteksi format PDF BigSeller
- **Split Bundle** — bundle SKU otomatis di-split per komponen produk
- **PDF Text Reader** — membaca PDF berbasis teks langsung
- **OCR Engine** — membaca PDF scan/gambar via Tesseract OCR
- **Configurable Parser** — regex pattern bisa disesuaikan dengan format PDF
- **Rekap SKU** — mengelompokkan data dan menjumlahkan quantity per SKU
- **Export Excel** — output ke file `.xlsx` dengan format rapi
- **Remote Kill Switch** — kontrol akses via GitHub Gist

## Tech Stack

| Komponen | Library |
|----------|---------|
| PDF Reader | PyMuPDF |
| OCR | Tesseract + pytesseract |
| Parser | Regex (configurable) |
| Data Processing | pandas |
| Export | openpyxl |
| UI | CustomTkinter |

## Instalasi

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

## Cara Jalankan

```bash
python run.py
```

## Konfigurasi

Edit `config.py` untuk menyesuaikan:

```python
# Regex pattern untuk extract data
# Grup 1: SKU, Grup 2: Nama Produk, Grup 3: Quantity
LINE_PATTERN = r"^(.+?)\s{2,}(.+?)\s{2,}(\d+)\s*$"

# Mode baca PDF: "auto", "text", "ocr"
PDF_READ_MODE = "auto"

# Bahasa OCR
OCR_LANGUAGES = "ind+eng"
```

### Contoh Format PDF

```
Bodymask2    Body Mask Whitening    5
SerumVC      Serum Vitamin C        2
LotionAL     Lotion Aloe Vera       1
```

Jika format PDF berbeda, sesuaikan `LINE_PATTERN` di `config.py`.

## Remote Kill Switch

Developer dapat mematikan aplikasi secara remote melalui GitHub Gist.

### Setup

1. Buat GitHub Gist baru (public)
2. Isi dengan JSON:
```json
{"active": true, "message": "", "shutdown_at": null}
```
3. Copy Gist ID dari URL
4. Paste ke `config.py`:
```python
KILL_SWITCH_GIST_ID = "YOUR_GIST_ID_HERE"
```

### Shutdown

Edit Gist → set `"active": false` → semua user tidak bisa menjalankan app.

## Struktur Project

```
Rekap_SKU_PDF/
├── run.py                  # Entry point
├── config.py               # Konfigurasi
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
