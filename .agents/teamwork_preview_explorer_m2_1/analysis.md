# Milestone 2 Investigation & Architecture Proposal: Teach Mode & Safety Boundary Logging Infrastructure

## Executive Summary
This document presents the detailed findings and recommended implementation strategy for Milestone 2 of the Forge AI OS project: **Teach Mode & Safety Boundary Logging Infrastructure**. 

Milestone 2 establishes two critical capabilities:
1. **Teach Mode / Interactive Override Handler**: Enables human-in-the-loop interactive corrections (via hotkey override or explicit point adjustment), capturing precise screen coordinates $(x, y)$, cropped target element screenshots, model predictions, pixel error delta, and full model context buffer.
2. **Safety Logger & Boundary Enforcement**: Enforces user-defined spatial restricted desktop zones (`config/safety_rules.json`) and action guardrails in `src/safety_logger.py`, logging boundary breaches to `dataset/safety_audit.jsonl` and production shadow records to `dataset/shadow_dataset.jsonl`.

---

## 1. Codebase Baseline & Observation Summary

### 1.1 `src/agent_loop.py`
- **Location**: `E:\AIF_Project\src\agent_loop.py` (232 lines)
- **Current Role**: Manages desktop screenshot capture (`capture_screenshot`), plan generation via VLM inference (`plan_task`), plan execution (`execute_task_plan`), loop detection (`ActionBuffer`), and top-level agent execution (`run_autonomous_agent`, `execute_react_loop`).
- **Observations & Gaps**:
  - Lines 127–139 contain a inline `is_safe_action` guardrail checking string blacklists (`del `, `format `, `rmdir`, `powershell -enc`, etc.).
  - **Gap 1**: No spatial desktop zone boundary checks exist in `agent_loop.py`.
  - **Gap 2**: No interactive override handler or Teach Mode hook exists to intercept execution, take human coordinate corrections $(x, y)$, crop element screenshots, or capture context buffer upon user intervention.
  - **Gap 3**: `agent_loop.py` does not interface with any shadow mode dataset logger or safety audit logger.

### 1.2 `src/logger.py` & `src/security.py`
- **`src/logger.py`**: `StructuredLogger` writes human-readable logs to `logs/agent_YYYYMMDD.log` and metrics to `logs/agent_metrics_YYYYMMDD.jsonl`.
- **`src/security.py`**: `SecurityManager` categorizes actions into `RiskLevel.SAFE`, `MODERATE`, `DESTRUCTIVE` and sanitizes secrets.
- **Observations & Gaps**:
  - Neither `logger.py` nor `security.py` handles spatial coordinate bounding box checks or JSONL shadow dataset logging.
  - `src/safety_logger.py` does **not** currently exist and must be created.

### 1.3 `src/shadow_mode.py` & `dataset/shadow_dataset.jsonl`
- **`src/shadow_mode.py`**: Standalone background listener using `pynput.mouse` and `mss` to log left clicks and VLM predictions.
- **`dataset/shadow_dataset.jsonl`**: Stores 160+ historical shadow records.
- **Observations & Gaps**:
  - Existing records in `shadow_dataset.jsonl` use legacy field names (`screen_size`, `ground_truth`, `ai_prediction`, `error_delta`) and **lack** the required `context_history` field and cropped target element screenshot paths.
  - `shadow_mode.py` writes directly to file without using a unified logger module.

### 1.4 Configuration & Audit Logs
- **`config/safety_rules.json`**: File does **not** exist yet.
- **`dataset/safety_audit.jsonl`**: File does **not** exist yet.

---

## 2. Detailed Technical Architecture & Requirements

### 2.1 Safety Logger API Contract (`src/safety_logger.py`)
Per `PROJECT.md` contract guidelines, `src/safety_logger.py` must provide the following standard API interface:

```python
class SafetyLogger:
    def check_boundary_violation(self, action_payload: dict) -> bool:
        """
        Checks whether action_payload violates restricted desktop zones (config/safety_rules.json),
        keyword blacklists, or restricted applications.
        If a violation is detected, automatically invokes log_safety_audit and returns True.
        """
        ...

    def log_shadow_record(self, record_payload: dict) -> None:
        """
        Appends a standardized Teach Mode / Shadow Mode production record to dataset/shadow_dataset.jsonl.
        """
        ...

    def log_safety_audit(self, breach_payload: dict) -> None:
        """
        Appends a security breach attempt record to dataset/safety_audit.jsonl.
        """
        ...
```

