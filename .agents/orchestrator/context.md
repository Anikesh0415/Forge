# Project Context & Findings

## Requirements Summary
- Project: Forge UI Unified VLM Refactor
- Core Objectives:
  1. Delete `src/planner.py`, clean `requirements.txt` (remove `ollama` & legacy vision deps), remove legacy routes/state from `server.py`.
  2. Wire `TEXT_INPUT` event in `server.py` / `src/agent_loop.py` to screenshot + VLM inference wrapper, preserving SYCL flags.
  3. Auto-execute valid VLM JSON actions with a 1.5s toast delay ("Executing: [Action] in 1.5s... [Press ESC to Cancel]") and global ESC listener for pyautogui halt.
  4. Stage, commit, and push changes to `main` branch.

## Codebase Map (Initial)
- Workspace: `E:\AIF_Project`
- Agents Directory: `E:\AIF_Project\.agents`
- Subagent Directory Pattern: `E:\AIF_Project\.agents\<agent_dir>`

## Active State
- Milestone: M1 (Legacy Cleanup) - Exploration starting
- Subagents: Dispatching 3 Explorers
