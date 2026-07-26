# Milestone 2 Analysis Report: Wire Unified VLM Pipeline

## Executive Summary
This report analyzes the integration requirements for Milestone 2 ("Wire Unified VLM Pipeline") of the Forge UI Unified VLM Refactor project. The goal of Milestone 2 is to wire the `TEXT_INPUT` event in `server.py` and `src/agent_loop.py` directly to the unified local VLM inference pipeline (`run_vlm_inference`), bypassing the legacy `plan_task()` / `MultiStagePlanner` architecture while preserving Intel Arc iGPU SYCL execution flags.

---

## Evidence Chain & Detailed Observations

### 1. VLM Inference Wrapper & SYCL Execution Flags
- **Primary Wrapper File**: `E:\AIF_Project\src\vlm_pipeline\tests\run_inference.py`
  - **Key Function**: `run_vlm_inference(image_path: str, prompt: str) -> dict` (Lines 12–77).
  - **Executable**: `LLAMA_CLI_PATH = r"E:\AIF_Project\src\vlm_pipeline\llama.cpp\build\bin\Release\llama-mtmd-cli.exe"` (Line 8).
  - **Model File**: `MODEL_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-Q4_K_M.gguf"` (Line 9).
  - **Vision Adapter**: `MMPROJ_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-mmproj-f16.gguf"` (Line 10).

- **SYCL Execution Environment & Command Settings**:
  - Environment variables configured prior to subprocess execution (Lines 25–29):
    ```python
    env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
    env["ZES_ENABLE_SYSMAN"] = "1"
    env["GGML_SYCL_DEBUG"] = "0"
    ```
  - Subprocess command configuration (Lines 31–41):
    ```python
    cmd = [
        LLAMA_CLI_PATH,
        "-m", MODEL_PATH,
        "--mmproj", MMPROJ_PATH,
        "--image", image_path,
        "-p", prompt,
        "-n", "512",
        "-c", "8192",
        "-b", "4096",
        "--temp", "0.1"
    ]
    ```

- **Supporting VLM Scripts**:
  - `E:\AIF_Project\src\vlm_pipeline\forge_agent.py`: Demonstrates the standalone pipeline: screenshot capture via `pyautogui.screenshot()` -> `run_vlm_inference()` -> `execute_action(action_plan)` via `src/vlm_pipeline/execution/executor.py`.
  - `E:\AIF_Project\src\vlm_pipeline\execution\executor.py`: Action executor for parsed JSON actions (`click`, `type`, `press`, `double_click`, `scroll`, `open_github`).
  - `E:\AIF_Project\src\vlm_pipeline\export\export_gguf.py`: Script managing `llama.cpp` SYCL release downloads (`llama-b10107-bin-win-sycl-x64.zip`).

---

### 2. Event Processing in `server.py` and `src/agent_loop.py`

#### A. `TEXT_INPUT` Reception (`server.py`)
- **Location**: `server.py`, WebSocket handler `ws_handler()` (Lines 679–697).
- **Execution Flow**:
  1. Frontend sends JSON message with `"command": "TEXT_INPUT"` and `"text": "... Prompt ..."`.
  2. Server extracts `text_cmd = payload.get("text")`.
  3. If state is not `SystemState.IDLE`, resets state to `IDLE`.
  4. Checks for attached image (`uploaded_image` context key).
  5. Calls `self.append_to_history("USER", display_text)`.
  6. Sets `self.fsm.current_context["voice_text"] = text_cmd`.
  7. Transitions state machine to `SystemState.PROCESSING_INTENT`.
  8. Calls `self.process_state()`.

#### B. Intent Processing & Routing (`server.py`)
- **Location**: `server.py`, `process_state()` (Lines 422–528).
- **Execution Flow**:
  1. When FSM state is `PROCESSING_INTENT`, spawns async task `_react_worker()`.
  2. `_react_worker()` retrieves `instruction = context.get("voice_text", "")`.
  3. Evaluates conversational phrases -> responds directly.
  4. Evaluates developer/flashcard macros -> routes to preset actions.
  5. Standard user requests (Lines 476–522):
     - Takes screenshot to `temp_screenshot.png` using `mss`.
     - Dynamically adds `src/vlm_pipeline` to `sys.path`.
     - Imports and calls `run_vlm_inference(screenshot_path, instruction)`.
     - Updates UI toast and executes action using `execute_action(plan)`.

#### C. Disconnect in `src/agent_loop.py`
- **Location**: `src/agent_loop.py` (Lines 1–261).
- **Observations**:
  - `server.py` line 36 imports `from src.agent_loop import execute_react_loop, plan_task, execute_task_plan`.
  - Line 3 of `src/agent_loop.py` imports `from src.planner import generate_plan, replan_failed_step, planner_instance`.
  - `plan_task()` in `src/agent_loop.py` (Lines 22–45) calls `planner_instance.generate_action_plan(instruction, ctx_summary)`.
  - Since Milestone 1 deletes `src/planner.py`, `src/agent_loop.py` will raise `ModuleNotFoundError` unless legacy imports and `plan_task()` calls are refactored to use the VLM inference wrapper.

---

### 3. Screenshot Snapping Analysis
- **Implementations Found**:
  - `mss` library: `with mss.mss() as sct: sct.shot(mon=-1, output=screenshot_path)` (Used in `server.py` line 480–482). Fastest multi-monitor capture.
  - `pyautogui.screenshot()`: `screenshot = pyautogui.screenshot(); screenshot.save(path)` (Used in `src/vlm_pipeline/forge_agent.py` line 21, `src/action_library.py` line 237). Standard across automation scripts.
- **Integration Strategy**:
  - Screenshot capture must occur immediately before calling `run_vlm_inference()`.
  - Path standard: `os.path.abspath("temp_screenshot.png")`.
  - The saved screenshot path is passed directly into `run_vlm_inference(screenshot_path, instruction)`.

---

## Required Refactoring Map

| Component | Target File | Line(s) | Action / Refactoring |
|---|---|---|---|
| Imports | `src/agent_loop.py` | 3 | Remove `from src.planner import ...`. Import `run_vlm_inference` from `src.vlm_pipeline.tests.run_inference` and screenshot module (`mss` or `pyautogui`). |
| Planner Bypass | `src/agent_loop.py` | 22–45 | Replace legacy `plan_task()` body with VLM pipeline invocation: capture screenshot -> call `run_vlm_inference(screenshot_path, instruction)` -> return single-step VLM action plan. |
| ReAct Loop | `src/agent_loop.py` | 239–247 | Update `execute_react_loop()` to trigger the unified VLM pipeline directly. |
| Event Handler | `server.py` | 36 | Update import statement to reference new/updated VLM pipeline functions in `src.agent_loop`. |
| Worker Routing | `server.py` | 476–522 | Clean up `_react_worker()` to call `src.agent_loop` VLM pipeline wrapper, maintaining UI feedback, SYCL environment flags, and action execution. |

---

## Conclusion
The unified VLM pipeline is fully supported by the existing `run_vlm_inference` function in `src/vlm_pipeline/tests/run_inference.py`. By refactoring `src/agent_loop.py` to remove legacy `src.planner` imports and wiring `plan_task()` / `execute_react_loop()` to `run_vlm_inference()`, `server.py` can route all `TEXT_INPUT` events cleanly through `src/agent_loop.py` with full SYCL acceleration.
