import os
import time
import argparse
import pyautogui
from PIL import Image
from tests.run_inference import run_vlm_inference
from execution.executor import execute_action

def main():
    parser = argparse.ArgumentParser(description="Forge Agent: End-to-End VLM Pipeline")
    parser.add_argument("--prompt", required=True, help="Instruction for the Forge Agent")
    parser.add_argument("--screenshot_path", default="temp_screenshot.png", help="Path to save the temporary screenshot")
    
    args = parser.parse_args()
    
    print(f"--- Forge Agent Initialized ---")
    print(f"Instruction: {args.prompt}")
    
    # 1. Take a screenshot
    print(f"Capturing screenshot to {args.screenshot_path}...")
    screenshot = pyautogui.screenshot()
    screenshot.save(args.screenshot_path)
    
    # 2. Run inference
    print("Running VLM Inference on the screenshot...")
    try:
        action_plan = run_vlm_inference(args.screenshot_path, args.prompt)
        print(f"Action Plan Received: {action_plan}")
    except Exception as e:
        print(f"Failed to run inference: {e}")
        return
        
    # 3. Execute the action
    print("Executing Action Plan...")
    success = execute_action(action_plan)
    
    if success:
        print("Action executed successfully.")
    else:
        print("Action execution failed or skipped.")
        
    # Cleanup
    if os.path.exists(args.screenshot_path):
        os.remove(args.screenshot_path)

if __name__ == "__main__":
    main()
