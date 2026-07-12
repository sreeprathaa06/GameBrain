import os
import subprocess
import sys

def create_spec_file():
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# We use the current directory as the project root
project_root = os.path.abspath('.')
# Ensure project root is in path during build
sys.path.insert(0, project_root)

datas = [
    ('app/assets', 'app/assets'),
    ('assets', 'assets'),
    ('configs', 'configs'),
    ('saved_models', 'saved_models'),
    ('logs', 'logs'),
    ('training_logs', 'training_logs'),
    ('graphs', 'graphs')
]

# Filter datas to only include existing directories
existing_datas = []
for src, dst in datas:
    if os.path.exists(src):
        existing_datas.append((src, dst))

hiddenimports = [
    'app',
    'app.main',
    'app.pages',
    'app.widgets',
    'app.utils',
    'controllers',
    'environments',
    'play_modes',
    'rl'
]

# Tell PyInstaller to aggressively collect everything in these packages
# by extending the hook directories or explicitly setting collect_submodules.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('rl')
hiddenimports += collect_submodules('controllers')
hiddenimports += collect_submodules('environments')
hiddenimports += collect_submodules('play_modes')

# Remove duplicates
hiddenimports = list(set(hiddenimports))

a = Analysis(
    ['app/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=existing_datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='GameBrain',
    icon='assets/logo.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx=True,
    upx_exclude=[],
    name='GameBrain',
)
"""
    with open("GameBrain.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("Generated GameBrain.spec")

def main():
    print("Starting build process for GameBrain2...")

    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Generate the spec file
    create_spec_file()

    # Build command using the generated spec file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",      # Overwrite output directory without asking
        "GameBrain.spec"
    ]

    print("Running PyInstaller with command:")
    print(" ".join(cmd))

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\nBuild successful! You can find the executable in the 'dist/GameBrain' folder.")
    else:
        print("\nBuild failed. Check the logs above.")

if __name__ == "__main__":
    main()
