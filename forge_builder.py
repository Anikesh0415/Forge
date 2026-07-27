import os
import sys
import shutil

def check_and_install_pyinstaller():
    """Ensures pyinstaller is installed in the current python environment."""
    try:
        import PyInstaller
        print(f"[FORGE BUILDER] PyInstaller {PyInstaller.__version__} is already installed.")
    except ImportError:
        print("[FORGE BUILDER] PyInstaller not found. Installing via pip...")
        import subprocess
        cmd = [sys.executable, "-m", "pip", "install", "pyinstaller"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[FORGE BUILDER ERROR] Failed to install pyinstaller:\n{res.stderr}")
            sys.exit(1)
        print("[FORGE BUILDER] Successfully installed PyInstaller.")

def build_forge_bundle():
    """Compiles the Forge AI OS standalone bundle using PyInstaller."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(project_root, "forge.spec")
    
    if not os.path.exists(spec_file):
        print(f"[FORGE BUILDER ERROR] Spec file not found at {spec_file}")
        sys.exit(1)
        
    check_and_install_pyinstaller()
    
    dist_path = os.path.join(project_root, "dist")
    work_path = os.path.join(project_root, "build")
    shutil.rmtree(work_path, ignore_errors=True)
    os.makedirs(dist_path, exist_ok=True)
    
    print("=" * 60)
    print("  FORGE AI OS - PRODUCTION BUNDLE COMPILER  ")
    print("=" * 60)
    print(f"[FORGE BUILDER] Project Root: {project_root}")
    print(f"[FORGE BUILDER] Running PyInstaller on {spec_file}...")
    
    import PyInstaller.__main__
    
    PyInstaller.__main__.run([
        '--noconfirm',
        '--distpath', dist_path,
        '--workpath', work_path,
        spec_file
    ])
    
    dist_dir = os.path.join(dist_path, "ForgeAIOS")
    exe_file = os.path.join(dist_dir, "ForgeAIOS.exe")
    
    if not os.path.exists(dist_dir) or not os.path.exists(exe_file):
        print(f"[FORGE BUILDER ERROR] Output executable not found at {exe_file}")
        sys.exit(1)
        
    print("=" * 60)
    print(" [FORGE BUILDER SUCCESS] Bundle compiled successfully! ")
    print("=" * 60)
    print(f"Bundle Location: {dist_dir}")
    print(f"Executable Path: {exe_file}")
    
    bin_dir = os.path.join(dist_dir, "bin")
    if os.path.exists(bin_dir):
        bin_files = os.listdir(bin_dir)
        print(f"Native Binaries Bundled ({len(bin_files)} files): {', '.join(bin_files[:5])}...")
    else:
        print("[FORGE BUILDER WARNING] Native bin directory not found in dist.")

if __name__ == "__main__":
    build_forge_bundle()
