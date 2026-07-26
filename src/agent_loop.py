import os
import time
import asyncio
import pyautogui
from src.vision import verify_anchor, smart_wait_for_completion, preflight_check
from src.context_manager import ContextManager
from src.memory_manager import MemoryManager
from src.execution_manager import ExecutionManager
from src.logger import logger
from src.macro_orchestrator import macro_orchestrator
from src.vlm_pipeline.tests.run_inference import run_vlm_inference

# Configuration Constants
ACTION_PAUSE         = 0.5   # seconds after standard actions
APP_OPEN_WAIT        = 2.0   # seconds before first anchor check on app open
OPEN_APP_MAX_RETRIES = 3     # retry count for page/app load anchors
OPEN_APP_RETRY_DELAY = 2.0   # seconds between retries

context_mgr = ContextManager()
memory_mgr  = MemoryManager()
exec_mgr    = ExecutionManager()


def capture_screenshot(output_path: str = "temp_screenshot.png") -> str:
    """
    Captures desktop screenshot to the specified output path using mss (if available) or pyautogui/PIL fallback.
    """
    abs_path = os.path.abspath(output_path)
    try:
        import mss
        with mss.mss() as sct:
            sct.shot(mon=-1, output=abs_path)
    except Exception as e:
        logger.info(f"mss screenshot capture unavailable ({e}), using pyautogui/PIL fallback.")
        try:
            shot = pyautogui.screenshot()
            shot.save(abs_path)
        except Exception:
            from PIL import ImageGrab
            shot = ImageGrab.grab()
            shot.save(abs_path)
    return abs_path


async def plan_task(instruction: str, update_callback=None, ctx_summary: str = None) -> list:
    """
    Generates action plan using unified VLM pipeline (run_vlm_inference).
    Snaps desktop screenshot and passes screenshot path + instruction to VLM.
    Preserves all SYCL execution flags set in run_vlm_inference.
    """
    callback = update_callback if callable(update_callback) else None

    def notify(msg: str):
        logger.info(f"[Agent Planner] {msg}")
        if callback:
            callback(msg)

    notify(f"[TRACE] Analyzing instruction with VLM: '{instruction}'...")

    # 1. Capture Desktop Screenshot
    screenshot_path = capture_screenshot("temp_screenshot.png")
    notify(f"[TRACE] Screenshot captured to {screenshot_path}")

    # 2. Run VLM Inference (SYCL flags configured inside run_vlm_inference)
    notify("[TRACE] Running unified VLM inference pipeline...")
    vlm_result = run_vlm_inference(screenshot_path, instruction)

    # Parse returned action dictionary/list into plan list
    if isinstance(vlm_result, list):
        plan = vlm_result
    elif isinstance(vlm_result, dict):
        if "plan" in vlm_result and isinstance(vlm_result["plan"], list):
            plan = vlm_result["plan"]
        elif "actions" in vlm_result and isinstance(vlm_result["actions"], list):
            plan = vlm_result["actions"]
        else:
            plan = [vlm_result]
    else:
        plan = [{"raw_output": str(vlm_result)}]

    notify(f"[TRACE] VLM Action Plan generated: {plan}")
    return plan


