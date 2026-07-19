import time
from src.planner import generate_plan
from src.action_library import (
    open_app, navigate_browser,
    type_action, key_action,
    click_action, scroll_action,
    copy_all, paste_action,
)
from src.vision import verify_anchor, smart_wait_for_completion

# How long to wait after open_app before starting verification
APP_OPEN_WAIT  = 3.0   # seconds — enough for a browser tab to appear
# How long to wait after any instant action before the next step
ACTION_PAUSE   = 0.3   # seconds

# For open_app, VISTA will retry verification up to this many times
OPEN_APP_MAX_RETRIES = 3
OPEN_APP_RETRY_DELAY = 2.0   # seconds between retries


def plan_task(instruction: str, update_callback=None) -> list:
    """
    Generates the ARIA plan for the instruction, checks for complex keywords,
    and returns the plan list.
    """
    def notify(msg: str):
        print(f"[Agent Planner] {msg}")
        if update_callback:
            update_callback(msg)

    notify(f"Thinking about: '{instruction}'...")

    # Generate plan
    plan = generate_plan(instruction)

    # CRITICAL CHECK: re-plan if too few steps
    complex_kw = ["and", "then", "copy", "send", "open", "paste"]
    is_complex = any(kw in instruction.lower() for kw in complex_kw)
    
    if plan and is_complex and len(plan) < 4:
        notify(f"⚠️ Only {len(plan)} steps generated for complex task — re-planning stricter...")
        plan = generate_plan(instruction + " [IMPORTANT: This requires multiple apps/actions, list ALL steps]")

    if not plan:
        notify("ARIA failed to generate a plan.")
        return []

    notify(f"ARIA plan generated: {len(plan)} step(s).")
    return plan


def execute_task_plan(plan: list, update_callback=None):
    """
    Executes the generated ARIA plan and performs anchor verification.
    """
    def notify(msg: str):
        print(f"[Agent Loop] {msg}")
        if update_callback:
            update_callback(msg)

    if not plan:
        notify("No plan to execute.")
        return

    notify(f"Starting execution of {len(plan)} step(s)...")

    for idx, step in enumerate(plan):
        action_type  = step.get("action", "").lower()
        anchor_check = step.get("anchor_check", "")   # Phase 4 anchor

        notify(f"Step {idx+1}/{len(plan)}: {action_type}")

        # ── ACT ────────────────────────────────────────────────────────────
        try:
            if action_type == "open_app":
                open_app(step.get("name", step.get("app", "")))

            elif action_type == "open_browser":
                navigate_browser(step.get("url", ""))

            elif action_type == "type_text":
                type_action(step.get("text", ""))

            elif action_type == "key_shortcut":
                key_action(step.get("keys", step.get("key", "")))

            elif action_type == "click_element":
                # For now just mock it until vision is fully hooked up
                notify(f"Clicking element: {step.get('target', '')}")

            elif action_type == "scroll":
                scroll_action(step.get("amount", 0))

            elif action_type == "copy_all":
                copy_all()

            elif action_type == "paste":
                paste_action()

            elif action_type == "wait_until":
                condition = step.get("condition", "")
                if condition:
                    notify(f"Waiting for condition: '{condition}'...")
                    success = smart_wait_for_completion(condition)
                    if not success:
                        notify(f"Wait timeout for: {condition}")
                        return
                    continue # Skip anchor verify since wait handles it

            elif action_type == "speak":
                text = step.get("text", "")
                notify(f"Speaking: {text}")
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass

            else:
                notify(f"Unknown action '{action_type}' — skipping.")
                continue

        except Exception as e:
            notify(f"Action raised an exception: {e}")
            continue

        # ── VERIFY (Phase 4: anchor-based) ─────────────────────────────────

        # Actions that need no verification — they are instant and deterministic
        NO_VERIFY = {"scroll", "copy_all", "paste", "click", "speak", "wait_until"}
        if action_type in NO_VERIFY or not anchor_check:
            time.sleep(ACTION_PAUSE)
            continue

        # For page-loading actions: give the OS a head-start before asking VISTA
        if action_type in {"open_app", "open_browser"}:
            notify(f"Waiting {APP_OPEN_WAIT}s for page/app to load...")
            time.sleep(APP_OPEN_WAIT)
            max_retries = OPEN_APP_MAX_RETRIES
        else:
            # For type / key: short pause, single check
            time.sleep(ACTION_PAUSE)
            max_retries = 1

        # Run anchor verification
        verified = False
        
        for attempt in range(max_retries):
            notify(f"VISTA anchor check (attempt {attempt+1}/{max_retries}): '{anchor_check}'")
            if verify_anchor(anchor_check):
                notify(f"Anchor confirmed ✓")
                verified = True
                break
            else:
                if attempt < max_retries - 1:
                    notify(f"Anchor not yet visible, retrying in {OPEN_APP_RETRY_DELAY}s...")
                    time.sleep(OPEN_APP_RETRY_DELAY)
                    
                    # Re-execute action on retry
                    notify(f"Re-executing action: {action_type}")
                    try:
                        if action_type == "open_app":
                            open_app(step.get("name", step.get("app", "")))
                        elif action_type == "open_browser":
                            navigate_browser(step.get("url", ""))
                        elif action_type == "type_text":
                            type_action(step.get("text", ""))
                        elif action_type == "key_shortcut":
                            key_action(step.get("keys", step.get("key", "")))
                        elif action_type == "click_element":
                            notify(f"Clicking element: {step.get('target', '')}")
                        elif action_type == "scroll":
                            scroll_action(step.get("amount", 0))
                    except Exception as e:
                        notify(f"Retry execution failed: {e}")

        if not verified:
            notify(f"Step failed after {max_retries} retries. Task paused.")
            return False

    notify("Task complete.")
    return True


def execute_react_loop(instruction: str, update_callback=None):
    """
    Executes the full ReAct loop (sequential plan + execution) for backward compatibility.
    """
    plan = plan_task(instruction, update_callback)
    if not plan:
        return
    execute_task_plan(plan, update_callback)

    notify("Task complete.")


if __name__ == "__main__":
    execute_react_loop("open youtube and search for lo-fi music")
