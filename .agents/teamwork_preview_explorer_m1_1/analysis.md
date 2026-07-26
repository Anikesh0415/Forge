# Milestone 1: Legacy Dependencies & Planner Cleanup Analysis

## Executive Summary
This analysis report provides a comprehensive codebase mapping and dependency audit for **Milestone 1: Legacy Dependencies Cleanup** of the Forge UI Unified VLM Refactor project. The investigation examined `src/planner.py`, repository-wide references, `requirements.txt`, and `server.py` to prepare actionable targets for clean removal of the legacy `MultiStagePlanner`, `ollama` integrations, and legacy vision dependencies.

---

## 1. Symbol & Structure Mapping of `src/planner.py`

### File Path
`E:\AIF_Project\src\planner.py` (725 lines, ~36.8 KB)

### System Prompt & Global Constants
- `PLANNER_SYSTEM_PROMPT` (Lines 9–53): Multi-stage planning system prompt defining ARIA JSON action structures and universal workflow patterns.
- `planner_instance` (Line 702): Global singleton instance of `MultiStagePlanner`.

### Class: `MultiStagePlanner`
- `__init__(self)` (Lines 62–80): Initializes `LocalLLMCore`, loads organoid bio-engine weights from `config.json` if configured.
- `decompose_intent(self, instruction: str, context_summary: str = "") -> dict` (Lines 81–145): Stage 1 intent decomposition into sub-goals and required apps. Includes vague intent safety guardrails.
- `_extract_whatsapp_plan(self, clean_inst: str) -> list` (Lines 148–206): Rule-based fast-path router for WhatsApp messaging actions.
- `_extract_ai_whatsapp_plan(self, clean_inst: str) -> list` (Lines 208–244): Macro generator for AI-to-WhatsApp workflows (Gemini prompt -> clipboard -> WhatsApp).
- `_extract_ai_notepad_plan(self, clean_inst: str) -> list` (Lines 246–283): Macro generator for AI-to-Notepad workflows.
- `generate_action_plan(self, instruction: str, context_summary: str = "") -> list` (Lines 285–624): Stage 2 action plan generation combining fast-path routers, double-action synthesizers, and `LocalLLMCore` intent processing.
- `replan_failed_step(self, failed_step: dict, error_reason: str, context_summary: str = "", ui_tree_snapshot: str = "") -> list` (Lines 626–669): Stage 4 active replanning engine triggered on execution or visual verification failures.
- `_clean_and_extract(self, raw_data) -> list` (Lines 671–699): Helper sanitizing LLM output dicts/JSON strings into structured action lists.

### Top-Level Backward-Compatibility Functions
- `generate_plan(instruction: str, context_summary: str = "") -> list` (Lines 705–707): Wraps `planner_instance.generate_action_plan`.
- `replan_failed_step(failed_step: dict, error_reason: str, context_summary: str = "", ui_tree_snapshot: str = "") -> list` (Lines 710–719): Wraps `planner_instance.replan_failed_step`.

### Module Imports inside `src/planner.py`
- Standard/External: `json`, `re`, `urllib.parse`
- Internal: `from src.llm_core import LocalLLMCore`, `from src.logger import logger`, `from src.config import BROWSER_APP_MAP`, `from src.utils.skill_retriever import get_relevant_examples`
- Lazy/Dynamic Imports:
  - `from src.action_library import action_registry`
  - `from src.vision import ask_moondream`
  - `from src.utils.json_parser import parse_json_from_text`

---

## 2. Repository-Wide References to `planner.py` & Planning Symbols

A full repository search identified references to `planner.py`, `MultiStagePlanner`, `planner_instance`, `generate_plan`, and `replan_failed_step` across the following files:

### Source Files
1. **`src/agent_loop.py`**:
   - Line 3: `from src.planner import generate_plan, replan_failed_step, planner_instance`
   - Line 35: `plan = await planner_instance.generate_action_plan(instruction, ctx_summary)` inside `plan_task()`
   - Line 152: `recovery_plan = replan_failed_step(step, error_reason, ctx_summary, ui_tree_snapshot)` inside `execute_task_plan()`
2. **`server.py`**:
   - Line 36: `from src.agent_loop import execute_react_loop, plan_task, execute_task_plan`
   - (`server.py` calls `plan_task` which delegates directly to `planner_instance`).

### Test Files
1. **`tests/test_architecture.py`**:
   - Line 14: `from src.planner import MultiStagePlanner`
   - Line 42: `planner = MultiStagePlanner()`
   - Line 44–45: `decomp = asyncio.run(planner.decompose_intent(...))`
2. **`tests/test_stress.py`**:
   - Line 3: `from src.planner import planner_instance`
   - Lines 36, 42, 48: `planner_instance.generate_action_plan(...)`

---

## 3. Dependency Audit (`requirements.txt`)

