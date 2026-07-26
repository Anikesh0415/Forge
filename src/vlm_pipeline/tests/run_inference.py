import subprocess
import argparse
import json
import os
import re

# Use the explicitly built SYCL executable
LLAMA_CLI_PATH = r"E:\AIF_Project\src\vlm_pipeline\llama.cpp\build\bin\Release\llama-mtmd-cli.exe"
MODEL_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-Q4_K_M.gguf"
MMPROJ_PATH = r"E:\AIF_Project\src\vlm_pipeline\export\Forge-VLM-v1-mmproj-f16.gguf"

def run_vlm_inference(image_path: str, prompt: str) -> dict:
    """
    Runs the Forge VLM model using llama.cpp with the SYCL backend.
    """
    if not os.path.exists(LLAMA_CLI_PATH):
        raise FileNotFoundError(f"Cannot find llama-mtmd-cli at {LLAMA_CLI_PATH}. Have you built it?")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Cannot find model gguf at {MODEL_PATH}.")
    if not os.path.exists(MMPROJ_PATH):
        raise FileNotFoundError(f"Cannot find mmproj gguf at {MMPROJ_PATH}.")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}.")

    env = os.environ.copy()
    # Explicitly enforce SYCL execution on the Intel Arc iGPU
    env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
    env["ZES_ENABLE_SYSMAN"] = "1"
    env["GGML_SYCL_DEBUG"] = "0"
    
    cmd = [
        LLAMA_CLI_PATH,
        "-m", MODEL_PATH,
        "--mmproj", MMPROJ_PATH,
        "--image", image_path,
        "-p", prompt,
        "-n", "512", # Max generation tokens
        "-c", "8192", # Huge context size to accommodate full HD screenshots
        "-b", "4096", # Increase batch size for image encoding
        "--temp", "0.1" # Low temp for structured Action Plan
    ]
    
    print(f"Running VLM Inference on {image_path}...")
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False # We handle errors manually
        )
    except Exception as e:
        raise RuntimeError(f"Failed to execute llama-mtmd-cli: {e}")
        
    if result.returncode != 0:
        print("--- STDERR ---")
        print(result.stderr)
        raise RuntimeError(f"llama-mtmd-cli failed with exit code {result.returncode}")
        
    output = result.stdout
    
    # We need to extract the JSON output from the stdout. 
    # llama-mtmd-cli prints lots of initialization info, so we look for {...}
    json_match = re.search(r"(\{.*?\})", output, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)
        try:
            # Fix unquoted keys and values (e.g. {action: open_github} -> {"action": "open_github"})
            clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
            clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
            action_plan = json.loads(clean_json)
            return action_plan
        except json.JSONDecodeError:
            # Fallback if it's still not strict JSON
            return {"raw_output": raw_json.strip()}
            
    return {"raw_output": output.strip()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge VLM Inference Wrapper")
    parser.add_argument("--image", required=True, help="Path to the desktop screenshot")
    parser.add_argument("--prompt", default="Analyze this desktop screenshot and output a structured JSON Action Plan.", help="User prompt")
    
    args = parser.parse_args()
    
    try:
        plan = run_vlm_inference(args.image, args.prompt)
        print("\n--- FORGE VLM ACTION PLAN ---")
        print(json.dumps(plan, indent=2))
    except Exception as e:
        print(f"Inference Error: {e}")
