# -*- mode: python ; coding: utf-8 -*-
# Run from project root: python -m PyInstaller configs/PulseWaveStudio.spec --clean


a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('src/IOC.ico', 'src'), ('src/fonts/MapleMono-NF-CN-ExtraBold.ttf', 'src/fonts')],
    hiddenimports=[
        'src',
        'src.ui',
        'src.ui.main_window',
        'src.ui.wave_canvas',
        'src.ui.range_slider',
        'src.ui.styles',
        'src.ui.panels',
        'src.ui.panels.library_panel',
        'src.ui.panels.canvas_panel',
        'src.ui.panels.func_panel',
        'src.ui.panels.sequence_panel',
        'src.utils',
        'src.utils.data_loader',
        'src.utils.signal_ops',
    ],
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
    name='PulseWaveStudio',
    icon='src/IOC.ico',
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
)
