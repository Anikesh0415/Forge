## 2026-07-27T16:12:20Z
Your Identity: Worker 3 (Implementation Worker for Milestone 3)
Working Directory: E:\AIF_Project\.agents\teamwork_preview_worker_m3_1
Project Root: E:\AIF_Project
Scope Document: E:\AIF_Project\.agents\orchestrator\PROJECT.md
Explorer Analysis: E:\AIF_Project\.agents\teamwork_preview_explorer_m3_1\analysis.md
Explorer Handoff: E:\AIF_Project\.agents\teamwork_preview_explorer_m3_1\handoff.md

Objective:
Implement Milestone 3: Dynamic Plugin Ecosystem & Core Integration.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Detailed Tasks:
1. Implement `src/plugin_manager.py`:
   - Abstract Base Class `BaseForgePlugin`:
     - `plugin_name: str`
     - `plugin_version: str`
     - `initialize(config: dict) -> bool`
     - `execute_action(action_payload: dict) -> dict`
     - `filter_action(action_payload: dict) -> bool`
   - `PluginManager` class:
     - Scans `src/plugins/` directory at startup using Python `importlib` and `pkgutil`.
     - Dynamically registers and manages lifecycle (discovery, activation, deactivation) of any valid plugin implementing `BaseForgePlugin`.
     - `filter_action(action_payload: dict) -> bool`: passes action through active plugins; returns `False` if blocked.
     - `route_action(action_payload: dict) -> dict`: dispatches plugin actions to target plugin's `execute_action`.
2. Implement `DevModePlugin` (`src/plugins/dev_mode.py`):
   - Inherits from `BaseForgePlugin`.
   - Intercepts Terminal/IDE window handles (VS Code, Cursor, PowerShell, CMD) and executes direct shell commands / developer operations.
3. Implement `StudentModePlugin` (`src/plugins/student_mode.py`):
   - Inherits from `BaseForgePlugin`.
   - Enforces focus window coordinate bounds and filters prohibited applications/websites during study sessions.
4. Integrate into `src/agent_loop.py`:
   - Initialize `PluginManager` on backend boot/loop start.
   - Run `plugin_manager.filter_action()` in action execution pipeline to enforce plugin guardrails.
   - Run `plugin_manager.route_action()` to handle plugin execution payloads.
5. Verification:
   - Create unit tests in `tests/test_plugin_system.py` verifying auto-discovery of new `.py` files in `src/plugins/`, activation, filtering, and action routing for DevMode and StudentMode plugins.
   - Run pytest suite (`pytest tests/test_plugin_system.py`) to confirm all tests pass cleanly.
6. Document implementation details and test command outputs in `E:\AIF_Project\.agents\teamwork_preview_worker_m3_1\handoff.md`.
7. Send a message to your orchestrator when done.
