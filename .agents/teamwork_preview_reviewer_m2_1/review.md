# Review Report — Milestone 2: Wire Unified VLM Pipeline

**Verdict**: APPROVE (PASS)

## Review Summary
Milestone 2 implementation cleanly wires the Unified VLM Pipeline into `src/agent_loop.py` and `server.py`. Desktop screenshots are captured on `TEXT_INPUT` events, passed alongside user instructions to `run_vlm_inference()`, and executed via `execute_task_plan()`. SYCL environment flags for Intel Arc iGPU hardware acceleration (`SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1`, `ZES_ENABLE_SYSMAN=1`, `GGML_SYCL_DEBUG=0`) are strictly preserved in `run_vlm_inference()`. All 15 unit tests pass cleanly in `pytest tests/`. No integrity violations, facade implementations, or hardcoded shortcuts were found.

---

## Findings

### Minor Finding 1: Unquoted JSON Fallback Regex Scope
- **What**: `run_vlm_inference()` in `src/vlm_pipeline/tests/run_inference.py` uses regex replacement to sanitize unquoted JSON keys/values.
- **Where**: `src/vlm_pipeline/tests/run_inference.py:68-70`
- **Why**: Works well for standard VLM action outputs, but complex nested strings with colons might theoretically require robust JSON repair if the model outputs malformed JSON.
- **Suggestion**: Ensure future prompt engineering or schema formatting guides enforce valid JSON directly from `llama-mtmd-cli`.

---

## Verified Claims

- **Claim 1**: `TEXT_INPUT` events in `server.py` trigger VLM pipeline via `plan_task()` and `execute_task_plan()`.
  - **Method**: Inspected `server.py:245-273` and `src/agent_loop.py:45-82`. Verified `_react_worker()` routes through `plan_task()` which calls `capture_screenshot()` and `run_vlm_inference()`.
  - **Result**: PASS.

- **Claim 2**: SYCL execution environment flags are preserved in VLM invocation.
  - **Method**: Inspected `src/vlm_pipeline/tests/run_inference.py:25-29` and ran `pytest tests/test_vlm_pipeline.py::test_sycl_flags_preset_in_inference_wrapper`.
  - **Result**: PASS.

- **Claim 3**: All unit tests pass cleanly without dummy stubs or facade implementations.
  - **Method**: Executed `pytest tests/`. 15 test cases passed in 41.06s.
  - **Result**: PASS.

---

## Coverage Gaps

- **Physical Hardware End-to-End Execution**: Full GGUF inference requires physical Intel Arc iGPU drivers and GGUF model binaries at `src/vlm_pipeline/export/`. Unit tests use mock subprocess execution for isolated verification.
  - **Risk Level**: LOW.
  - **Recommendation**: Accept risk; mocked subprocess tests properly assert CLI call signature and environment flag propagation.

---

## Unverified Items
- None.
