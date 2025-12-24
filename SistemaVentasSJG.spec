# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\zantr\\OneDrive\\Documentos\\GitHub\\Proyecto-Metodologia-Sistemas-II\\connection_data.json', '.'), ('C:\\Users\\zantr\\OneDrive\\Documentos\\GitHub\\Proyecto-Metodologia-Sistemas-II\\app', 'app')],
    hiddenimports=['flet', 'pyodbc', 'decimal', 'datetime'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='SistemaVentasSJG',
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
