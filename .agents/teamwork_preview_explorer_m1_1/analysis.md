# Milestone 1 Technical Analysis & Implementation Blueprint
**Cross-Platform One-Click Installer & Production Bundler**

---

## 1. Executive Summary & Architecture Overview

Milestone 1 establishes the production-grade packaging and zero-configuration boot pipeline for **Forge AI OS**. The objective is to package `server.py` and all backend dependencies into a standalone, cross-platform executable system using PyInstaller (`forge_builder.py` and `forge.spec`), featuring:

1. **Self-Healing Model Downloader**: Pre-flight verification of local `models/` directory for `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` (and required multimodal vision projector `mmproj-Qwen2-VL-2B-Instruct-f16.gguf`). Auto-downloads missing model weights directly from Hugging Face (`bartowski/Qwen2-VL-2B-Instruct-GGUF`) via `huggingface_hub` with console (`tqdm`) and GUI (`customtkinter`) progress indicators.
2. **SYCL GPU Hardware Bootloader**: Spawns embedded `llama-server.exe` with SYCL backend parameters (`SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1`, `ZES_ENABLE_SYSMAN=1`, `-ngl 99`) targeting Intel Arc GPUs / iGPUs, serving local VLM requests on `http://127.0.0.1:8080`.
3. **Core Backend Orchestrator**: Launches `server.py` WebSocket/HTTP instance on port `8765` once `llama-server` health check returns HTTP 200 OK.
4. **Standalone Packaging**: Production PyInstaller build specification (`forge.spec` & launcher `forge_builder.py`) bundling native DLLs, static frontend assets (`ui/`), configuration files, and Python execution environments into a single portable bundle (`--onedir`).

---

## 2. Current State Analysis

### 2.1 Server Architecture (`server.py`)
- **WebSocket Listener**: Runs on `ws://0.0.0.0:8765` handling real-time UI state sync, voice dictation, intent execution, and UI injection.
- **FSM & Intent Engine**: Uses `AIF_StateMachine` in `src/fsm_module.py` and `agent_loop.py` (`plan_task` / `execute_task_plan`).
- **Dependencies**: Imports modules across `src/` (`stt_module`, `fsm_module`, `fusion_engine`, `agent_loop`, `action_library`, `context_manager`, `execution_manager`, `security`, `logger`, `event_bus`, `config`, `tts_module`).

### 2.2 Inference Hardware & SYCL Backend (`src/vlm_pipeline/`)
- Existing inference logic in `src/vlm_pipeline/tests/run_inference.py` directly executes `llama-mtmd-cli.exe` or `llama-server.exe` compiled in `src/vlm_pipeline/llama.cpp/build/bin/Release/`.
- Tested and confirmed native device support:
  - Device: `SYCL0: Intel(R) Arc(TM) 130V GPU (8GB)` (8080 MiB VRAM).
- Required SYCL Environment Variables:
  - `SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS = "1"`
  - `ZES_ENABLE_SYSMAN = "1"`
  - `GGML_SYCL_DEBUG = "0"`

### 2.3 Model File Inventory (`models/`)
- Current local directory: `models/qwen2.5-3b-instruct-q4_k_m.gguf`.
- Target GGUF Repository: `bartowski/Qwen2-VL-2B-Instruct-GGUF`.
- Files in repository (verified via `HfApi().list_repo_files`):
  1. `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` (Language model weights)
  2. `mmproj-Qwen2-VL-2B-Instruct-f16.gguf` (Multimodal vision projector weights)

---

## 3. PyInstaller Build Specification Design (`forge_builder.py` & `forge.spec`)

### 3.1 `--onedir` Bundle Rationale
- **Why `--onedir` over `--onefile`**:
  - Model binaries (`llama-server.exe`, `llama.dll`, `llama-server-impl.dll`) and model weights are large files (~2GB+).
  - `--onefile` forces PyInstaller to unpack all binaries to `%TEMP%` on every launch, taking 15–30 seconds before launch.
  - `--onedir` creates a clean portable folder structure `dist/ForgeAIOS/` that boots instantly (< 1s execution startup).

### 3.2 Dynamic Path Resolution Strategy
The entry point must dynamically determine whether it is running as a compiled PyInstaller executable (`sys.frozen == True`) or as raw Python source code:

```python
import sys
import os

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running from Python source script
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
BUNDLE_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
MODELS_DIR = os.path.join(BASE_DIR, "models")
```

### 3.3 Hidden Imports Inventory
The following modules must be explicitly declared in `forge.spec` `hiddenimports`:
- `websockets`, `websockets.legacy`, `websockets.legacy.server`, `websockets.legacy.client`
- `customtkinter`, `huggingface_hub`, `tqdm`
- `mss`, `pyautogui`, `pywin32`, `win32gui`, `win32con`, `keyboard`, `pyttsx3`, `sounddevice`, `numpy`, `PIL`, `asyncio`, `faster_whisper`
- `src.stt_module`, `src.fsm_module`, `src.fusion_engine`, `src.agent_loop`, `src.action_library`, `src.context_manager`, `src.execution_manager`, `src.security`, `src.logger`, `src.event_bus`, `src.config`, `src.tts_module`

### 3.4 Data Files (`datas`) & Binaries (`binaries`) Mapping
- **Datas**:
  - `('ui', 'ui')` — Frontend Web Dashboard HTML/JS/CSS assets
  - `('config.json', '.')` — Configuration file
  - `('data', 'data')` — Persistent databases and skills
