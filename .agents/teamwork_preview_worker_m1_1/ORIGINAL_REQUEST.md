## 2026-07-25T22:38:36Z
You are Worker 1 implementing Milestone 1: Legacy Dependencies Cleanup.
Working directory: E:\AIF_Project\.agents\teamwork_preview_worker_m1_1
Input files to read:
- E:\AIF_Project\.agents\teamwork_preview_explorer_m1_1\handoff.md
- E:\AIF_Project\.agents\teamwork_preview_explorer_m1_1\analysis.md
- E:\AIF_Project\.agents\orchestrator\PROJECT.md

Your task:
1. Create your working directory `E:\AIF_Project\.agents\teamwork_preview_worker_m1_1`.
2. Delete `src/planner.py`.
3. Modify `requirements.txt` to remove legacy vision dependencies: `pytesseract`, `opencv-python`, `mediapipe`.
4. Modify `server.py` to remove legacy imports (`cv2`, `HandTracker`, `plan_task`), legacy routes/endpoints (`confirm_plan`, `reject_plan`), legacy thread (`_camera_worker`), legacy Ollama meeting call (`_run_meeting`), and legacy WS commands (`TOGGLE_MEETING`, `CONFIRM_PLAN`, `REJECT_PLAN`).
5. Modify `src/agent_loop.py`, `tests/test_architecture.py`, and `tests/test_stress.py` to remove all imports and references to `src.planner` / `MultiStagePlanner` / `planner_instance` / `replan_failed_step`.
6. Run the test suite and verification commands using powershell / python / pytest to ensure all imports and existing tests pass cleanly without errors.
7. Document all changes in `E:\AIF_Project\.agents\teamwork_preview_worker_m1_1\changes.md` and write your handoff report in `E:\AIF_Project\.agents\teamwork_preview_worker_m1_1\handoff.md`. Include exact build/test commands run and their full outputs.
8. Send a message to parent orchestrator with your handoff summary.

## 2026-07-27T21:40:15Z
Objective: Implement Milestone 1: Cross-Platform One-Click Installer & Production Bundler.

Detailed Tasks:
1. Ensure PyInstaller is installed in the python environment (`pip install pyinstaller` if needed during build step).
2. Develop `forge_builder.py` and `forge.spec` to package the Forge Python backend (`server.py`) into a standalone OS-native executable bundle in `dist/`.
   - Use `--onedir` bundle configuration so multi-gigabyte models and native binaries stay uncompressed alongside the executable.
   - Package all required dependencies, hidden imports (`websockets.legacy`, `customtkinter`, `huggingface_hub`, `mss`, `pyautogui`, etc.), dynamic native binaries (`llama-server.exe`, `llama.dll`, `llama-server-impl.dll` from `src/vlm_pipeline/llama.cpp/build/bin/Release/`), static assets (`ui/`), and `config.json`.
3. Entry script logic:
   - On launch, check local `models/` directory for `Qwen2-VL-2B-Instruct-Q4_K_M.gguf` (and multimodal projector `mmproj-Qwen2-VL-2B-Instruct-f16.gguf` if missing).
   - If missing, streamingly download official model weights directly from Hugging Face (`bartowski/Qwen2-VL-2B-Instruct-GGUF`) with a progress bar via `huggingface_hub` (`hf_hub_download`).
   - Once verified, set SYCL environment variables (`SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1`, `ZES_ENABLE_SYSMAN=1`), boot `llama-server` process with SYCL parameters (`-ngl 99`, `-c 8192`, `-b 4096`), poll health endpoint (`http://127.0.0.1:8080/health`), and launch the `server.py` WebSocket/HTTP instance on port `8765`.
4. Run build and verification:
   - Execute `python forge_builder.py` to compile the binary in `dist/`.
   - Verify binary existence and boot capabilities.
5. Document your implementation details, build outputs, test results, and command logs in `E:\AIF_Project\.agents\teamwork_preview_worker_m1_1\handoff.md`.
6. Send a message to your orchestrator when done.
