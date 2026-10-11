# Rekap SKU PDF Scanner

**Version: 2.1.10**

Aplikasi desktop Python untuk memindai file PDF, mengekstrak data produk (SKU, Nama, Quantity), mengelompokkan berdasarkan SKU, dan mengekspor hasil rekap ke Excel.

## Download (EXE)

**Untuk user yang tidak paham coding, langsung download:**

1. Buka [Releases](https://github.com/syahrilardiansyah/Rekap_SKU_PDF/releases)
2. Download `RekapSKU-v2.1.10.zip`
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
- **SKU Aliasing** — produk dengan nama berbeda digabung otomatis (contoh: `DeepClean` + `DeepClean1500gr` → DeepClean)
- **Freebie Exclusion** — item freebie otomatis di-exclude dari hasil rekap (edit `freebie_keywords.txt` tanpa rebuild)
- **Gabung SKU Multi-PCS** — SKU isi banyak pcs digabung jadi 1 baris, `BodyMask1*1 + BodyMask2*2 + BodyMask3*3` → `BodyMask` (edit `sku_groups.txt` tanpa rebuild)
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

## Freebie Keywords (editable)

Edit `freebie_keywords.txt` — satu keyword per baris, `#` untuk komentar. Tidak perlu rebuild EXE.

**Pencocokan hanya ke kolom SKU** (bukan nama/deskripsi produk), supaya produk legit yang kebetulan menyebut freebie di deskripsinya (contoh: `Laundry Bag ... Jaring Baju Kotor`) tidak salah di-exclude. Konsekuensinya keyword yang mengandung spasi (`sticker pack`, `gelang couple`, `free claim`) tidak akan pernah cocok karena SKU tidak punya spasi — pakai versi tanpa spasi (`stickerpack`, `gelangcouple`).

**Default keywords:**
`stickerpack`, `sticker pack`, `sticker`, `gelangcouple`, `gelang couple`, `tester`, `freebiest`, `free claim`, `freegelang`, `freesticker`, `kamper`, `kawatcuci`, `sikatsudut`, `sikatmini`, `spondaki`, `jaring`, `sarungtangan`, `glove`, `sponmandi`

## Gabung SKU Multi-PCS (editable)

SKU yang isinya lebih dari 1 pcs dijual terpisah dengan suffix angka. Contoh di `sku_groups.txt`:

```
BodyMask = BodyMask1*1, BodyMask2*2, BodyMask3*3
BodyLotion = BodyLotion1*1, BodyLotion2*2
LapMicrofiber = LapMicrofiber2*2
BoxMicrofiber = LapMicrofiber2*1
```

Artinya: `BodyMask` = `BodyMask1`×1 + `BodyMask2`×2 + `BodyMask3`×3, dan `BodyLotion` = `BodyLotion1`×1 + `BodyLotion2`×2.

**Satu SKU anggota boleh dipakai lebih dari satu grup** — `LapMicrofiber2` dipakai dua kali: `LapMicrofiber` (isi 2 → ×2) dan `BoxMicrofiber` (1 box per pack → ×1). Contoh 9 pack `LapMicrofiber2`:

```
LapMicrofiber   = 9 x 2 = 18
BoxMicrofiber   = 9 x 1 = 9
```

Contoh konkret (10 order `BodyMask1` + 4 order `BodyMask2` isi 2 + 2 order `BodyMask3` isi 3):

```
BodyMask = 10 + 4*2 + 2*3 = 24
```

- Satu baris per grup, format `NamaHasil = AngkaSKU*multiplier, ...`
- Pencocokan **tidak membedakan huruf besar/kecil** (`BODYMASK1` = `BodyMask1`)
- Baris anggota grup (`BodyMask1/2/3`, `BodyLotion1/2`, `LapMicrofiber2`) **diganti** jadi 1 baris hasil gabungan di tabel & Excel
- Kolom `Breakdown` di Excel berisi cara hitungnya, mis. `BodyMask1 (64x1) + BodyMask2 (7x2) + BodyMask3 (7x3)`
- `#` untuk komentar, edit tanpa rebuild EXE
- Grup yang tidak dipakai di file tersebut tetap aman — kalau anggotanya nggak ada, barisnya cuma dilewat

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
├── freebie_keywords.txt    # Daftar keyword freebie (editable)
├── sku_groups.txt          # Aturan gabung SKU multi-PCS (editable)
├── requirements.txt        # Dependencies
├── LICENSE                  # Lisensi
└── app/
    ├── main.py             # UI (CustomTkinter)
    ├── pdf_reader.py       # PDF text reader
    ├── ocr_engine.py       # OCR engine
    ├── parser.py           # Extract SKU/Nama/Qty (auto-detect format)
    ├── bigseller_parser.py # Parser khusus format BigSeller
    ├── rekap.py            # Group by SKU + split bundle
    ├── sku_group.py        # Gabung SKU multi-PCS
    ├── export.py           # Export to Excel
    └── kill_switch.py      # Remote shutdown + cache
```

## Changelog

### v2.1.10 (2026-10-10)
- Add: Grup `LapMicrofiber = LapMicrofiber2*2` + baris turunan `BoxMicrofiber = LapMicrofiber2*1` (1 box per pack)
- Add: Satu SKU anggota boleh dipakai banyak grup (sebelumnya cuma boleh satu grup per SKU)
- Verified: `TT WF JNT 10-10-2026.pdf` → `LapMicrofiber` 18, `BoxMicrofiber` 9; 6 file lain berubah (semua berisi `LapMicrofiber2`), 17 file tidak berubah

### v2.1.9 (2026-10-10)
- Fix: Quantity dengan pemisah ribuan (`2.839`) tidak dikenali → baris SKU hilang; `TT PB NEW.pdf` cuma kebaca 262, sekarang parse mentah 3012 (persis header "Jumlah Produk: 3.012")
- Verified: `TT PB NEW.pdf` 4 SKU / 3101 setelah split bundle, 23 file lain tidak berubah

### v2.1.8 (2026-10-10)
- Fix: Baris `BubbleWrap+Kardus` salah ke-exclude karena nama produknya mengandung "extra packing" — pengecekan nama sekarang di-skip kecuali SKU-nya material packing (BubbleWrap/Kardus)
- Verified: `T PB 1.pdf` kini 4 SKU / 399 (`BubbleWrap+Kardus` = 1 ikut), 23 file lain tidak berubah

### v2.1.7 (2026-10-10)
- Add: Grup `BodyLotion = BodyLotion1*1 + BodyLotion2*2` (aturan sama dengan BodyMask)
- Add: Freebie keyword `glove`, `sponmandi` — `S FOBB` 163 → 155 (Glove 3 + SponMandi 5 ke-exclude), 22 file lain tidak berubah
- Note: perubahan murni config (`sku_groups.txt` + `freebie_keywords.txt`), tanpa ubah kode

### v2.1.6 (2026-10-10)
- Add: Gabung SKU multi-PCS — `sku_groups.txt` (default `BodyMask1*1 + BodyMask2*2 + BodyMask3*3` → `BodyMask`), edit tanpa rebuild
- Add: Kolom `Breakdown` di Excel berisi cara hitung gabungan
- Fix: Export Excel selalu gagal `ValueError: Length mismatch` (kontrak 3 kolom vs data 2 kolom)

### v2.1.5 (2026-10-10)
- Fix: SKU bundle yang kepotong line-wrap menghasilkan baris palsu (`L`, `mL`, `ns`) — sekarang di-join lewat anchor shelf marker
- Fix: Freebie keyword hanya dicocokkan ke kolom SKU (bukan nama produk) — `LaundryBag40x50CM`, `City100mL`, `Allofme100mL` salah ke-exclude karena deskripsi marketing
- Verified: `SHP PH 10-10-2026.pdf` parse mentah = 39 SKU / 971 unit, cocok persis dengan header PDF

### v2.1.4 (2026-09-28)
- Fix: SKU alias — `Allfome100mL` digabung ke `Allofme100mL` (typo di PDF BigSeller)

### v2.1.3 (2026-09-11)
- Add: SKU aliasing — DeepClean+DeepClean1500gr, Lap2+LapMicrofiber2, Spons+SponsRandom, CharmKuning+CharmSilky
- Add: `BUBBLEWRAP+KARDUS` tetap 1 row (tidak dipecah)
- Add: Freebie — Kamper, KawatCuci, SikatSudut, SikatMini, SponDaki, Jaring, SarungTangan
- Fix: Line wrapping untuk SKU terpotong (`DeepClean1500gr+WATERMEL` + `ON` → `WATERMELON`)
- Fix: Header UI version display

### v2.1.2 (2026-09-11)
- Fix: Hapus keyword "pengiriman" dari skip filter (salah exclude order legitimate)
- Add: `tas` ke freebie keywords

### v2.1.1 (2026-09-10)
- Fix: Line wrapping guard — cegah product description (ada spasi) tidak salah di-join
- Fix: Bundle split before freebie check
- Add: `sticker` ke freebie keywords

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
