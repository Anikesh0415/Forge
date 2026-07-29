## 2026-07-27T22:01:09Z
You are the Launcher Hardening Worker for Forge AI OS (`forge_launcher.py`).
Working directory: E:\AIF_Project\.agents\worker_launcher_hardener
Project root: E:\AIF_Project
Parent conversation ID: e48cfc24-a943-4900-9061-d6007221efcf

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your mission:
Apply the following 6 hardening improvements to `forge_launcher.py`:
1. In `boot_llama_server()`, check if `llama-server.exe` exists (`os.path.exists(llama_exe)`). If missing, raise an informative `RuntimeError("llama-server executable not found at: ...")` or handle gracefully BEFORE calling `subprocess.Popen` so it does not crash with an unhandled `FileNotFoundError`.
2. In `boot_forge_app()`, wrap the `llama_proc` lifecycle (including `poll_llama_server_health` and backend server startup) inside a `try...finally` block to ensure `llama_proc` is safely terminated/cleaned up on any exception or exit.
3. In `boot_forge_app()`, check the return value of `poll_llama_server_health()`. If `False` (timed out), handle the timeout cleanly (raise an error or abort launch) rather than ignoring the return value.
4. Improve port check/port conflict handling in `is_llama_server_running()` and `boot_llama_server()`.
5. Sanitize `sys.path` handling so `BASE_DIR` is appended safely without hijacking standard library imports.
6. Set `os.chdir(BASE_DIR)` at the start of the boot sequence in `forge_launcher.py`.

Verification after implementation:
1. Run `pytest tests/test_safety_logger.py tests/test_plugin_system.py tests/test_architecture.py -v`.
2. Run `python -c "import forge_builder, forge_launcher; print('BUILDER OK')"`.
3. Create `handoff.md` in `E:\AIF_Project\.agents\worker_launcher_hardener\handoff.md` with complete implementation details and test command outputs.
4. Send completion report to parent orchestrator (`e48cfc24-a943-4900-9061-d6007221efcf`) via send_message.
