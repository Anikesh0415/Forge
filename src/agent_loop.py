import os
import time
import math
import asyncio
from datetime import datetime, timezone
import pyautogui
from src.context_manager import ContextManager
from src.memory_manager import MemoryManager
from src.execution_manager import ExecutionManager
from src.logger import logger
from src.vlm_pipeline.tests.run_inference import run_vlm_inference
from src.memory_buffer import ActionBuffer
from src.plugin_manager import PluginManager
from src.safety_logger import safety_logger
from src.aria_planner import AriaPlanner

# Configuration Constants
ACTION_PAUSE         = 0.5   # seconds after standard actions
APP_OPEN_WAIT        = 2.0   # seconds before first anchor check on app open
OPEN_APP_MAX_RETRIES = 3     # retry count for page/app load anchors
OPEN_APP_RETRY_DELAY = 2.0   # seconds between retries

context_mgr = ContextManager()
memory_mgr  = MemoryManager()
exec_mgr    = ExecutionManager()
action_buffer = ActionBuffer(max_length=5)
plugin_manager = PluginManager()
plugin_manager.discover_plugins()
aria_planner = AriaPlanner(memory_mgr, plugin_manager)


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


def crop_target_element(image_path: str, x: float, y: float, crop_width: int = 200, crop_height: int = 200) -> str:
    """
    Crops a square ROI around target coordinates (x, y) from desktop screenshot.
    Saves cropped image to dataset/images/crop_<timestamp_ms>.png and returns absolute path.
    """
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset", "images"))
    os.makedirs(images_dir, exist_ok=True)
    
    timestamp_ms = int(time.time() * 1000)
    crop_filename = f"crop_{timestamp_ms}.png"
    crop_path = os.path.join(images_dir, crop_filename)

    try:
        from PIL import Image
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img_w, img_h = img.size
            half_w, half_h = crop_width / 2.0, crop_height / 2.0
            
            left = max(0, int(x - half_w))
            upper = max(0, int(y - half_h))
            right = min(img_w, int(x + half_w))
            lower = min(img_h, int(y + half_h))
            
            cropped = img.crop((left, upper, right, lower))
            cropped.save(crop_path)
            return crop_path
    except Exception as e:
        logger.info(f"Failed to crop element screenshot: {e}")
    
    return ""


def handle_interactive_override(
    user_action: dict,
    model_prediction: dict = None,
    screenshot_path: str = None,
    context_history: list = None
) -> dict:
    """
    Interactive override handler for Teach Mode.
    Captures user coordinates, crops target element screenshot, calculates error delta in pixels,
    records context history, formats standard Teach Mode payload, and logs to dataset/shadow_dataset.jsonl.
    """
    if model_prediction is None:
        model_prediction = {}

    screen_dim = {"width": 1920, "height": 1080}
    try:
        sw, sh = pyautogui.size()
        screen_dim = {"width": int(sw), "height": int(sh)}
    except Exception:
        pass

    if not screenshot_path or not os.path.exists(screenshot_path):
        screenshot_path = capture_screenshot("temp_override.png")

    if screenshot_path and os.path.exists(screenshot_path):
        try:
            from PIL import Image
            img = Image.open(screenshot_path)
            screen_dim = {"width": img.width, "height": img.height}
        except Exception:
            pass

    user_x = user_action.get("x")
    user_y = user_action.get("y")

    crop_path = ""
    if user_x is not None and user_y is not None:
        crop_path = crop_target_element(screenshot_path, float(user_x), float(user_y))

    formatted_user_action = dict(user_action)
    if crop_path:
        formatted_user_action["target_crop_path"] = crop_path
    if screenshot_path:
        formatted_user_action["full_image_path"] = os.path.abspath(screenshot_path)

    model_x = model_prediction.get("x")
    model_y = model_prediction.get("y")
    
    error_delta_px = None
    if user_x is not None and user_y is not None and model_x is not None and model_y is not None:
        try:
            dx = float(user_x) - float(model_x)
            dy = float(user_y) - float(model_y)
            error_delta_px = round(math.sqrt(dx * dx + dy * dy), 2)
        except (ValueError, TypeError):
            error_delta_px = None

    if context_history is None:
        context_history = action_buffer.get_history()

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record_payload = {
        "timestamp": timestamp,
        "screen_dim": screen_dim,
        "user_action": formatted_user_action,
        "model_prediction": model_prediction,
        "error_delta_px": error_delta_px,
        "context_history": context_history
    }

    safety_logger.log_shadow_record(record_payload)
    return record_payload



async def plan_task(instruction: str, update_callback=None, ctx_summary: str = None) -> list:
    """
    Generates action plan using AriaPlanner.
    Snaps desktop screenshot and passes it to the planner.
    """
    callback = update_callback if callable(update_callback) else None

    def notify(msg: str):
        logger.info(f"[Agent Planner] {msg}")
        if callback:
            callback(msg)

    notify(f"[TRACE] Analyzing instruction with ARIA Planner: '{instruction}'...")

    # 1. Capture Desktop Screenshot
    screenshot_path = capture_screenshot("temp_screenshot.png")
    notify(f"[TRACE] Screenshot captured to {screenshot_path}")

    if action_buffer.detect_loop():
        notify("⚠️ LOOP DETECTED! Executing reset safeguard...")
        pyautogui.press('esc')
        action_buffer.clear()
        
    context_history = action_buffer.get_history()

    # 2. Run ARIA Planner
    notify("[TRACE] Running unified ARIA inference pipeline...")
    plan = aria_planner.generate_plan(instruction, screenshot_path, context_history)

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

        # ── 1. SAFETY GUARDRAIL & PLUGIN FILTERING ──────────────────────
        if safety_logger.check_boundary_violation(step):
            notify(f"[TRACE] 🛑 SECURITY ALERT: Blocked action '{action_type}' targeting '{target}' due to safety boundary violation")
            memory_mgr.log_action(action_type, str(target), "Blocked by Safety Guardrail", False)
            memory_mgr.complete_task(success=False)
            return False


        if not plugin_manager.filter_action(step):
            notify(f"[TRACE] 🛑 PLUGIN FILTER ALERT: Action '{action_type}' ({target}) blocked by active plugin policy.")
            memory_mgr.log_action(action_type, str(target), "Blocked by Plugin Action Filter Guardrail", False)
            memory_mgr.complete_task(success=False)
            return False

        # ── 2. EXECUTE ──────────────────────────────────────────────────────
        try:
            if getattr(memory_mgr, 'abort_flag', False):
                notify("🛑 TASK ABORTED BY KILL-SWITCH!")
                memory_mgr.complete_task(success=False)
                return False

            if plugin_manager.can_handle(step):
                notify(f"[TRACE] Routing action '{action_type}' to target plugin...")
                route_res = plugin_manager.route_action(step)
                success = route_res.get("success", False)
                exec_msg = route_res.get("message") or route_res.get("error") or str(route_res)
            else:
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

