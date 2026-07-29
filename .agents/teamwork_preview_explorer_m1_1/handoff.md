# Handoff Report — Explorer 1

**Milestone 1: Cross-Platform One-Click Installer & Production Bundler Analysis**

---

## 1. Observation

### 1.1 Existing System Components & Code Paths
- **Backend Entry Point (`server.py`)**:
  - File: `E:\AIF_Project\server.py` (551 lines)
  - WebSocket Server: Line 504: `websockets.serve(self.ws_handler, "0.0.0.0", 8765)`
  - ReAct & VLM Agent Integration: Lines 265-276 calls `plan_task(instruction, update_ui)` from `src/agent_loop.py`
- **Agent Loop & VLM Pipeline Integration (`src/agent_loop.py`)**:
  - File: `E:\AIF_Project\src\agent_loop.py` (232 lines)
  - Line 9: `from src.vlm_pipeline.tests.run_inference import run_vlm_inference`
  - Line 75: `vlm_result = run_vlm_inference(screenshot_path, instruction)`
- **SYCL Inference & Hardware Capabilities (`src/vlm_pipeline/tests/run_inference.py`)**:
  - File: `E:\AIF_Project\src\vlm_pipeline\tests\run_inference.py` (92 lines)
  - Environment variables configured (lines 27-29):
    - `SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS = "1"`
    - `ZES_ENABLE_SYSMAN = "1"`
    - `GGML_SYCL_DEBUG = "0"`
  - Compiled Binaries Location: `E:\AIF_Project\src\vlm_pipeline\llama.cpp\build\bin\Release\`
    - Executables confirmed: `llama-server.exe`, `llama-mtmd-cli.exe`
    - Dynamic Libraries confirmed: `llama-server-impl.dll`, `llama.dll`
  - Device query result (`llama-server.exe --list-devices`):
    - `SYCL0: Intel(R) Arc(TM) 130V GPU (8GB) (8080 MiB, 7527 MiB free)`
- **Hugging Face Model Repository**:
  - Repo ID: `bartowski/Qwen2-VL-2B-Instruct-GGUF`
  - Files listed in repo via `huggingface_hub` `HfApi().list_repo_files`:
    - `Qwen2-VL-2B-Instruct-Q4_K_M.gguf`
    - `mmproj-Qwen2-VL-2B-Instruct-f16.gguf`
  - Current Local `models/` folder: `E:\AIF_Project\models\` contains `qwen2.5-3b-instruct-q4_k_m.gguf`. Missing `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` and `mmproj-Qwen2-VL-2B-Instruct-f16.gguf`.
- **Python Environment Dependencies (`venv`)**:
  - `huggingface_hub` version 1.23.0 is installed in `.\venv`.
  - `PyInstaller` is **not currently installed** in `.\venv` (`ModuleNotFoundError: No module named 'PyInstaller'`).

---

## 2. Logic Chain

1. **Target Architecture**:
   - Milestone 1 requires packaging `server.py` into a standalone executable via `forge_builder.py` and `forge.spec`.
   - On boot, the entry point must verify local `models/` directory, stream missing Qwen2-VL weights via `huggingface_hub`, spawn `llama-server.exe` with SYCL parameters, poll readiness on `http://127.0.0.1:8080/health`, and start `server.py` on port `8765`.

2. **Packaging Strategy (`--onedir` vs `--onefile`)**:
   - Because `llama-server.exe`, its native DLLs (`llama.dll`, `llama-server-impl.dll`), and model GGUF files total multi-gigabytes, `--onefile` would cause severe startup latency due to unpacking to `%TEMP%` on every launch.
   - Therefore, `--onedir` strategy must be used, bundling the executable into `dist/ForgeAIOS/`.

