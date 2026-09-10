# Rekap SKU PDF Scanner

**Version: 2.1.0**

Aplikasi desktop Python untuk memindai file PDF, mengekstrak data produk (SKU, Nama, Quantity), mengelompokkan berdasarkan SKU, dan mengekspor hasil rekap ke Excel.

## Download (EXE)

**Untuk user yang tidak paham coding, langsung download:**

1. Buka [Releases](https://github.com/syahrilardiansyah/Rekap_SKU_PDF/releases)
2. Download `RekapSKU-v2.1.0.zip`
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
- **Split Bundle** — bundle SKU otomatis di-split per komponen produk (contoh: `BEACH+WATERMELON` → BEACH + WATERMELON)
- **PDF Text Reader** — membaca PDF berbasis teks langsung
- **OCR Engine** — membaca PDF scan/gambar via Tesseract OCR
- **Configurable Parser** — regex pattern bisa disesuaikan dengan format PDF
- **Rekap SKU** — mengelompokkan data dan menjumlahkan quantity per SKU
- **Export Excel** — output ke file `.xlsx` dengan format rapi
- **Remote Kill Switch** — kontrol akses aplikasi dari jarak jauh via GitHub Gist

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

## Remote Kill Switch

Kill switch memungkinkan developer mengontrol akses aplikasi dari jarak jauh.

### Cara Kerja

- **Aplikasi user** mengecek status ke GitHub Gist setiap kali dibuka
- **Developer** mengubah status via `admin.py` → semua user terdampak
- **Tanpa internet** → app tetap jalan (menggunakan cache lokal)
- **User tidak perlu akun GitHub** — hanya developer yang butuh

### Kompatibilitas

| Skenario | Hasil |
|----------|-------|
| Kill switch ON + internet | App jalan |
| Kill switch OFF | App mati |
| Kill switch ON + no internet (pertama kali) | App mati (perlu internet sekali saja) |
| Kill switch ON + no internet (sudah pernah jalan) | App jalan (cache lokal) |
| Kill switch ON, berpindah device | App jalan (asal ada internet pertama kali) |

### Setup (Developer)

1. Buat [GitHub Personal Access Token](https://github.com/settings/tokens)
   - Scope: `gist`
2. Buat [GitHub Gist](https://gist.github.com) baru (public)
   - Filename: `kill_switch.json`
   - Content:
   ```json
   {"active": true, "message": "", "shutdown_at": null}
   ```
3. Copy Gist ID dari URL
4. Jalankan:
   ```bash
   python admin.py
   ```
5. Masukkan Gist ID dan Token saat diminta

### Menu Admin

```
1. Lihat Status        - Cek status kill switch saat ini
2. Toggle ON/OFF       - Aktifkan/nonaktifkan aplikasi
3. Set Shutdown Jadwal  - Matikan aplikasi di waktu tertentu
4. Update Config       - Ganti Gist ID atau Token
0. Keluar
```

### Contoh Penggunaan

**Matikan semua aplikasi user:**
```
Pilih: 2
Status: OFF (Aplikasi mati)
```

**Hidupkan kembali:**
```
Pilih: 2
Status: ON (Aplikasi aktif)
```

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
├── admin.py                # Admin kill switch
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
    └── kill_switch.py      # Remote shutdown + cache
```

## Changelog

### v2.1.0 (2026-09-10)
- Fix: bypass GitHub CDN cache untuk kill switch (cache-busting)
- Fix: self-destruct disabled di EXE mode
- Add: local cache untuk kill switch (offline support)
- Add: log file untuk debugging kill switch

### v2.0.0 (2026-09-09)
- Add: BigSeller PDF format support
- Add: Bundle splitting (BEACH+WATERMELON → BEACH + WATERMELON)
- Add: New UI with row numbers, alternating colors, green qty
- Add: Remote kill switch via GitHub Gist
- Add: Admin CLI tool (`admin.py`)
- Add: Auto-detect PDF format (BigSeller vs generic)
- Add: EXE build script (`build.bat`)
- Fix: Tesseract path detection for PyInstaller

## License

MIT License — lihat [LICENSE](LICENSE) untuk detail.
