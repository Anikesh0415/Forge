# Execution Plan: Forge AI OS Consumer Features

## Phase 1: Exploration & Architecture Analysis (Milestones 1 & 2)
1. Dispatch 3 Explorers (`teamwork_preview_explorer`) to inspect existing codebase structure:
   - Explorer 1: Inspect `server.py`, models directory, and bundling requirements for `forge_builder.py` and `forge.spec`.
   - Explorer 2: Inspect `src/agent_loop.py`, teach mode requirements, shadow dataset format, and safety logger requirements.
   - Explorer 3: Inspect `src/plugins/`, existing plugin implementations, `src/plugin_manager.py` requirements, `DevModePlugin`, and `StudentModePlugin`.

## Phase 2: Milestone 1 Execution — One-Click Installer & Production Bundler
1. Worker 1 implements `forge_builder.py` and `forge.spec`.
2. Reviewer 1 & Reviewer 2 verify build spec, Hugging Face downloading logic, SYCL llama-server invocation, and WebSocket boot.
3. Challenger 1 tests executable generation and launch workflow.
4. Forensic Auditor 1 runs integrity checks.
5. Gate evaluation.

## Phase 3: Milestone 2 Execution — Teach Mode & Safety Boundary Logging Infrastructure
1. Worker 2 implements interactive override handler in `src/agent_loop.py`, `src/safety_logger.py`, `config/safety_rules.json`, and logging schemas for `dataset/shadow_dataset.jsonl` & `dataset/safety_audit.jsonl`.
2. Reviewer 1 & Reviewer 2 verify coordinate capture, screenshot inclusion, context buffer formatting, and zone breach enforcement.
3. Challenger 2 verifies log payloads and boundary restriction blocking.
4. Forensic Auditor 2 runs integrity verification.
5. Gate evaluation.

## Phase 4: Milestone 3 Execution — Dynamic Plugin Ecosystem
1. Worker 3 implements `src/plugin_manager.py`, `src/plugins/dev_mode.py`, `src/plugins/student_mode.py`, and integrates plugin discovery/routing into `src/agent_loop.py`.
2. Reviewers verify auto-discovery via `importlib` and `pkgutil`, `BaseForgePlugin` interface, and plugin execution.
3. Challengers & Auditor verify integrity and dynamic loading.
4. Gate evaluation.

## Phase 5: Milestone 4 Execution — E2E Integration & Verification
1. Run complete test suite and acceptance tests across all 3 features.
2. Forensic Auditor runs final full integrity audit.
3. Sentinel report.
