# -*- mode: python ; coding: utf-8 -*-
# Run from project root: python -m PyInstaller configs/DG-LAB-Wave-Editer.spec --clean

import os
import sys

from PyQt6.QtCore import QLibraryInfo

ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

if sys.platform == 'win32':
    windows_root = os.environ['SystemRoot']
    os.environ['PATH'] = os.pathsep.join([
        QLibraryInfo.path(QLibraryInfo.LibraryPath.BinariesPath),
        os.path.dirname(sys.executable),
        sys.base_prefix,
        os.path.join(sys.base_prefix, 'DLLs'),
        os.path.join(windows_root, 'System32'),
        windows_root,
    ])


a = Analysis(
    [os.path.join(ROOT, 'src/main.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[(os.path.join(ROOT, 'src/IOC.ico'), 'src'), (os.path.join(ROOT, 'src/fonts/MapleMono-NF-CN-ExtraBold.ttf'), 'src/fonts')],
    hiddenimports=[
        'src',
        'src.domain',
        'src.domain.models',
        'src.services',
        'src.services.id_service',
        'src.services.wave_service',
        'src.services.sequence_service',
        'src.repositories',
        'src.repositories.json5_library_repository',
        'src.repositories.json5_pulse_repository',
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
    name='DG-LAB-Wave-Editer',
    icon=os.path.join(ROOT, 'src/IOC.ico'),
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