### 2.2 Boundary Enforcement Logic & `config/safety_rules.json` Schema
The boundary checker will evaluate three categories of safety constraints:
1. **Spatial Desktop Zones (`restricted_zones`)**: Bounding boxes defined by `x_min`, `y_min`, `x_max`, `y_max`. Any click/hover action targeting coordinates $(x, y)$ falling inside a restricted zone returns `True` (violation).
2. **Destructive Command Blacklists (`restricted_keywords`)**: Target text, command strings, or action types matching restricted patterns.
3. **Restricted Desktop Applications (`restricted_apps`)**: Target process names or window titles.

#### Recommended `config/safety_rules.json` Structure:
```json
{
  "restricted_zones": [
    {
      "name": "Taskbar System Tray",
      "x_min": 1700,
      "y_min": 1040,
      "x_max": 1920,
      "y_max": 1080
    },
    {
      "name": "Window Close Controls",
      "x_min": 1880,
      "y_min": 0,
      "x_max": 1920,
      "y_max": 40
    }
  ],
  "restricted_keywords": [
    "del ",
    "format ",
    "rmdir",
    "rd /s",
    "powershell -enc",
    "reg add",
    "net user",
    "drop table",
    "rm -rf"
  ],
  "restricted_apps": [
    "regedit.exe",
    "cmd.exe",
    "powershell.exe"
  ]
}
```

### 2.3 Teach Mode & Interactive Override Handler Architecture
Interactive corrections occur when the human user overrides a model prediction or adjusts click coordinates during execution.

#### Workflow Requirements:
1. **Coordinate Capture**: Extract precise $(x_{user}, y_{user})$ coordinates from manual click or hotkey override payload.
2. **Target Element Screenshot**:
   - Capture full screenshot and crop a bounding ROI centered at $(x_{user}, y_{user})$ (e.g. $200 \times 200$ pixels).
   - Save to `dataset/images/crop_<timestamp>.png`.
3. **Context Buffer Retrieval**: Extract `action_buffer.buffer` list and current instruction/prompt string from `agent_loop.py`.
4. **Error Delta Calculation**:
   $$\text{error\_delta\_px} = \sqrt{(x_{user} - x_{model})^2 + (y_{user} - y_{model})^2}$$
   (Set to `null` if model prediction did not contain point coordinates).
5. **Shadow Record Payload Standard Schema**:
   ```json
   {
     "timestamp": "2026-07-27T21:38:19Z",
     "screen_dim": {
       "width": 1920,
       "height": 1080
     },
     "user_action": {
       "type": "click",
       "x": 450,
       "y": 320,
       "target_crop_path": "E:\\AIF_Project\\dataset\\images\\crop_1785063602688.png",
       "full_image_path": "E:\\AIF_Project\\dataset\\images\\shadow_1785063602688.png"
     },
     "model_prediction": {
       "type": "click",
       "x": 480,
       "y": 310,
       "raw_output": "{\"x\": 480, \"y\": 310}"
     },
     "error_delta_px": 31.62,
     "context_history": [
       {"action": "open_browser", "target": "https://google.com"},
       {"action": "type_text", "target": "Forge AI OS"}
     ]
   }
   ```

### 2.4 Safety Audit Record Standard Schema (`dataset/safety_audit.jsonl`)
```json
{
  "timestamp": "2026-07-27T21:38:19Z",
  "violation_type": "RESTRICTED_ZONE_BREACH",
  "action_payload": {
    "action": "click",
    "x": 1800,
    "y": 1050,
    "target": "Taskbar System Tray"
  },
  "matched_rule": {
    "rule_type": "zone",
    "name": "Taskbar System Tray",
    "bounds": {"x_min": 1700, "y_min": 1040, "x_max": 1920, "y_max": 1080}
  },
  "blocked": true,
  "context": "Agent attempted click in restricted desktop zone"
}
```

---

## 3. Recommended Implementation Strategy for Implementer

### Step 1: Create Configuration File
- Create `config/safety_rules.json` with default desktop zones, keywords, and restricted applications.

### Step 2: Implement `src/safety_logger.py`
- Implement class `SafetyLogger` with thread-safe file handling for JSONL files (`shadow_dataset.jsonl` and `safety_audit.jsonl`).
- Implement `check_boundary_violation(action_payload)` checking spatial coordinates, keywords, and app names against `config/safety_rules.json`.
- Implement `log_shadow_record(record_payload)` validating payload keys (`timestamp`, `screen_dim`, `user_action`, `model_prediction`, `error_delta_px`, `context_history`).
- Implement `log_safety_audit(breach_payload)` appending breach details to `dataset/safety_audit.jsonl`.

