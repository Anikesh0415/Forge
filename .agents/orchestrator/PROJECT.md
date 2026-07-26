# Project: Forge UI Unified VLM Refactor

## Architecture
Replace legacy `MultiStagePlanner` and multi-model backend (`ollama` + vision deps) in Forge UI (`server.py`, `src/planner.py`, `src/agent_loop.py`) with a unified VLM inference pipeline. The architecture consists of:
1. Unified VLM inference wrapper invoked on `TEXT_INPUT` event (capturing screenshot + prompt, using SYCL execution flags).
2. Direct auto-execution loop executing parsed VLM JSON actions without manual "Confirm" step.
3. Safety Toast Delay (1.5s UI countdown) + Global ESC Key Listener to cancel execution via pyautogui halt.
4. Clean removal of legacy planner (`src/planner.py`), `ollama`, vision dependencies from `requirements.txt`, and legacy server endpoints.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Legacy Dependencies Cleanup | Delete `src/planner.py`, remove `ollama`/vision dependencies from `requirements.txt`, strip legacy routes/state from `server.py` | none | DONE |
| 2 | Wire Unified VLM Pipeline | Modify `server.py` and `src/agent_loop.py` to trigger VLM inference wrapper on `TEXT_INPUT` with screenshot + prompt, preserving SYCL flags | M1 | IN_PROGRESS |
| 3 | Auto-Execution & Killswitch | Auto-pass valid VLM JSON output to execution script, implement 1.5s UI toast delay, and add global ESC key listener for pyautogui halt | M2 | IN_PROGRESS |
| 4 | Verification & Git Operations | Run build/test suite, verify all acceptance criteria, stage, commit, and push to main branch | M3 | PLANNED |

## Interface Contracts
### `server.py` ↔ `src/agent_loop.py`
- Event `TEXT_INPUT`: Triggers screenshot capture, invokes VLM inference wrapper with screenshot path + user instruction.
- VLM Response: JSON action payload passed directly to auto-execution handler.
- SYCL Flags: Required runtime environment flags passed down to VLM subprocess/wrapper.

### Execution Handler ↔ Killswitch
- Toast Delay: 1.5 second UI notification banner prior to action execution.
- ESC Listener: Active Python keyboard hook/listener that sets abort flag and halts pyautogui execution immediately if ESC is pressed during toast window or execution.

## Code Layout
- `server.py` — Backend API routes and event handlers.
- `src/agent_loop.py` — Core agent event loop and VLM inference handler.
- `src/planner.py` — Legacy planner (deleted).
- `requirements.txt` — Project Python dependencies.
