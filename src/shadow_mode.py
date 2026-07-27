import os
import sys
import time
import json
import math
import argparse
import threading
import queue
from datetime import datetime
import mss

from pynput import mouse

# Append src path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vlm_pipeline.tests.run_inference import run_vlm_inference
from src.safety_logger import safety_logger


DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')
LOG_FILE = os.path.join(DATASET_DIR, 'shadow_dataset.jsonl')

event_queue = queue.Queue()

def ensure_dirs():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

def take_screenshot(filepath):
    with mss.MSS() as sct:
        sct.shot(mon=-1, output=filepath)

def process_event_worker():
    while True:
        event = event_queue.get()
        if event is None:
            break
            
        timestamp = event['timestamp']
        x, y = event['x'], event['y']
        image_path = event['image_path']
        screen_size = event['screen_size']

        prompt = "Analyze this UI and predict the user's intended click action. You MUST output ONLY valid JSON containing numeric 'x' and 'y' coordinates. Format: {\"x\": 500, \"y\": 500}. Do not include bounding_boxes, types, or nested objects."
        
        ai_prediction = None
        error_delta = None
        
        try:
            prediction = run_vlm_inference(image_path, prompt)
            ai_prediction = prediction
            
            ai_x, ai_y = None, None
            if isinstance(prediction, dict):
                # Flatten the prediction to string to easily extract any x/y numbers using regex if standard parsing fails
                import re
                
                # Try standard exact paths first
                if "x" in prediction and "y" in prediction:
                    ai_x, ai_y = float(prediction["x"]), float(prediction["y"])
                elif "actions" in prediction and isinstance(prediction["actions"], list) and len(prediction["actions"]) > 0:
                    action = prediction["actions"][0]
                    if isinstance(action, dict):
                        if "x" in action and "y" in action:
                            ai_x, ai_y = float(action["x"]), float(action["y"])
                        elif "point" in action and isinstance(action["point"], dict):
                            ai_x, ai_y = float(action["point"].get("x", 0)), float(action["point"].get("y", 0))
                elif "primary_element_x" in prediction and "primary_element_y" in prediction:
                    ai_x, ai_y = float(prediction["primary_element_x"]), float(prediction["primary_element_y"])
                
                # If still none, try aggressive regex extraction
                if ai_x is None or ai_y is None:
                    raw_str = json.dumps(prediction)
                    # Look for bounding box like [x1, y1, x2, y2] or (x1,y1,x2,y2)
                    bbox_match = re.search(r'(?:bounding_box|bbox).*?[\[\(](\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)[\]\)]', raw_str)
                    if bbox_match:
                        x1, y1, x2, y2 = map(float, bbox_match.groups())
                        ai_x, ai_y = (x1 + x2) / 2, (y1 + y2) / 2
                    else:
                        # Fallback to the first two numbers we can find associated with x and y
                        x_match = re.search(r'["\']?x["\']?\s*:\s*(\d+)', raw_str)
                        y_match = re.search(r'["\']?y["\']?\s*:\s*(\d+)', raw_str)
                        if x_match and y_match:
                            ai_x, ai_y = float(x_match.group(1)), float(y_match.group(1))
                        
            if ai_x is not None and ai_y is not None:
                error_delta = math.sqrt((ai_x - float(x))**2 + (ai_y - float(y))**2)
        except Exception as e:
            print(f"ShadowMode Error querying VLM: {e}")
            
        user_action = {"type": "click", "x": x, "y": y, "full_image_path": image_path}
        crop_path = ""
        try:
            from src.agent_loop import crop_target_element
            crop_path = crop_target_element(image_path, float(x), float(y))
        except Exception:
            pass
        if crop_path:
            user_action["target_crop_path"] = crop_path

        from datetime import timezone
        record_payload = {
            "timestamp": datetime.fromtimestamp(timestamp / 1000.0, timezone.utc).isoformat().replace("+00:00", "Z") if isinstance(timestamp, (int, float)) else str(timestamp),
            "screen_dim": screen_size,
            "user_action": user_action,
            "model_prediction": ai_prediction if isinstance(ai_prediction, dict) else {"raw_output": str(ai_prediction)},
            "error_delta_px": round(error_delta, 2) if error_delta is not None else None,
            "context_history": []
        }
        
        safety_logger.log_shadow_record(record_payload)

            
        print(f"[Shadow Mode] Logged event. Delta: {error_delta}")
        event_queue.task_done()

def capture_and_queue(x, y, timestamp):
    image_name = f"shadow_{timestamp}.png"
    image_path = os.path.join(IMAGES_DIR, image_name)
    
    take_screenshot(image_path)
        
    with mss.MSS() as sct:
        monitor = sct.monitors[1] # primary
        screen_size = {"width": monitor["width"], "height": monitor["height"]}

    event_queue.put({
        "timestamp": timestamp,
        "x": x,
        "y": y,
        "image_path": image_path,
        "screen_size": screen_size
    })

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        timestamp = int(time.time() * 1000)
        # Capture instantly in a tiny thread so we don't block the mouse driver
        threading.Thread(target=capture_and_queue, args=(x, y, timestamp), daemon=True).start()

def run_shadow_mode():
    ensure_dirs()
    print("Starting Shadow Mode Listener...")
    
    worker = threading.Thread(target=process_event_worker, daemon=True)
    worker.start()
    
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        event_queue.put(None)
        worker.join()

def run_test_mode():
    ensure_dirs()
    print("Starting Test Mode...")
    worker = threading.Thread(target=process_event_worker, daemon=True)
    worker.start()
    
    timestamp = int(time.time() * 1000)
    event_queue.put({"timestamp": timestamp, "x": 500, "y": 500, "test_mode": True})
    
    # Wait for processing
    event_queue.join()
    event_queue.put(None)
    worker.join()
    print("Test Mode Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-mode", action="store_true", help="Run a programmatic synthetic test")
    args = parser.parse_args()
    
    if args.test_mode:
        run_test_mode()
    else:
        run_shadow_mode()
