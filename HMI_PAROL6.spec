# -*- mode: python ; coding: utf-8 -*-
import pybullet_data
import os

pybullet_data_path = pybullet_data.getDataPath()

a = Analysis(
    ['main.py'],
    pathex=['.', os.path.abspath('.')],
    binaries=[],
    datas=[
        ('PAROL6.urdf', '.'),
        ('brazo-robotico.ico', '.'),
        ('Logo_UTP.png', '.'),
        ('gseea.png', '.'),
        ('meshes', 'meshes'),
        (pybullet_data_path, 'pybullet_data'),
    ],
    hiddenimports=[
        'pybullet',
        'pybullet_data',
        'PyQt5.QtPrintSupport',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HMI_PAROL6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='brazo-robotico.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HMI_PAROL6',
)
