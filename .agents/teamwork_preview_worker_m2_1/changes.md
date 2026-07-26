# Changes Summary — Milestone 2: Wire Unified VLM Pipeline

## 1. `src/agent_loop.py`
- **Imports**: Imported `run_vlm_inference` from `src.vlm_pipeline.tests.run_inference`.
- **Screenshot Snapping**: Added `capture_screenshot()` helper using `mss` with `pyautogui` / `PIL` fallbacks.
- **`plan_task()` Refactoring**: Updated signature and implementation to snap a desktop screenshot to `temp_screenshot.png`, invoke `run_vlm_inference(screenshot_path, instruction)`, and return the parsed action plan list. Preserves all SYCL execution flags (`SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1`, `ZES_ENABLE_SYSMAN=1`, `GGML_SYCL_DEBUG=0`).
- **`execute_task_plan()` Refactoring**: Enhanced step execution to handle VLM action plans (`click`, `type`, `press`, `double_click`, `scroll`, `open_github`) with fallback to `execute_action()` from `src.vlm_pipeline.execution.executor`.
- **`execute_react_loop()`**: Updated to trigger `plan_task()` and `execute_task_plan()`.

## 2. `server.py`
- **Imports**: Updated import from `src.agent_loop` to include `plan_task`.
- **`_react_worker()` Routing**: Refactored `TEXT_INPUT` handling in `_react_worker()` to call `plan_task(instruction, update_ui)` directly, routing all text input requests through the unified VLM pipeline in `src/agent_loop.py`. Preserved FSM state transitions (`PROCESSING_INTENT` -> `EXECUTING` -> `IDLE`) and 1.5s countdown toast feedback.

## 3. `tests/test_vlm_pipeline.py`
- Added comprehensive unit tests covering:
  - `src/agent_loop.py` imports and function exports.
  - SYCL environment flag configuration inside `run_vlm_inference`.
  - Desktop screenshot capture functionality.
  - VLM inference invocation and action plan parsing in `plan_task()`.
  - Step execution in `execute_task_plan()`.
  - End-to-end ReAct loop wiring in `execute_react_loop()`.
  - `server.py` integration and import verification.

## Verification Log Output
```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\AIF_Project
plugins: anyio-4.13.0, langsmith-0.8.16, zarr-3.2.1
collected 13 items

tests\test_architecture.py .                                             [  7%]
tests\test_moondream.py .                                                [ 15%]
tests\test_moondream_point.py .                                          [ 23%]
tests\test_ollama.py .                                                   [ 30%]
tests\test_stress.py .                                                   [ 38%]
tests\test_ui_dump.py .                                                  [ 46%]
tests\test_vlm_pipeline.py .......                                       [100%]

============================== warnings summary ===============================
tests/test_stress.py::test_stress
  E:\AIF_Project\tests\test_stress.py:31: RuntimeWarning: coroutine 'LocalLLMCore.process_intent' was never awaited
    macro_plan = macro_orchestrator.analyze_instruction(prompt)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_vlm_pipeline.py::test_server_imports_vlm_pipeline
  C:\Users\Anikesh\AppData\Local\Programs\Python\Python314\Lib\site-packages\chromadb\telemetry\opentelemetry\__init__.py:128: DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated and slated for removal in Python 3.16; use inspect.iscoroutinefunction() instead
    if asyncio.iscoroutinefunction(f):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 13 passed, 2 warnings in 11.70s =======================
```
