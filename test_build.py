import os
import sys
import PyInstaller.__main__

project_root = os.path.dirname(os.path.abspath(__file__))
spec_path = os.path.join(project_root, "forge.spec")

print(f"Project root: {project_root}")
print(f"Spec path: {spec_path}")

PyInstaller.__main__.run([
    '--noconfirm',
    '--distpath', os.path.join(project_root, 'dist'),
    '--workpath', os.path.join(project_root, 'build'),
    spec_path
])

dist_dir = os.path.join(project_root, 'dist', 'ForgeAIOS')
exe_file = os.path.join(dist_dir, 'ForgeAIOS.exe')

print(f"Checking dist_dir: {dist_dir} -> Exists: {os.path.exists(dist_dir)}")
print(f"Checking exe_file: {exe_file} -> Exists: {os.path.exists(exe_file)}")

if os.path.exists(dist_dir):
    print("Files in dist/ForgeAIOS:")
    for root, dirs, files in os.walk(dist_dir):
        print(root, dirs, files[:5])
