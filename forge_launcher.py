import os
import sys
import time
import subprocess
import urllib.request
import json
import threading
import logging
import socket
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ForgeBootloader")

def get_base_dir() -> str:
    """Returns the base directory where executable or script is located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_bundle_dir() -> str:
    """Returns PyInstaller bundle dir (_MEIPASS) or script dir."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', get_base_dir())
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
BUNDLE_DIR = get_bundle_dir()
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPO_ID = "Qwen/Qwen2.5-3B-Instruct-GGUF"
MODEL_FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"

def ensure_models_downloaded() -> dict:
    """
    Checks local models/ directory for Qwen2-VL model and mmproj weights.
    Downloads missing files directly from Hugging Face repository via huggingface_hub.
    Returns dict with paths to model and mmproj.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, MODEL_FILENAME)
    
    required = [
        (MODEL_FILENAME, model_path)
    ]
    
    for fname, fpath in required:
        if not os.path.exists(fpath):
            logger.info(f"[FORGE BOOT] Missing model weight: {fname}")
            logger.info(f"[FORGE BOOT] Initiating streaming download from Hugging Face ({REPO_ID})...")
            try:
                from huggingface_hub import hf_hub_download
                hf_hub_download(
                    repo_id=REPO_ID,
                    filename=fname,
                    local_dir=MODELS_DIR,
                    local_dir_use_symlinks=False
                )
                logger.info(f"[FORGE BOOT] Download complete for {fname}")
            except Exception as e:
                logger.error(f"[FORGE BOOT ERROR] Failed to download {fname}: {e}")
                raise RuntimeError(f"Failed to download required model file {fname}: {e}")
        else:
            logger.info(f"[FORGE BOOT] Model weight verified: {fname} ({os.path.getsize(fpath)} bytes)")
            
    return {
        "model_path": model_path
    }

def find_llama_server_binary() -> str:
    """Finds llama-server.exe binary in bundle or source paths."""
    candidates = [
        os.path.join(BUNDLE_DIR, "bin", "llama-server.exe"),
        os.path.join(BASE_DIR, "bin", "llama-server.exe"),
        os.path.join(BUNDLE_DIR, "llama-server.exe"),
        os.path.join(BASE_DIR, "src", "vlm_pipeline", "llama.cpp", "build", "bin", "Release", "llama-server.exe"),
        os.path.join(BASE_DIR, "llama-server.exe"),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return os.path.abspath(cand)
    # Default fallback
    return os.path.abspath(os.path.join(BASE_DIR, "src", "vlm_pipeline", "llama.cpp", "build", "bin", "Release", "llama-server.exe"))

def is_port_in_use(host: str = "127.0.0.1", port: int = 8080) -> bool:
    """Checks if a TCP port is currently in use / bound by any process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        res = sock.connect_ex((host, port))
        return res == 0

def is_llama_server_running(host: str = "127.0.0.1", port: int = 8080) -> bool:
    """Checks if llama-server is already active and responding with HTTP 200 OK on host:port."""
    health_url = f"http://{host}:{port}/health"
    try:
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def boot_llama_server(model_paths: dict, port: int = 8080, host: str = "127.0.0.1") -> subprocess.Popen:
    """
    Spawns llama-server process with SYCL acceleration environment variables.
    Raises RuntimeError if llama-server executable is missing or port conflict occurs.
    """
    llama_exe = find_llama_server_binary()
    logger.info(f"[FORGE BOOT] llama-server executable: {llama_exe}")
    
    if not os.path.exists(llama_exe):
        err_msg = f"llama-server executable not found at: {llama_exe}"
        logger.error(f"[FORGE BOOT ERROR] {err_msg}")
        raise RuntimeError(err_msg)
        
    if is_port_in_use(host, port) and not is_llama_server_running(host, port):
        err_msg = f"Port conflict detected: Port {port} is already in use by another process on {host}"
        logger.error(f"[FORGE BOOT ERROR] {err_msg}")
        raise RuntimeError(err_msg)
        
    env = os.environ.copy()
    env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
    env["ZES_ENABLE_SYSMAN"] = "1"
    env["GGML_SYCL_DEBUG"] = "0"
    
    exe_dir = os.path.dirname(llama_exe)
    if exe_dir and exe_dir not in env.get("PATH", ""):
        env["PATH"] = exe_dir + os.pathsep + env.get("PATH", "")

    cmd = [
        llama_exe,
        "-m", model_paths["model_path"],
        "--host", host,
        "--port", str(port),
        "-c", "2048",
        "-b", "512",
        "--temp", "0.3",
        "--repeat-penalty", "1.15",
        "--image-min-tokens", "1024"
    ]
    
    logger.info(f"[FORGE BOOT] Spawning llama-server process on port {port} (CPU ONLY)...")
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    proc = subprocess.Popen(cmd, env=env, creationflags=creation_flags)
    return proc

