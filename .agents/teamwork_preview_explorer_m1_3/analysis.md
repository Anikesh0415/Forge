# Milestone 3 Detailed Analysis Report: Auto-Execution & Killswitch

**Author**: Explorer 3  
**Date**: 2026-07-25  
**Target Milestone**: Milestone 3 (Auto-Execution & Killswitch)  
**Project**: Forge UI Unified VLM Refactor  

---

## Executive Summary

This report delivers a complete architectural analysis and design specification for Milestone 3 (Auto-Execution & Killswitch). It examines how VLM JSON outputs are parsed and passed to PyAutoGUI execution backends, details the removal of manual confirmation prompts in favor of an automated pipeline, specifies the 1.5-second UI toast grace delay countdown, and defines the global ESC keyboard listener killswitch mechanism that immediately halts `pyautogui` action execution and safely recovers system state.

---

## 1. Architecture of VLM JSON Action Parsing & PyAutoGUI Execution

### 1.1 VLM Inference Pipeline (`src/vlm_pipeline/tests/run_inference.py`)
The VLM inference pipeline executes `llama-mtmd-cli.exe` with SYCL hardware acceleration flags for Intel Arc iGPUs:
- **Environment Variables**:
  ```python
  env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
  env["ZES_ENABLE_SYSMAN"] = "1"
  env["GGML_SYCL_DEBUG"] = "0"
  ```
- **Execution Command**:
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
- **Parsing Logic**:
  `run_vlm_inference()` captures stdout, extracts JSON structure using regex (`re.search(r"(\{.*?\})", output, re.DOTALL)`), and sanitizes unquoted JSON keys and string values:
  ```python
  clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
  clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
  action_plan = json.loads(clean_json)
  ```

### 1.2 Action Dispatch & Execution (`src/vlm_pipeline/execution/executor.py`)
The parsed dictionary is passed directly to `execute_action(action_plan: dict)`:
- **Action Schema**:
  - `click`: `{"action": "click", "x": 100, "y": 200, "button": "left"}` -> `pyautogui.click(x=int(x), y=int(y), button=button)`
  - `type`: `{"action": "type", "text": "hello"}` -> `pyautogui.write(text, interval=0.05)`
  - `press`: `{"action": "press", "key": "enter"}` -> `pyautogui.press(key)`
  - `double_click`: `{"action": "double_click", "x": 100, "y": 200}` -> `pyautogui.doubleClick(x=int(x), y=int(y))`
  - `scroll`: `{"action": "scroll", "clicks": -5}` -> `pyautogui.scroll(int(clicks))`
  - `open_github`: `{"action": "open_github"}` -> `pyautogui.hotkey('win', 'r')`, types `https://github.com`, presses `enter`.

### 1.3 Execution Manager Integration (`src/execution_manager.py` & `src/executors/pyautogui_executor.py`)
For full multi-backend fallback and rich action types (`open_app`, `navigate_browser`, `search_web`, `click_element`, `key_shortcut`, `speak`, `send_whatsapp`), action objects can be routed through `ExecutionManager.execute_step()`, which delegates to `PyAutoGUIExecutor` and standard action library routines in `src/action_library.py`.

---

## 2. Automatic Execution Workflow (Bypassing Manual Confirmation)

### 2.1 Legacy Confirmation vs. Auto-Execution Architecture
- **Legacy Flow (`server.py`)**:
  1. User prompt -> Planner generates action plan.
  2. Server transitions to `SystemState.AWAITING_CONFIRMATION`.
  3. Server waits for explicit user action: WS event `CONFIRM_PLAN` or voice command ("confirm", "yes").
  4. Only on confirmation does server transition to `SystemState.EXECUTING` and call `execute_task_plan()`.

- **Auto-Execution Flow (Milestone 3 Specification)**:
  1. User sends `TEXT_INPUT` event to `server.py`.
  2. Server captures desktop screenshot (`temp_screenshot.png`) via `mss`.
  3. Server invokes `run_vlm_inference(screenshot_path, instruction)`.
  4. VLM returns parsed single-step or multi-step JSON action plan.
  5. System **completely bypasses** `SystemState.AWAITING_CONFIRMATION`.
  6. System triggers 1.5-second Toast Grace Period (`update_ui("Executing: [Action] in 1.5s... [Press ESC to Cancel]")`).
  7. During the 1.5s grace period, the abort listener monitors for the ESC key.
  8. If not aborted, system transitions to `SystemState.EXECUTING` and executes `execute_action(plan)`.
  9. System transitions back to `SystemState.IDLE`.

---

## 3. 1.5-Second UI Toast Delay Implementation