async def execute_task_plan(plan: list, update_callback=None) -> bool:
    """
    Executes the generated action plan.
    """
    def notify(msg: str):
        logger.info(f"[Agent Loop] {msg}")
        if update_callback:
            update_callback(msg)

    if not plan:
        notify("[TRACE] No plan to execute.")
        return False

    if getattr(memory_mgr, 'abort_flag', False):
        notify("🛑 TASK ABORTED BY KILL-SWITCH!")
        memory_mgr.complete_task(success=False)
        return False

    notify(f"[TRACE] Starting execution of {len(plan)} step(s)...")

    for idx, step in enumerate(plan):
        if getattr(memory_mgr, 'abort_flag', False):
            notify("🛑 TASK ABORTED BY KILL-SWITCH!")
            memory_mgr.complete_task(success=False)
            return False

        action_type  = step.get("action", "").lower()
        target       = step.get("target") or step.get("name") or step.get("url") or step.get("text") or ""
        anchor_check = step.get("anchor_check", "")

        memory_mgr.update_task_step(idx, status="executing")
        notify(f"[TRACE] Step {idx+1}/{len(plan)}: {action_type} ({target})")

        # ── 1. OBSERVE & PREFLIGHT ──────────────────────────────────────────
        fast_macros = ["send_whatsapp", "set_timer", "open_app", "open_browser"]
        if action_type not in fast_macros and target:
            pre_res = preflight_check(str(target))
            if not pre_res["clear_to_proceed"]:
                notify(f"[TRACE] ⚠️ Preflight Warning: {pre_res['popup_description']}")

        # ── 1.5. SAFETY GUARDRAIL ───────────────────────────────────────────
        def is_safe_action(action: str, tgt: str) -> bool:
            if action in ["type_text", "key_shortcut", "type", "press"]:
                blacklist = ["del ", "format ", "rmdir", "rd /s", "powershell -enc", "reg add", "net user", "drop table"]
                if any(bad in str(tgt).lower() for bad in blacklist):
                    return False
            return True
            
        if not is_safe_action(action_type, str(target)):
            notify(f"[TRACE] 🛑 SECURITY ALERT: Blocked destructive action '{target}'")
            memory_mgr.log_action(action_type, str(target), "Blocked by Safety Guardrail", False)
            memory_mgr.complete_task(success=False)
            return False

        # ── 2. EXECUTE ──────────────────────────────────────────────────────
        try:
            if getattr(memory_mgr, 'abort_flag', False):
                notify("🛑 TASK ABORTED BY KILL-SWITCH!")
                memory_mgr.complete_task(success=False)
                return False
            success, exec_msg = await exec_mgr.execute_step(step)
            if not success:
                from src.vlm_pipeline.execution.executor import execute_action
                vlm_exec_success = execute_action(step)
                if vlm_exec_success:
                    success = True
                    exec_msg = f"Executed VLM action '{action_type}'"
        except pyautogui.FailSafeException as fse:
            memory_mgr.abort_flag = True
            notify("🛑 TASK ABORTED BY KILL-SWITCH!")
            memory_mgr.complete_task(success=False)
            return False
        except Exception as e:
            if getattr(memory_mgr, 'abort_flag', False):
                notify("🛑 TASK ABORTED BY KILL-SWITCH!")
                memory_mgr.complete_task(success=False)
                return False
            try:
                from src.vlm_pipeline.execution.executor import execute_action
                success = execute_action(step)
                exec_msg = f"Executed VLM action '{action_type}'" if success else f"Crash during execution: {e}"
            except Exception:
                success, exec_msg = False, f"Crash during execution: {e}"
            
        if getattr(memory_mgr, 'abort_flag', False):
            notify("🛑 TASK ABORTED BY KILL-SWITCH!")
            memory_mgr.complete_task(success=False)
            return False
            
        if not success:
            notify(f"[TRACE] Action execution warning: {exec_msg}")
        elif action_type.startswith("background_") or action_type == "summarize_youtube":
            notify(f"[ANSWER] {exec_msg}")

        # ── 3. VERIFY ───────────────────────────────────────────────────────
        NO_VERIFY = {"click", "type", "press", "double_click", "scroll", "open_github", "copy_all", "paste", "speak", "wait_until", "hover_element", "read_file", "write_file", "run_terminal", "summarize_youtube", "generate_study_html", "search_knowledge_base"}
        if action_type in NO_VERIFY or not anchor_check:
            await asyncio.sleep(ACTION_PAUSE)
            memory_mgr.log_action(action_type, str(target), exec_msg, True, "No verification needed")
            continue

        if action_type in {"open_app", "open_browser"}:
            notify(f"[TRACE] Waiting {APP_OPEN_WAIT}s for page/app to load...")
            await asyncio.sleep(APP_OPEN_WAIT)
            max_retries = OPEN_APP_MAX_RETRIES
        else:
            await asyncio.sleep(ACTION_PAUSE)
            max_retries = 1

        verified = False
        
        for attempt in range(max_retries):
            notify(f"[TRACE] VISTA anchor check (attempt {attempt+1}/{max_retries}): '{anchor_check}'")
            try:
                anchor_met = verify_anchor(anchor_check)
            except Exception as e:
                notify(f"[TRACE] VISTA check crashed: {e}")
                anchor_met = False
                
            if anchor_met:
                notify("[TRACE] Anchor confirmed ✓")
                verified = True
                memory_mgr.log_action(action_type, str(target), exec_msg, True, "Anchor confirmed")
                break
            else:
                if attempt < max_retries - 1:
                    notify(f"[TRACE] Anchor not yet visible, retrying in {OPEN_APP_RETRY_DELAY}s...")
                    await asyncio.sleep(OPEN_APP_RETRY_DELAY)
                    try:
                        await exec_mgr.execute_step(step)
                    except Exception:
                        pass

        # ── 4. REFLECT & REPLAN ─────────────────────────────────────────────
        if not verified:
            notify(f"[TRACE] Step {idx+1} verification failed.")
            memory_mgr.complete_task(success=False)
            return False

    notify("[TRACE] Plan execution completed successfully.")
    return True


