# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\Tools\\JMFSubmitter.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['prismasyncjmfjdf', 'requests', 'base64io'],
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
    name='JMFSubmitter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='JMFSubmitter_version_info.txt',
    onefile=True,
)