### 3.1 Backend Countdown & Cancellation Loop (`server.py`)
To allow user cancellation via ESC during the 1.5s toast window without blocking the asyncio event loop:
```python
action_desc = plan.get('action', '').replace('_', ' ').title()
target_desc = plan.get('target', plan.get('name', plan.get('text', plan.get('url', ''))))

# Broadcast Toast to UI and HUD
update_ui(f"Executing: {action_desc} {target_desc} in 1.5s... [Press ESC to Cancel]")
event_bus.publish("ui_status", f"Executing: {action_desc} in 1.5s [ESC to Cancel]")

# Non-blocking 1.5s countdown (checking abort flag every 100ms)
self.memory_mgr.abort_flag = False
aborted = False
for _ in range(15):
    if getattr(self.memory_mgr, 'abort_flag', False):
        aborted = True
        break
    await asyncio.sleep(0.1)

if aborted:
    update_ui("🛑 Execution cancelled by user (ESC pressed)!")
    self.fsm.transition(SystemState.IDLE)
    return
```

### 3.2 Frontend UI Toast Rendering (`ui/app.js` & `src/hud.py`)
- **Web UI (`ui/app.js`)**: WebSocket messages containing `reply_text` and `action_text` update the status panel (`actionText.textContent`) and append a SYSTEM toast item to the chat log.
- **Desktop HUD (`src/hud.py`)**: Listens on `event_bus` topic `ui_status`, updating `lbl_action` label in real-time ("Status: Executing: Click in 1.5s...").

---

## 4. Global ESC Key Listener & PyAutoGUI Killswitch

### 4.1 Global Listener Mechanisms (`keyboard` / `pynput`)
To ensure ESC key events are intercepted system-wide regardless of active application focus:
1. **`keyboard` Library (Current Implementation in `server.py`)**:
   Uses Win32 `SetWindowsHookEx` low-level keyboard hook:
   ```python
   import keyboard
   import pyautogui

   def _global_killswitch_handler():
       print("\n[KILLSWITCH] ESC pressed! Halting PyAutoGUI instantly...")
       # 1. Trigger PyAutoGUI Failsafe immediately
       pyautogui.FAILSAFE = True
       try:
           pyautogui.moveTo(0, 0, duration=0)
       except Exception:
           pass
       # 2. Set abort flag on MemoryManager
       if hasattr(server_instance, 'memory_mgr'):
           server_instance.memory_mgr.abort_flag = True

   keyboard.add_hotkey('esc', _global_killswitch_handler)
   keyboard.add_hotkey('ctrl+e', _global_killswitch_handler)
   ```
2. **Alternative `pynput` Thread-based Listener**:
   ```python
   from pynput import keyboard

   def on_press(key):
       if key == keyboard.Key.esc:
           _global_killswitch_handler()

   listener = keyboard.Listener(on_press=on_press)
   listener.daemon = True
   listener.start()
   ```

### 4.2 PyAutoGUI Safety Failsafe & Exception Handling
`pyautogui.FAILSAFE = True` automatically raises `pyautogui.FailSafeException` whenever the cursor reaches coordinates `(0, 0)`. Moving the mouse cursor to `(0, 0)` inside the killswitch handler forces any ongoing or in-flight PyAutoGUI call (`click`, `write`, `dragTo`) to immediately throw an unhandled `FailSafeException`, terminating the GUI automation action instantaneously.

### 4.3 Safe State Recovery
When the killswitch fires:
1. `memory_mgr.abort_flag` is set to `True`.
2. The countdown loop or `execute_action()` catches `FailSafeException` or checks `abort_flag`.
3. `server.py` transitions state to `SystemState.IDLE`.
4. Audit log entry is written: `[KILLSWITCH] Task execution aborted by ESC hotkey.`
5. UI displays `"🛑 TASK ABORTED BY KILL-SWITCH!"`.

---

## 5. Summary of Proposed Implementation Changes

| File | Location | Description of Change |
|------|----------|-----------------------|
| `server.py` | Top-level initialization | Ensure `keyboard.add_hotkey('esc', handler)` updates `memory_mgr.abort_flag = True` and moves mouse to `(0,0)`. |
| `server.py` | `_react_worker()` | Replace `AWAITING_CONFIRMATION` flow with direct VLM inference, 1.5s 100ms interval countdown toast, abort flag check, and `execute_action()`. |
| `src/vlm_pipeline/execution/executor.py` | `execute_action()` | Add `abort_flag` checks and `try...except pyautogui.FailSafeException` wrapper returning `(False, "Aborted by killswitch")`. |
| `ui/app.js` | WS message listener | Render status countdown toasts in status bar and chat log cleanly without duplicate entries. |

---

## 6. Verification Criteria
1. **Auto-Execution**: Send user prompt via Web UI (`TEXT_INPUT`). Verify VLM inference runs and directly transitions to execution without requiring manual button click.
2. **1.5s Toast Delay**: Observe UI message displaying `"Executing: [Action] in 1.5s... [Press ESC to Cancel]"` for exactly 1.5 seconds prior to action execution.
3. **ESC Killswitch**: Press `ESC` during the 1.5s toast window or during action execution. Verify action is aborted immediately, mouse failsafe triggers, state resets to `IDLE`, and `"🛑 TASK ABORTED BY KILL-SWITCH!"` is displayed.
