import os
import time
import asyncio
import pyautogui
from src.context_manager import ContextManager
from src.memory_manager import MemoryManager
from src.execution_manager import ExecutionManager
from src.logger import logger
from src.vlm_pipeline.tests.run_inference import run_vlm_inference
from src.memory_buffer import ActionBuffer

# Configuration Constants
ACTION_PAUSE         = 0.5   # seconds after standard actions
APP_OPEN_WAIT        = 2.0   # seconds before first anchor check on app open
OPEN_APP_MAX_RETRIES = 3     # retry count for page/app load anchors
OPEN_APP_RETRY_DELAY = 2.0   # seconds between retries

context_mgr = ContextManager()
memory_mgr  = MemoryManager()
exec_mgr    = ExecutionManager()
action_buffer = ActionBuffer(max_length=5)


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

    if action_buffer.detect_loop():
        notify("⚠️ LOOP DETECTED! Executing reset safeguard...")
        pyautogui.press('esc')
        action_buffer.clear()
        
    context_str = action_buffer.get_context_string()
    if context_str:
        instruction = f"{instruction}\n\n{context_str}"

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

        # ── 1. SAFETY GUARDRAIL ───────────────────────────────────────────
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

        # ── 3. POST-ACTION PAUSE ────────────────────────────────────────────
        await asyncio.sleep(ACTION_PAUSE)
        if success:
            action_buffer.add_action(action_type, str(target))
        memory_mgr.log_action(action_type, str(target), exec_msg, success, "Action executed")

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

    notify("[TRACE] Single Task Plan Phase...")
    plan = await plan_task(instruction, update_callback)
    if not plan:
        return False

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

