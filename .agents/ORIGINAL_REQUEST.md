# Original User Request

## Initial Request — 2026-07-27T16:07:16Z

<USER_REQUEST>
Teamwork Project Prompt
Status: Ready for launch
Goal: Implement production-grade consumer features for Forge AI OS (No mocks, stubs, or dummy implementations allowed)
Working directory: E:\AIF_Project
Integrity mode: production

Requirements

R1. Cross-Platform One-Click Installer & Production Bundler
Develop a production PyInstaller build specification (`forge_builder.py` and `forge.spec`) to package the Forge Python backend (`server.py`) into a standalone executable.
- The entry script must check the local `models/` directory on launch for `Qwen2-VL-2B-Instruct-Q4_K_M.gguf`.
- If missing, it must streamingly download the official model weights directly from Hugging Face (`bartowski/Qwen2-VL-2B-Instruct-GGUF`) with a console/GUI progress bar via `huggingface_hub`.
- Once verified, the executable must boot the `llama-server` process with SYCL backend parameters and launch the `server.py` WebSocket/HTTP instance on port `8765`.

R2. Teach Mode & Safety Boundary Logging Infrastructure
Implement an interactive override handler inside `src/agent_loop.py` and write logging endpoints to `src/safety_logger.py`.
- When a user performs an interactive correction (hotkey override or explicit point adjustment), capture the precise screen coordinates $(x, y)$, target element screenshot, and full model context buffer.
- Append production record payloads to `dataset/shadow_dataset.jsonl` matching the standard schema (`timestamp`, `screen_dim`, `user_action`, `model_prediction`, `error_delta_px`, `context_history`).
- Implement boundary restriction enforcement in `src/safety_logger.py` that checks actions against user-defined restricted desktop zones (`config/safety_rules.json`) and writes security breach attempts to `dataset/safety_audit.jsonl`.

R3. Dynamic Plugin Ecosystem
Implement a dynamic production plugin loader in `src/plugin_manager.py` using Python's `importlib` and `pkgutil`.
- Scans `src/plugins/` directory at startup and dynamically registers any valid plugin module implementing the `BaseForgePlugin` interface.
- Implement two initial production plugins:
  1. `DevModePlugin` (`src/plugins/dev_mode.py`): Intercepts Terminal/IDE window handles and executes direct shell commands.
  2. `StudentModePlugin` (`src/plugins/student_mode.py`): Enforces focus window bounds and filters prohibited applications during study sessions.
- Expose runtime plugin discovery, activation, and action routing through `src/plugin_manager.py` integrated directly into `src/agent_loop.py`.

Acceptance Criteria

One-Click Installer
 - Running `python forge_builder.py` successfully produces a compiled OS-native binary in `dist/`.
 - Launching the executable verifies model integrity, triggers automated download if missing, and opens the live WebSocket interface on `ws://localhost:8765`.

Teach Mode & Safety Logs
 - Live user click overrides are intercepted and correctly formatted directly to `dataset/shadow_dataset.jsonl`.
 - Any attempted AI action within restricted screen bounds set in `config/safety_rules.json` is blocked before execution and logged to `dataset/safety_audit.jsonl`.

Plugin Ecosystem
 - Adding a new `.py` file to `src/plugins/` causes `plugin_manager.py` to auto-discover and register the plugin on backend boot without core code modification.
 - Simulated and live action payloads routed through `DevModePlugin` and `StudentModePlugin` execute full operational workflows and return validated structured outputs.
</USER_REQUEST>
