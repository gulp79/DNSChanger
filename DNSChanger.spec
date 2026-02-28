# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Percorso della directory del progetto
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

block_cipher = None

a = Analysis(
    ['dns_changer.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        ('dns_providers.yaml', '.'),
    ],
    hiddenimports=[
        'pydantic',
        'pydantic.fields',
        'pydantic.main',
        'yaml',
        'customtkinter',
        'tkinter',
        'tkinter.messagebox',
        'models',
        'models.dns_provider',
        'core',
        'core.dns_loader',
        'core.dns_verifier',
        'core.migration',
        'ps',
        'ps.ps_adapter',
        'ps.doh_manager',
        'ui',
        'ui.main_window',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DNSChanger',
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
    uac_admin=True,
)
