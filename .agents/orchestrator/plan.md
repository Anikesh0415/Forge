# Execution Plan: Forge UI Unified VLM Refactor

## Strategic Goal
Refactor Forge UI to a unified VLM pipeline with auto-execution and ESC killswitch while stripping legacy planner/deps, preserving SYCL support, and committing/pushing to git main.

## Milestones & Tasks

### Milestone 1: Legacy Dependencies Cleanup
- Task 1.1: Remove `src/planner.py`.
- Task 1.2: Remove `ollama` and legacy vision dependencies from `requirements.txt`.
- Task 1.3: Clean legacy backend API routes and state logic from `server.py`.
- Verification: Build/import check, verify no references to `planner.py` or legacy routes remain.

### Milestone 2: Wire Unified VLM Pipeline
- Task 2.1: Map VLM inference wrapper interface and SYCL execution flags.
- Task 2.2: Update `server.py` and `src/agent_loop.py` `TEXT_INPUT` handler to capture screenshots and invoke VLM wrapper with screenshot + prompt.
- Task 2.3: Bypass legacy `plan_task()` calls completely.
- Verification: Code review, unit test/dry-run of VLM invocation with SYCL flags.

### Milestone 3: Auto-Execution & Killswitch Implementation
- Task 3.1: Enable automatic execution of parsed VLM JSON actions (no manual "Confirm").
- Task 3.2: Implement 1.5s UI toast delay ("Executing: [Action] in 1.5s... [Press ESC to Cancel]").
- Task 3.3: Implement global Python ESC listener to halt pyautogui actions instantly.
- Verification: Test toast countdown timing, test ESC key cancellation hook.

### Milestone 4: Verification & Git Operations
- Task 4.1: Run full test suite / verification checks across all acceptance criteria.
- Task 4.2: Perform Forensic Audit to ensure no dummy/hardcoded logic or cheat patterns.
- Task 4.3: Git stage, commit with clear refactor message, and push to `main` branch.
