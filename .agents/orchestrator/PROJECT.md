# Project: Forge AI OS Consumer Features

## Architecture
- Forge AI OS backend: `server.py` (WebSocket/HTTP server on port 8765) and `src/agent_loop.py`.
- One-Click Installer: `forge_builder.py` + `forge.spec` creating standalone executable with Hugging Face auto-downloader (`bartowski/Qwen2-VL-2B-Instruct-GGUF`) and SYCL llama-server process boot.
- Teach Mode & Safety Logger: Interactive override screen capture & payload logging in `dataset/shadow_dataset.jsonl`; restricted desktop zones check (`config/safety_rules.json`) logging breaches to `dataset/safety_audit.jsonl` in `src/safety_logger.py`.
- Dynamic Plugin Ecosystem: `src/plugin_manager.py` using `importlib` and `pkgutil` to dynamically discover and register plugins implementing `BaseForgePlugin`. Initial plugins: `DevModePlugin` (`src/plugins/dev_mode.py`) and `StudentModePlugin` (`src/plugins/student_mode.py`).

## Code Layout
- `forge_builder.py`, `forge.spec`: Bundling and installer entry point.
- `src/agent_loop.py`: Agent execution loop, teach mode override handler, plugin routing.
- `src/safety_logger.py`: Safety boundary checker and audit logger.
- `src/plugin_manager.py`: Dynamic plugin discovery and lifecycle manager.
- `src/plugins/dev_mode.py`: Developer mode plugin for terminal/IDE interception.
- `src/plugins/student_mode.py`: Student mode plugin for focus bounds and app filtering.
- `config/safety_rules.json`: Safety boundary configuration.
- `dataset/shadow_dataset.jsonl`, `dataset/safety_audit.jsonl`: Logging outputs.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Cross-Platform One-Click Installer & Production Bundler | `forge_builder.py`, `forge.spec` | none | DONE |
| 2 | Teach Mode & Safety Boundary Logging Infrastructure | `src/agent_loop.py`, `src/safety_logger.py`, `dataset/shadow_dataset.jsonl`, `config/safety_rules.json`, `dataset/safety_audit.jsonl` | none | DONE |
| 3 | Dynamic Plugin Ecosystem & Core Integration | `src/plugin_manager.py`, `src/plugins/dev_mode.py`, `src/plugins/student_mode.py`, integration into `src/agent_loop.py` | M2 | DONE |
| 4 | E2E Integration & Verification | All components and acceptance criteria | M1, M2, M3 | PLANNED |

## Interface Contracts
### Plugin Interface (`BaseForgePlugin`)
- `plugin_name: str`
- `plugin_version: str`
- `initialize(config: dict) -> bool`
- `execute_action(action_payload: dict) -> dict`
- `filter_action(action_payload: dict) -> bool`

### Safety Logger API
- `check_boundary_violation(action_payload: dict) -> bool`
- `log_shadow_record(record_payload: dict) -> None`
- `log_safety_audit(breach_payload: dict) -> None`
