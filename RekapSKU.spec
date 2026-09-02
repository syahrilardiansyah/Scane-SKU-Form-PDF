# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('app/bigseller_parser.py', 'app'), ('app/export.py', 'app'), ('app/kill_switch.py', 'app'), ('app/main.py', 'app'), ('app/ocr_engine.py', 'app'), ('app/parser.py', 'app'), ('app/pdf_reader.py', 'app'), ('app/rekap.py', 'app'), ('app/__init__.py', 'app'), ('config.py', '.')]
binaries = []
hiddenimports = ['customtkinter', 'pymupdf', 'pytesseract', 'pandas', 'openpyxl', 'PIL']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RekapSKU',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
