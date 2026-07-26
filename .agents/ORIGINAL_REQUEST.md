# Original User Request

## 2026-07-25T17:06:25Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Get user approval → delegate to teamwork_preview

Refactor the Forge UI architecture to replace the legacy MultiStagePlanner and multi-model backend with a unified VLM pipeline featuring an auto-execution loop and emergency killswitch.

Working directory: `E:\AIF_Project`
Integrity mode: development

## Requirements

### R1. Remove Legacy Dependencies
Delete `src/planner.py`, remove `ollama` and vision dependencies from `requirements.txt`, and strip legacy backend API routes and state logic from `server.py`.

### R2. Wire Unified VLM
Modify `server.py` and `src/agent_loop.py` so that a `TEXT_INPUT` event snaps a screenshot and passes it alongside the user instruction to the new VLM inference wrapper, bypassing the old `plan_task()` logic.

### R3. Implement Auto-Execution & Killswitch
Execute the parsed JSON action plan immediately by default. Add a 1.5-second UI toast delay ("Executing: [Action] in 1.5s... [Press ESC to Cancel]") and a global Python listener (ESC key) that halts pyautogui execution.

### R4. Version Control
Stage all modified files, commit with a specific refactor message, and push to the `main` branch.

## Acceptance Criteria

### Execution & Integration
- [ ] `src/planner.py` no longer exists and legacy routing logic is removed from `server.py`.
- [ ] `TEXT_INPUT` events successfully trigger the VLM inference wrapper instead of the old planner.
- [ ] Valid VLM JSON outputs are automatically passed to the execution script without requiring a manual "Confirm" step.
- [ ] A 1.5-second delay occurs before execution, during which pressing the ESC key aborts the action.
- [ ] SYCL execution flags remain intact in the new VLM invocation logic.
- [ ] Changes are successfully committed and pushed to the remote repository.
