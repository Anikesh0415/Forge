import os
import sys
import traceback
import PyInstaller.__main__

project_root = os.path.dirname(os.path.abspath(__file__))
spec_path = os.path.join(project_root, "forge.spec")

try:
    PyInstaller.__main__.run([
        '--noconfirm',
        '--distpath', os.path.join(project_root, 'dist'),
        '--workpath', os.path.join(project_root, 'build'),
        spec_path
    ])
    print("[DEBUG] PyInstaller finished run() without exception.")
except Exception as e:
    print(f"[DEBUG EXCEPTION] {e}")
    traceback.print_exc()

dist_dir = os.path.join(project_root, 'dist', 'ForgeAIOS')
print(f"[DEBUG] dist_dir exists: {os.path.exists(dist_dir)}")
if os.path.exists(dist_dir):
    print(f"[DEBUG] dist_dir contents: {os.listdir(dist_dir)}")
