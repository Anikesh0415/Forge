import os
import json
import time
from datetime import datetime
import pyautogui
from PIL import Image

DATASET_DIR = os.path.join(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
JSONL_FILE = os.path.join(DATASET_DIR, "forge_vlm_data.jsonl")

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)

def capture_screenshot(filename: str) -> str:
    """Captures a screenshot and saves it to the images directory."""
    print("📸 Taking screenshot in 3 seconds...")
    time.sleep(3)
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(IMAGES_DIR, filename)
    screenshot.save(filepath)
    print(f"✅ Screenshot saved to {filepath}")
    return filepath

def append_to_jsonl(image_filename: str, user_prompt: str, action_plan: str):
    """Appends a new conversation entry to the JSONL dataset."""
    
    # Try to parse the action_plan to ensure it's valid JSON
    try:
        parsed_plan = json.loads(action_plan)
        # Re-encode to ensure compact, standard formatting
        action_plan_str = json.dumps(parsed_plan)
    except json.JSONDecodeError:
        print("⚠️ Warning: Action plan provided is not valid JSON. Saving as raw string.")
        action_plan_str = action_plan

    entry = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": f"images/{image_filename}"},
                    {"type": "text", "text": user_prompt}
                ]
            },
            {
                "role": "assistant",
                "content": action_plan_str
            }
        ]
    }
    
    with open(JSONL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✅ Entry added to {JSONL_FILE}")

def main():
    print("="*50)
    print("🛠️ Forge VLM Automated Dataset Creator Tool")
    print("="*50)
    
    while True:
        choice = input("\nDo you want to create a new dataset entry? (y/n): ").strip().lower()
        if choice != 'y':
            print("Exiting...")
            break
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"forge_screen_{timestamp}.jpg"
        
        # 1. Capture Screenshot
        capture_screenshot(image_filename)
        
        # 2. Get User Prompt
        print("\n📝 Enter the user prompt (e.g., 'Open Browser and go to GitHub'):")
        user_prompt = input("> ").strip()
        
        # 3. Get Expected JSON Action Plan
        print("\n🧩 Enter the expected JSON Action Plan (can be multiple lines, type 'EOF' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
            
        action_plan = "\n".join(lines).strip()
        
        # 4. Save to JSONL
        append_to_jsonl(image_filename, user_prompt, action_plan)

if __name__ == "__main__":
    main()
