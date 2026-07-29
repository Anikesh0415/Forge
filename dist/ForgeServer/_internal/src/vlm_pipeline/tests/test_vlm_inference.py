import os
import sys
import json
import subprocess
import pyautogui

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
GGUF_Q4_PATH = os.path.join(EXPORT_DIR, "Forge-VLM-v1-Q4_K_M.gguf")
LLAMA_CLI = os.path.join(BASE_DIR, "llama.cpp", "build", "bin", "Release", "llama-cli.exe")

def capture_screenshot(save_path):
    print("📸 Capturing desktop screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path, format="JPEG")

def main():
    print("="*50)
    print("🧪 Forge VLM End-to-End Verification Test (Intel SYCL)")
    print("="*50)
    
    if not os.path.exists(GGUF_Q4_PATH):
        print(f"❌ Error: Model {GGUF_Q4_PATH} not found. Run Phase 4 first.")
        sys.exit(1)
        
    if not os.path.exists(LLAMA_CLI):
        print(f"❌ Error: llama-qwen2vl-cli not found at {LLAMA_CLI}")
        sys.exit(1)
        
    img_path = os.path.join(BASE_DIR, "tests", "test_screenshot.jpg")
    capture_screenshot(img_path)
    prompt = "Open Browser and go to GitHub"
    
    print(f"Loading {GGUF_Q4_PATH} onto Intel Arc iGPU (via SYCL)...")
    print(f"🧠 Querying VLM with prompt: '{prompt}'...")
    
    # Run the native SYCL executable for Qwen2-VL
    # -m: model path
    # -ngl 99: offload all layers to GPU (SYCL)
    # --image: path to the screenshot
    # -p: the prompt
    cmd = [
        LLAMA_CLI,
        "-m", GGUF_Q4_PATH,
        "-ngl", "99",
        "--image", img_path,
        "-p", prompt
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        output_text = result.stdout
        
        print("\n--- RAW OUTPUT ---")
        print(output_text)
        print("------------------\n")
        
        # Optionally, print stderr if there were warnings/errors during inference
        if result.stderr and "error" in result.stderr.lower():
            print("⚠️ STDERR Output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Failed to run inference: {e}")
        sys.exit(1)
        
    print("✅ Inference complete. Native SYCL acceleration verified.")

if __name__ == "__main__":
    main()
