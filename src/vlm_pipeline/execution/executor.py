import json
import pyautogui
import time

def execute_action(action_plan: dict):
    """
    Executes a desktop action based on the parsed JSON action plan from the VLM.
    """
    try:
        from src.agent_loop import memory_mgr
        if getattr(memory_mgr, 'abort_flag', False):
            print("🛑 Execution aborted before action start (abort_flag set).")
            return False
    except Exception:
        pass

    if "raw_output" in action_plan:
        import re
        raw = action_plan["raw_output"]
        match = re.search(r'action:\s*([a-zA-Z0-9_]+)', raw)
        if match:
            action_plan = {"action": match.group(1)}
            
    if "action" not in action_plan:
        print(f"Unknown or invalid action plan: {action_plan}")
        return False
        
    action = action_plan["action"]
    
    try:
        if action == "click":
            x = action_plan.get("x")
            y = action_plan.get("y")
            button = action_plan.get("button", "left")
            if x is not None and y is not None:
                print(f"Executing: click at ({x}, {y}) with {button} button")
                pyautogui.click(x=int(x), y=int(y), button=button)
            else:
                print("Missing x or y coordinates for click.")
                
        elif action == "type":
            text = action_plan.get("text")
            if text:
                print(f"Executing: type '{text}'")
                pyautogui.write(text, interval=0.05)
            else:
                print("Missing text for type action.")
                
        elif action == "press":
            key = action_plan.get("key")
            if key:
                print(f"Executing: press '{key}'")
                pyautogui.press(key)
            else:
                print("Missing key for press action.")
                
        elif action == "double_click":
            x = action_plan.get("x")
            y = action_plan.get("y")
            if x is not None and y is not None:
                print(f"Executing: double_click at ({x}, {y})")
                pyautogui.doubleClick(x=int(x), y=int(y))
            else:
                print("Missing x or y coordinates for double_click.")
                
        elif action == "scroll":
            clicks = action_plan.get("clicks")
            if clicks is not None:
                print(f"Executing: scroll {clicks}")
                pyautogui.scroll(int(clicks))
            else:
                print("Missing clicks for scroll action.")
                
        elif action == "open_github":
            print("Executing: Opening GitHub via run dialog...")
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write('https://github.com')
            pyautogui.press('enter')
            
        elif action == "sleep":
            t = action_plan.get("time", 1)
            print(f"Executing: sleep for {t}s")
            time.sleep(float(t))
            
        else:
            print(f"Unsupported action type: {action}")
            return False
            
        return True
        
    except pyautogui.FailSafeException as fse:
        print(f"🛑 [KILLSWITCH] PyAutoGUI FailSafe triggered! Action '{action}' aborted.")
        try:
            from src.agent_loop import memory_mgr
            memory_mgr.abort_flag = True
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"Failed to execute action '{action}': {e}")
        return False

if __name__ == "__main__":
    # Test cases
    print("Testing executor...")
    execute_action({"action": "click", "x": 100, "y": 100})
    time.sleep(1)
    execute_action({"action": "type", "text": "Test from Forge Executor"})