def poll_llama_server_health(host: str = "127.0.0.1", port: int = 8080, timeout: int = 60) -> bool:
    """
    Polls llama-server health endpoint http://<host>:<port>/health until HTTP 200 OK.
    """
    health_url = f"http://{host}:{port}/health"
    logger.info(f"[FORGE BOOT] Polling health endpoint: {health_url} (timeout: {timeout}s)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    body = resp.read().decode('utf-8')
                    logger.info(f"[FORGE BOOT] llama-server health check SUCCESS (HTTP 200): {body}")
                    return True
        except Exception:
            pass
        time.sleep(1)
        
    logger.warning(f"[FORGE BOOT WARNING] llama-server health check timed out after {timeout} seconds.")
    return False

def boot_forge_app():
    """Complete one-click boot sequence for Forge AI OS."""
    os.chdir(BASE_DIR)
    logger.info("=" * 60)
    logger.info("  FORGE AI OS - PRODUCTION BOOTLOADER  ")
    logger.info("=" * 60)
    logger.info(f"[FORGE BOOT] Changed working directory to BASE_DIR: {BASE_DIR}")
    
    # Ensure sys.path appends BUNDLE_DIR, BASE_DIR, and src safely without hijacking standard library
    for path_dir in [BUNDLE_DIR, BASE_DIR, os.path.join(BUNDLE_DIR, "src")]:
        abs_path = os.path.abspath(path_dir)
        if os.path.exists(abs_path) and abs_path not in sys.path:
            sys.path.append(abs_path)
        
    # 1. Download/verify model files
    model_paths = ensure_models_downloaded()
    
    # 2. Boot llama-server process lifecycle wrapped safely in try...finally
    llama_proc = None
    try:
        if not is_llama_server_running(port=8080):
            llama_proc = boot_llama_server(model_paths, port=8080)
            # 3. Poll health endpoint and check return value
            healthy = poll_llama_server_health(port=8080, timeout=60)
            if not healthy:
                err_msg = "llama-server health check failed: timed out after 60 seconds"
                logger.error(f"[FORGE BOOT ERROR] {err_msg}")
                raise RuntimeError(err_msg)
        else:
            logger.info("[FORGE BOOT] llama-server is already running and healthy on port 8080.")
            
        # 4. Launch Native UI Dashboard in Brave
        ui_path = os.path.abspath(os.path.join(BASE_DIR, "ui", "index.html")).replace("\\", "/")
        logger.info(f"[FORGE BOOT] Opening Native Dashboard: file:///{ui_path}")
        subprocess.Popen(f'start "" "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe" --app="file:///{ui_path}" --window-size=1280,800', shell=True)

        # 5. Launch server.py WebSocket/HTTP instance on port 8765
        logger.info("[FORGE BOOT] Starting Forge Server backend on port 8765...")
        import server
        server_inst = server.AIF_Server()
        server_inst.start_server()
    finally:
        if llama_proc and llama_proc.poll() is None:
            logger.info("[FORGE BOOT] Terminating embedded llama-server process...")
            try:
                llama_proc.terminate()
                llama_proc.wait(timeout=5)
            except Exception as e:
                logger.warning(f"[FORGE BOOT WARNING] Exception while terminating llama_proc: {e}")

if __name__ == "__main__":
    boot_forge_app()
