# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

project_root = os.path.abspath(SPECPATH)

datas = [
    (os.path.join(project_root, 'ui'), 'ui'),
    (os.path.join(project_root, 'config.json'), '.'),
]

if os.path.exists(os.path.join(project_root, 'src')):
    datas.append((os.path.join(project_root, 'src'), 'src'))
if os.path.exists(os.path.join(project_root, 'data')):
    datas.append((os.path.join(project_root, 'data'), 'data'))
if os.path.exists(os.path.join(project_root, 'config')):
    datas.append((os.path.join(project_root, 'config'), 'config'))
if os.path.exists(os.path.join(project_root, 'dataset')):
    datas.append((os.path.join(project_root, 'dataset'), 'dataset'))

# Collect dynamic native binaries from llama.cpp Release directory into 'bin'
release_bin_dir = os.path.join(project_root, 'src', 'vlm_pipeline', 'llama.cpp', 'build', 'bin', 'Release')
binaries = []
if os.path.exists(release_bin_dir):
    for f in os.listdir(release_bin_dir):
        full_f = os.path.join(release_bin_dir, f)
        if os.path.isfile(full_f) and (f.endswith('.exe') or f.endswith('.dll') or f.endswith('.spv')):
            binaries.append((full_f, 'bin'))

hidden_imports = [
    'websockets',
    'websockets.legacy',
    'websockets.legacy.server',
    'websockets.legacy.client',
    'customtkinter',
    'huggingface_hub',
    'tqdm',
    'mss',
    'pyautogui',
    'pywin32',
    'win32gui',
    'win32con',
    'keyboard',
    'pyttsx3',
    'sounddevice',
    'numpy',
    'PIL',
    'asyncio',
    'faster_whisper',
    'requests',
    'httpx',
    'urllib.request',
    'src.stt_module',
    'src.fsm_module',
    'src.fusion_engine',
    'src.agent_loop',
    'src.action_library',
    'src.context_manager',
    'src.execution_manager',
    'src.security',
    'src.logger',
    'src.event_bus',
    'src.config',
    'src.tts_module',
    'src.utils.migrate_memory',
    'src.hud',
    'src.memory_manager',
    'src.memory_buffer',
] + collect_submodules('customtkinter') + collect_submodules('huggingface_hub')

excludes = [
    'torch',
    'torchvision',
    'torchaudio',
    'pandas',
    'matplotlib',
    'scipy',
    'sympy',
    'tensorboard',
    'lxml',
    'pyarrow',
    'tkinter.test',
    'unittest',
]

a = Analysis(
    ['forge_launcher.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ForgeAIOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ForgeAIOS',
)