### Step 3: Enhance `src/agent_loop.py`
- Integrate `SafetyLogger` singleton.
- Update `execute_task_plan`: Replace local `is_safe_action` check with `safety_logger.check_boundary_violation(step)`.
- Implement `handle_interactive_override` and element screenshot cropping logic:
  - Add helper function `crop_target_element(image_path, x, y, width=200, height=200) -> str`.
  - Construct standardized `record_payload` and pass to `safety_logger.log_shadow_record`.

### Step 4: Refactor `src/shadow_mode.py`
- Update `shadow_mode.py` to use `SafetyLogger.log_shadow_record()` for unified logging and schema consistency.

### Step 5: Unit & Integration Testing
- Create `tests/test_safety_logger.py` verifying:
  1. Boundary violation detection for spatial coordinates inside/outside restricted zones.
  2. Keyword and restricted app breach logging in `dataset/safety_audit.jsonl`.
  3. Teach Mode override record logging in `dataset/shadow_dataset.jsonl` matching standard schema.
  4. Element screenshot cropping around correction coordinates $(x, y)$.

---

## 4. Proposed Code Modifications (Patches / Snippets)

### Proposed `src/safety_logger.py`
```python
import os
import json
import math
import time
from datetime import datetime
import threading

DEFAULT_RULES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "safety_rules.json"))
DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
SHADOW_DATASET_PATH = os.path.join(DATASET_DIR, "shadow_dataset.jsonl")
SAFETY_AUDIT_PATH = os.path.join(DATASET_DIR, "safety_audit.jsonl")

class SafetyLogger:
    def __init__(self, rules_path: str = DEFAULT_RULES_PATH):
        self.rules_path = rules_path
        self._lock = threading.Lock()
        self.rules = self._load_rules()
        os.makedirs(DATASET_DIR, exist_ok=True)

    def _load_rules(self) -> dict:
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[SafetyLogger] Warning: failed to load rules ({e})")
        return {"restricted_zones": [], "restricted_keywords": [], "restricted_apps": []}

    def check_boundary_violation(self, action_payload: dict) -> bool:
        action_type = str(action_payload.get("action", "")).lower()
        target = str(action_payload.get("target") or action_payload.get("text") or "")
        
        # 1. Keyword check
        for kw in self.rules.get("restricted_keywords", []):
            if kw.lower() in target.lower() or kw.lower() in action_type:
                self.log_safety_audit({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "violation_type": "KEYWORD_BREACH",
                    "action_payload": action_payload,
                    "matched_rule": {"rule_type": "keyword", "keyword": kw},
                    "blocked": True
                })
                return True

        # 2. Spatial zone check
        x = action_payload.get("x")
        y = action_payload.get("y")
        if x is not None and y is not None:
            try:
                x_val, y_val = float(x), float(y)
                for zone in self.rules.get("restricted_zones", []):
                    if zone["x_min"] <= x_val <= zone["x_max"] and zone["y_min"] <= y_val <= zone["y_max"]:
                        self.log_safety_audit({
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "violation_type": "RESTRICTED_ZONE_BREACH",
                            "action_payload": action_payload,
                            "matched_rule": {"rule_type": "zone", "name": zone.get("name"), "bounds": zone},
                            "blocked": True
                        })
                        return True
            except (ValueError, TypeError):
                pass

        return False

    def log_shadow_record(self, record_payload: dict) -> None:
        with self._lock:
            with open(SHADOW_DATASET_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record_payload) + "\n")

    def log_safety_audit(self, breach_payload: dict) -> None:
        with self._lock:
            with open(SAFETY_AUDIT_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(breach_payload) + "\n")

safety_logger = SafetyLogger()
```

---

## 5. Verification Plan & Test Matrix
To independently verify Milestone 2 implementation:
1. Run `pytest tests/test_safety_logger.py` to test boundary checking, audit logging, and shadow record appending.
2. Verify `dataset/shadow_dataset.jsonl` entries contain required schema keys (`timestamp`, `screen_dim`, `user_action`, `model_prediction`, `error_delta_px`, `context_history`).
3. Verify `dataset/safety_audit.jsonl` contains audit records when attempting actions targeting restricted zones (e.g. $(1800, 1050)$) or restricted keywords (e.g. `del system32`).
