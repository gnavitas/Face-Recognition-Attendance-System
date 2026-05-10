# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['as.py'],
    pathex=[],
    binaries=[],
    datas=[('datasets', 'datasets'), ('ui', 'ui'), ('src', 'src'), ('trainer', 'trainer'), ('sound', 'sound'), ('interfaces', 'interfaces'), ('images', 'images'), ('fonts', 'fonts'), ('config.ini', '.')],
    hiddenimports=[],
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
    name='as',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['faceid.ico'],
)