### Current `requirements.txt` Inventory (20 lines)
```
1: fastapi
2: uvicorn
3: websockets
4: PyAutoGUI
5: pywin32
6: pytesseract
7: pyperclip
8: pillow
9: opencv-python
10: mediapipe
11: faster-whisper
12: sounddevice
13: numpy
14: requests
15: httpx
16: pyttsx3
17: youtube-transcript-api
18: chromadb
19: customtkinter
```

### Targets for Removal in Milestone 1
1. **`pytesseract`** (Line 6): Legacy Tesseract OCR library. Used in legacy OCR locating (`src/vision.py` line 82, `src/executors/pyautogui_executor.py` line 140).
2. **`opencv-python`** (Line 9): OpenCV image processing library. Used in legacy camera capture worker in `server.py` line 5 and `src/cv_module.py` line 1.
3. **`mediapipe`** (Line 10): MediaPipe hand gesture tracking framework. Used in `src/cv_module.py` line 2 and `server.py` line 248.

### Status of `ollama` Dependency
- `ollama` is **not** installed as a PyPI Python package in `requirements.txt` (the project interfaced with Ollama via raw HTTP REST endpoints `http://127.0.0.1:11434/api/generate` using `requests` and `httpx`).
- However, legacy `ollama` references exist in system configuration files (`src/config.py` lines 5–6, 21), LLM core (`src/llm_core.py` lines 20–21, 51, 118, 193), startup scripts (`boot.py` lines 13, 15; `Start_FORGE_App.bat` lines 4–12), `.env.example`, and `server.py` line 397 (`_run_meeting`).

---

## 4. Legacy Backend Examination (`server.py`)

### Legacy Imports in `server.py`
- Line 5: `import cv2` (OpenCV dependency for legacy camera worker)
- Line 32: `from src.cv_module import HandTracker` (MediaPipe gesture tracker)
- Line 36: `from src.agent_loop import execute_react_loop, plan_task, execute_task_plan` (`plan_task` uses legacy planner)

### Legacy API Endpoints, WebSocket Commands & State Logic
1. **`_run_meeting(self)` (Lines 389–412)**:
   - Direct HTTP POST request to Ollama endpoint `http://localhost:11434/api/generate` with model `qwen2.5:1.5b` to summarize transcriptions.
2. **`TOGGLE_MEETING` WS Command (Lines 588–595)**:
   - Starts the `_run_meeting` background thread calling Ollama.
3. **`CONFIRM_PLAN` & `REJECT_PLAN` WS Commands (Lines 616–621)** and **`confirm_plan()` / `reject_plan()` methods (Lines 139–164, 193–198)**:
   - Legacy two-stage manual confirmation workflow (`AWAITING_CONFIRMATION` -> `EXECUTING` / `IDLE`). Replaced in Milestone 2/3 by the auto-execution pipeline.
4. **`_camera_worker(self)` (Lines 233–388)** & **`self.tracker`**:
   - Background OpenCV thread capturing webcam frames for MediaPipe gesture tracking, peace sign vision triggers, and dwell clicking.
5. **`SET_MODE` WS Command (Lines 596–615)**:
   - Invokes `self.exec_mgr.headless_executor.llm_core.swap_model(mode)` for multi-model switching.
6. **Voice Confirmation handling in `_stt_worker()` (Lines 220–230)**:
   - Voice listener branch for `SystemState.AWAITING_CONFIRMATION` listening for "yes", "confirm", "proceed", "no", "cancel", "reject".

### FSM State & Context Cleanups Needed
- `SystemState.AWAITING_CONFIRMATION` (in `src/fsm_module.py` and `server.py`)
- `self.fsm.current_context["pending_plan"]`
- `self.is_tracking_mode` & camera thread startup (Lines 67, 86–87)

---

## 5. Recommended Concrete Action Plan for Milestone 1 Implementer

1. **Delete File**:
   - Remove `src/planner.py`.
2. **Update `requirements.txt`**:
   - Delete `pytesseract`, `opencv-python`, and `mediapipe`.
3. **Refactor `src/agent_loop.py`**:
   - Remove imports from `src.planner`.
   - Remove `plan_task()` or replace with direct VLM pipeline entry point.
   - Clean up `replan_failed_step` call in `execute_task_plan()`.
4. **Clean up `server.py`**:
   - Remove `import cv2`, `from src.cv_module import HandTracker`, and legacy planner imports.
   - Strip `_run_meeting` method and `TOGGLE_MEETING` WS command.
   - Remove `_camera_worker` thread and `HandTracker` initialization.
   - Strip legacy manual confirmation handlers (`confirm_plan`, `reject_plan`, `CONFIRM_PLAN`, `REJECT_PLAN`) and `SystemState.AWAITING_CONFIRMATION` state logic.
5. **Update Test Suite**:
   - Remove/update legacy planner import and tests in `tests/test_architecture.py` and `tests/test_stress.py`.