3. **Model Auto-Download Requirements**:
   - Qwen2-VL is a vision-language model; `llama-server` requires both `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` and its multimodal projector `mmproj-Qwen2-VL-2B-Instruct-f16.gguf`.
   - Both files must be checked in `models/` and downloaded from `bartowski/Qwen2-VL-2B-Instruct-GGUF` using `huggingface_hub.hf_hub_download(..., local_dir=models_dir, local_dir_use_symlinks=False)`.

4. **SYCL GPU Hardware Activation**:
   - Intel Arc GPU acceleration requires `SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1` and `ZES_ENABLE_SYSMAN=1`.
   - Launching `llama-server.exe` with `-m models/Qwen2-VL-2B-Instruct-Q4_K_M.gguf --mmproj models/mmproj-Qwen2-VL-2B-Instruct-f16.gguf -ngl 99 --host 127.0.0.1 --port 8080 -c 8192 -b 4096 --temp 0.1` ensures all layers are offloaded to `SYCL0: Intel(R) Arc(TM) 130V GPU`.

5. **Server Boot Synchronization**:
   - Polling `http://127.0.0.1:8080/health` with exponential backoff / loop ensures `server.py` WebSocket instance on port 8765 only opens after VLM inference is operational.

---

## 3. Caveats

- **PyInstaller Dependency**: `pyinstaller` package is not yet installed in the `venv` environment. `forge_builder.py` must install `pyinstaller` (e.g. `pip install pyinstaller`) before compiling `forge.spec`.
- **System Memory / Disk Requirement**: Downloading `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` (~1.5GB) and `mmproj-Qwen2-VL-2B-Instruct-f16.gguf` (~600MB) requires ~2.5GB free disk space in `models/`.
- **Windows Subprocess Console Flags**: On Windows, spawning `llama-server.exe` as a background process should use `creationflags=subprocess.CREATE_NO_WINDOW` or `subprocess.DETACHED_PROCESS` to prevent pop-up console windows during GUI operation.

---

## 4. Conclusion

The specification for Milestone 1 is fully investigated and feasible. The recommended implementation plan comprises:
1. `forge_builder.py`: Python automation script to handle virtual environment check, PyInstaller invocation, and release folder compilation.
2. `forge.spec`: PyInstaller specification with `--onedir` bundle configuration, hidden imports inventory, binary bundling (`llama-server.exe` + DLLs), and static assets (`ui/`, `config.json`, `data/`).
3. Model Downloader Module: Uses `huggingface_hub` `hf_hub_download` targeting repo `bartowski/Qwen2-VL-2B-Instruct-GGUF` for model and mmproj files.
4. Launcher Orchestration: Enforces SYCL environment flags, launches `llama-server` on port 8080 with `-ngl 99`, polls `/health`, and boots `server.py` on port 8765.

Full technical details and code snippets are documented in `E:\AIF_Project\.agents\teamwork_preview_explorer_m1_1\analysis.md`.

---

## 5. Verification Method

To verify the implementation once built by Worker 1:

1. **Verify Builder Execution**:
   ```cmd
   .\venv\Scripts\python.exe forge_builder.py
   ```
   *Expected result*: PyInstaller builds successfully, generating `dist\ForgeAIOS\` directory with `ForgeAIOS.exe` (or `server.exe`), `bin\llama-server.exe`, and bundled dependencies.

2. **Verify Auto-Downloader**:
   - Ensure `models/Qwen2-VL-2B-Instruct-Q4_K_M.gguf` is absent.
   - Run executable from `dist\ForgeAIOS\`.
   - *Expected result*: Application logs download progress for `bartowski/Qwen2-VL-2B-Instruct-GGUF` and populates `models/`.

3. **Verify SYCL llama-server Boot**:
   ```cmd
   netstat -ano | findstr 8080
   ```
   *Expected result*: `llama-server.exe` process is active listening on port 8080 with Intel Arc GPU offloading.

4. **Verify WebSocket Server Launch**:
   ```cmd
   netstat -ano | findstr 8765
   ```
   *Expected result*: `server.py` process is active listening on port 8765.
