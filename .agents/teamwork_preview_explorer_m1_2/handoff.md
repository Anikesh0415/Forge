# Handoff Report: Milestone 2 — Wire Unified VLM Pipeline

## 1. Observation
1. **VLM Inference Wrapper**: `E:\AIF_Project\src\vlm_pipeline\tests\run_inference.py` lines 12–77 defines `run_vlm_inference(image_path: str, prompt: str) -> dict`.
   - Executable path (line 8): `LLAMA_CLI_PATH = r"E:\AIF_Project\src\vlm_pipeline\llama.cpp\build\bin\Release\llama-mtmd-cli.exe"`.
   - Model path (line 9): `MODEL_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-Q4_K_M.gguf"`.
   - Multimodal projector path (line 10): `MMPROJ_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-mmproj-f16.gguf"`.
2. **SYCL Environment Settings**:
   - Environment variables set in `run_vlm_inference()` (lines 25–29):
     ```python
     env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
     env["ZES_ENABLE_SYSMAN"] = "1"
     env["GGML_SYCL_DEBUG"] = "0"
     ```
   - CLI flags passed to `llama-mtmd-cli.exe` (lines 31–41): `-m`, `--mmproj`, `--image`, `-p`, `-n 512`, `-c 8192`, `-b 4096`, `--temp 0.1`.
3. **`TEXT_INPUT` Handler in `server.py`**:
   - In `server.py` lines 679–697, WebSocket command `"TEXT_INPUT"` receives user prompt, updates `voice_text` context variable, appends message to user history via `append_to_history("USER", display_text)`, and transitions state machine to `SystemState.PROCESSING_INTENT`.
   - In `server.py` lines 422–528 (`process_state()`), `_react_worker()` runs inline screenshot + `run_vlm_inference(screenshot_path, instruction)` + `execute_action(plan)`.
4. **Legacy Dependencies in `src/agent_loop.py`**:
   - In `src/agent_loop.py` line 3: `from src.planner import generate_plan, replan_failed_step, planner_instance`.
   - `plan_task()` in `src/agent_loop.py` lines 22–45 invokes `planner_instance.generate_action_plan(instruction, ctx_summary)`.
   - When `src/planner.py` is removed in Milestone 1, `src/agent_loop.py` will fail with `ModuleNotFoundError` if `src.planner` imports are not removed.

---

## 2. Logic Chain
1. **Observation 1 & 2** establish that `run_vlm_inference(image_path, prompt)` in `src/vlm_pipeline/tests/run_inference.py` is the complete, self-contained VLM wrapper that enforces SYCL flags on Intel Arc iGPU and invokes `llama-mtmd-cli.exe` with the GGUF model and mmproj adapter.
2. **Observation 3** establishes that `server.py` receives user commands via `"TEXT_INPUT"`, updates `voice_text`, transitions to `PROCESSING_INTENT`, and spawns `_react_worker()`.
3. **Observation 4** establishes that `src/agent_loop.py` currently relies on legacy `src/planner.py`. Once Milestone 1 deletes `src/planner.py`, `src/agent_loop.py` must be updated to remove `src.planner` imports and replace `plan_task()` with calls to `run_vlm_inference()`.
4. **Synthesis**: Refactoring `src/agent_loop.py` to import `run_vlm_inference()` and encapsulate screenshot capture + VLM inference allows `server.py` to route `TEXT_INPUT` cleanly through `agent_loop.py`, bypassing `plan_task()` and preserving SYCL flags.

---

## 3. Caveats
- **Physical Hardware Execution**: In non-GUI / headless test environments where Intel Arc iGPU or `llama-mtmd-cli.exe` binaries are absent, `run_vlm_inference` raises `FileNotFoundError`. Mocking or dry-running the subprocess call may be necessary during unit tests.
- **Screenshot Permissions**: Multi-monitor setups require proper `mss` monitor index selection (`mon=-1` captures all screens or primary monitor).

---

## 4. Conclusion
Milestone 2 implementation requires two key file modifications:
1. `src/agent_loop.py`: Remove `from src.planner import ...`, import `run_vlm_inference`, and refactor `plan_task()` and `execute_react_loop()` to capture desktop screenshots and invoke `run_vlm_inference(screenshot_path, prompt)`.
2. `server.py`: Route `TEXT_INPUT` event workers through `src/agent_loop.py`'s updated VLM pipeline functions, ensuring UI countdown toast display and execution handling are preserved alongside SYCL environment flags.

---

## 5. Verification Method
1. **File Inspection**:
   - Inspect `src/agent_loop.py` to ensure zero imports from `src.planner`.
   - Inspect `src/agent_loop.py` and `server.py` to ensure `run_vlm_inference` is called on `TEXT_INPUT` events.
2. **Import Verification**:
   - Run `python -c "import src.agent_loop"` to confirm no `ModuleNotFoundError` occurs after `src/planner.py` deletion.
3. **SYCL Flag Verification**:
   - Run `python -c "from src.vlm_pipeline.tests.run_inference import run_vlm_inference; print('VLM module loaded')"` to verify import paths and SYCL environment flag setup.