async def run_autonomous_agent(instruction: str, update_callback=None) -> bool:
    """
    The top-level entry point. Uses MacroOrchestrator to break down massive prompts.
    """
    def notify(msg: str):
        logger.info(f"[Macro Orchestrator] {msg}")
        if update_callback:
            update_callback(msg)

    notify("[TRACE] Checking if instruction requires Macro Loop Orchestration...")
    macro_plan = macro_orchestrator.analyze_instruction(instruction)
    
    if macro_plan.get("is_loop"):
        iterations = macro_plan.get("iterations", 1)
        notify(f"[TRACE] 🚀 MASSIVE LOOP DETECTED! Iterations: {iterations}")
        
        # 1. Setup Phase
        setup_task = macro_plan.get("setup_instructions")
        if setup_task:
            notify(f"[TRACE] Phase 1/3: Running Setup -> {setup_task}")
            setup_plan = await plan_task(setup_task, update_callback)
            if not await execute_task_plan(setup_plan, update_callback):
                notify("[TRACE] Setup failed. Aborting Macro.")
                return False
                
        # 2. Loop Phase
        loop_task = macro_plan.get("loop_instructions")
        if loop_task:
            notify(f"[TRACE] Phase 2/3: Executing Loop {iterations} times...")
            for i in range(iterations):
                notify(f"[TRACE] --- LOOP ITERATION {i+1} OF {iterations} ---")
                iter_plan = await plan_task(loop_task, update_callback)
                if not await execute_task_plan(iter_plan, update_callback):
                    notify(f"[TRACE] Loop iteration {i+1} failed! Attempting to continue next iteration...")
                    
        # 3. Teardown Phase
        teardown_task = macro_plan.get("teardown_instructions")
        if teardown_task:
            notify(f"[TRACE] Phase 3/3: Running Teardown -> {teardown_task}")
            teardown_plan = await plan_task(teardown_task, update_callback)
            await execute_task_plan(teardown_plan, update_callback)
            
        notify("[TRACE] ✅ Macro Orchestration Completed Successfully!")
        return True

    else:
        notify("[TRACE] Standard linear task detected.")
        plan = await plan_task(instruction, update_callback)
        return await execute_task_plan(plan, update_callback)


async def execute_react_loop(instruction: str, update_callback=None):
    """
    Executes the full ReAct loop using the unified VLM pipeline.
    """
    plan = await plan_task(instruction, update_callback)
    if not plan:
        return False
    return await execute_task_plan(plan, update_callback)


def trigger_self_healing_learning() -> str:
    """
    Exposed hook for the UI's `/learn` slash command.
    Tells the MemoryManager to compile the last successful task into a permanent skill.
    """
    result = memory_mgr.compile_learned_skill()
    logger.info(f"Self-Healing Triggered: {result}")
    return result


if __name__ == "__main__":
    asyncio.run(execute_react_loop("open browser to google.com"))

