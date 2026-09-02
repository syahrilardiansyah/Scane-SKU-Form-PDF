@echo off
echo ==========================================
echo   Build Rekap SKU PDF Scanner ke EXE
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan! Install Python dulu.
    pause
    exit /b 1
)

:: Install PyInstaller
echo [1/4] Install PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Gagal install PyInstaller!
    pause
    exit /b 1
)

:: Clean old build
echo [2/4] Clean old build...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build EXE
echo [3/4] Building EXE...
echo Ini mungkin butuh beberapa menit...

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "RekapSKU" ^
    --icon "NONE" ^
    --add-data "app\bigseller_parser.py;app" ^
    --add-data "app\export.py;app" ^
    --add-data "app\kill_switch.py;app" ^
    --add-data "app\main.py;app" ^
    --add-data "app\ocr_engine.py;app" ^
    --add-data "app\parser.py;app" ^
    --add-data "app\pdf_reader.py;app" ^
    --add-data "app\rekap.py;app" ^
    --add-data "app\__init__.py;app" ^
    --add-data "config.py;." ^
    --hidden-import "customtkinter" ^
    --hidden-import "pymupdf" ^
    --hidden-import "pytesseract" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "PIL" ^
    --collect-all "customtkinter" ^
    --noconfirm ^
    run.py

if errorlevel 1 (
    echo [ERROR] Build gagal!
    pause
    exit /b 1
)

:: Copy Tesseract ke folder output
echo [4/4] Copy Tesseract OCR...
if not exist "dist\tesseract" mkdir "dist\tesseract"
if not exist "dist\tesseract\tessdata" mkdir "dist\tesseract\tessdata"

:: Copy essential files only
copy "C:\Program Files\Tesseract-OCR\tesseract.exe" "dist\tesseract\" >nul
copy "C:\Program Files\Tesseract-OCR\libtesseract-5.dll" "dist\tesseract\" >nul
copy "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata" "dist\tesseract\tessdata\" >nul
copy "C:\Program Files\Tesseract-OCR\tessdata\ind.traineddata" "dist\tesseract\tessdata\" >nul
copy "C:\Program Files\Tesseract-OCR\tessdata\osd.traineddata" "dist\tesseract\tessdata\" >nul

:: Copy required DLLs
for %%f in (
    libarchive-13.dll
    libcrypto-3-x64.dll
    liblzma-5.dll
    libtiff-6.dll
    zlib1.dll
) do (
    if exist "C:\Program Files\Tesseract-OCR\%%f" (
        copy "C:\Program Files\Tesseract-OCR\%%f" "dist\tesseract\" >nul
    )
)

echo.
echo ==========================================
echo   BUILD BERHASIL!
echo ==========================================
echo.
echo Output: dist\RekapSKU.exe
echo Tesseract: dist\tesseract\
echo.

:: Create zip for distribution
echo Membuat zip untuk distribusi...
powershell -command "Compress-Archive -Path 'dist\*' -DestinationPath 'dist\RekapSKU-v2.0.0.zip' -Force"
if exist "dist\RekapSKU-v2.0.0.zip" (
    echo Zip berhasil: dist\RekapSKU-v2.0.0.zip
) else (
    echo Gagal membuat zip.
)

echo.
echo Untuk menjalankan:
echo   1. Copy folder "dist" ke komputer user
echo   2. Double-click RekapSKU.exe
echo.
echo Untuk upload ke GitHub Releases:
echo   Upload file: dist\RekapSKU-v2.0.0.zip
echo.
pause
