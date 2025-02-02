# -*- mode: python ; coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

block_cipher = None

a = Analysis(
    ['src/wxc_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models/lid.176.bin', 'models'),
        ('assets/AppIcon.icns', '.')
    ],
    hiddenimports=[
        'fasttext',
        'gtts',
        'langdetect',
        'PyQt5.QtPrintSupport'
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
    name='WenxuecityTTS',
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
    icon='assets/AppIcon.icns',
)
app = BUNDLE(
    exe,
    name='WenxuecityTTS.app',
    icon='assets/AppIcon.icns',
    bundle_identifier='wenxuecity-tts',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleDisplayName': 'Wenxuecity TTS',
        'CFBundleName': 'Wenxuecity',
        'CFBundleDevelopmentRegion': 'English',
    },
)
