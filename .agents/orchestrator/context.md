# Context: Forge AI OS Consumer Features Project

## Overview
Project orchestrator for implementing three key consumer features in Forge AI OS:
1. One-Click Installer & Bundler (`forge_builder.py`, `forge.spec`)
2. Teach Mode & Safety Boundary Logging (`src/agent_loop.py`, `src/safety_logger.py`, dataset files, safety rules config)
3. Dynamic Plugin Ecosystem (`src/plugin_manager.py`, `src/plugins/dev_mode.py`, `src/plugins/student_mode.py`)

## Key System Requirements & Constraints
- No mocks, stubs, or dummy implementations. All code must be production-grade.
- PyInstaller bundling for `server.py`. Entry script checks `models/Qwen2-VL-2B-Instruct-Q4_K_M.gguf`, downloads via `huggingface_hub` from `bartowski/Qwen2-VL-2B-Instruct-GGUF` if missing.
- Boots `llama-server` with SYCL backend params and launches `server.py` on port 8765.
- Teach Mode: interactive override capturing screen $(x,y)$, screenshot, context buffer -> `dataset/shadow_dataset.jsonl`.
- Safety boundary: check restricted zones from `config/safety_rules.json` -> log breaches to `dataset/safety_audit.jsonl`.
- Plugin Ecosystem: `src/plugin_manager.py` using `importlib` and `pkgutil` dynamically loading `BaseForgePlugin` implementations in `src/plugins/`.