- **Binaries**:
  - `('src/vlm_pipeline/llama.cpp/build/bin/Release/llama-server.exe', 'bin')`
  - `('src/vlm_pipeline/llama.cpp/build/bin/Release/llama-server-impl.dll', 'bin')`
  - `('src/vlm_pipeline/llama.cpp/build/bin/Release/llama.dll', 'bin')`

---

## 4. Pre-Flight Model Downloader Design (`huggingface_hub`)

### 4.1 Downloader Workflow
1. Check if `models/Qwen2-VL-2B-Instruct-Q4_K_M.gguf` and `models/mmproj-Qwen2-VL-2B-Instruct-f16.gguf` exist.
2. If missing, initialize `huggingface_hub.hf_hub_download`.
3. Provide visual download progress:
   - Console mode: Uses default `huggingface_hub` `tqdm` progress bars.
   - GUI mode: Uses a lightweight `customtkinter` progress window with progress percentage and cancel safety.

### 4.2 Code Implementation Blueprint

```python
import os
from huggingface_hub import hf_hub_download

REPO_ID = "bartowski/Qwen2-VL-2B-Instruct-GGUF"
REQUIRED_FILES = [
    "Qwen2-VL-2B-Instruct-Q4_K_M.gguf",
    "mmproj-Qwen2-VL-2B-Instruct-f16.gguf"
]

def check_and_download_models(models_dir: str, status_callback=None):
    os.makedirs(models_dir, exist_ok=True)
    for filename in REQUIRED_FILES:
        target_path = os.path.join(models_dir, filename)
        if not os.path.exists(target_path):
            msg = f"Downloading missing model file: {filename} from {REPO_ID}..."
            print(msg)
            if status_callback:
                status_callback(msg)
            
            hf_hub_download(
                repo_id=REPO_ID,
                filename=filename,
                local_dir=models_dir,
                local_dir_use_symlinks=False
            )
            print(f"Successfully downloaded {filename}")
```

---

## 5. SYCL `llama-server` Boot & Readiness Pipeline

### 5.1 SYCL Environment Setup
To ensure execution on Intel Arc GPUs, `llama-server` must be launched with:

```python
env = os.environ.copy()
env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
env["ZES_ENABLE_SYSMAN"] = "1"
env["GGML_SYCL_DEBUG"] = "0"
```

### 5.2 Server Execution Arguments
```python
llama_cmd = [
    llama_server_path,
    "-m", os.path.join(models_dir, "Qwen2-VL-2B-Instruct-Q4_K_M.gguf"),
    "--mmproj", os.path.join(models_dir, "mmproj-Qwen2-VL-2B-Instruct-f16.gguf"),
    "-ngl", "99",
    "--host", "127.0.0.1",
    "--port", "8080",
    "-c", "8192",
    "-b", "4096",
    "--temp", "0.1"
]
```

### 5.3 Readiness Verification Loop
Before starting `server.py`, poll `http://127.0.0.1:8080/health`:

```python
import urllib.request
import time

def wait_for_llama_server(host="127.0.0.1", port=8080, timeout=30):
    url = f"http://{host}:{port}/health"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    print(f"llama-server is READY on http://{host}:{port}")
                    return True
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"llama-server failed to respond on port {port} within {timeout} seconds.")
```

---

## 6. End-to-End Execution Sequence (`forge_builder.py` / App Entry Point)

```
[Start Launcher App]
        │
        ▼
[Resolve Base Directory & Models Path]
        │
        ▼
[Check Local models/ for Qwen2-VL GGUF & mmproj]
   ├── Missing ──► [Download via huggingface_hub with console/GUI progress]
   └── Present ──► [Continue]
        │
        ▼
[Spawn llama-server.exe with SYCL Env Flags on Port 8080]
        │
        ▼
[Poll http://127.0.0.1:8080/health until HTTP 200 OK]
        │
        ▼
[Launch server.py WebSocket Server on ws://0.0.0.0:8765]
        │
        ▼
[Open Dashboard UI (Brave/Default Browser / index.html)]
```

---

## 7. Recommended Implementation Specs & Files

### 7.1 `forge.spec` Design
- PyInstaller spec file referencing `server.py` or launcher script.
- Includes hidden imports, datas, and binary dependencies.

### 7.2 `forge_builder.py` Design
- Automation script to:
  1. Verify virtual environment & dependencies (`pip install pyinstaller huggingface_hub`).
  2. Run `pyinstaller --noconfirm forge.spec`.
  3. Validate compiled output directory `dist/ForgeAIOS`.

---

## 8. Verification Strategy

1. **PyInstaller Packaging Verification**:
   - Run `python forge_builder.py`.
   - Verify `dist/ForgeAIOS/ForgeAIOS.exe` (or `server.exe`) is created without PyInstaller build errors.

2. **Auto-Download Verification**:
   - Temporarily rename `models/Qwen2-VL-2B-Instruct-Q4_K_M.gguf`.
   - Launch packaged executable; confirm `huggingface_hub` streams missing model into `models/`.

3. **SYCL & llama-server Boot Verification**:
   - Verify `llama-server.exe` launches silently with `SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1`.
   - Inspect Task Manager / Intel Arc Control panel to confirm GPU utilization on `SYCL0: Intel Arc GPU`.

4. **WebSocket Verification**:
   - Connect to `ws://localhost:8765` via web browser (`ui/index.html`).
   - Confirm state updates and text/voice prompts operate seamlessly.
