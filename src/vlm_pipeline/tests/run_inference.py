import subprocess
import argparse
import json
import os
import sys
import re
import urllib.request
import base64


def get_project_root() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    curr = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(curr, "..", "..", ".."))

PROJECT_ROOT = get_project_root()

def find_file(relative_paths: list) -> str:
    for rel in relative_paths:
        full = os.path.join(PROJECT_ROOT, rel)
        if os.path.exists(full):
            return full
        if getattr(sys, 'frozen', False):
            bundle_dir = getattr(sys, '_MEIPASS', PROJECT_ROOT)
            full_bundle = os.path.join(bundle_dir, rel)
            if os.path.exists(full_bundle):
                return full_bundle
    return os.path.join(PROJECT_ROOT, relative_paths[0])

LLAMA_CLI_PATH = find_file([
    os.path.join("bin", "llama-mtmd-cli.exe"),
    os.path.join("bin", "llama-server.exe"),
    os.path.join("src", "vlm_pipeline", "llama.cpp", "build", "bin", "Release", "llama-mtmd-cli.exe"),
    os.path.join("src", "vlm_pipeline", "llama.cpp", "build", "bin", "Release", "llama-server.exe"),
])

MODEL_PATH = find_file([
    os.path.join("src", "vlm_pipeline", "export", "Forge-VLM-v1-Q4_K_M.gguf"),
])

MMPROJ_PATH = find_file([
    os.path.join("src", "vlm_pipeline", "export", "Forge-VLM-v1-mmproj-f16.gguf"),
])

QWEN_PLANNER_MODEL_PATH = find_file([
    os.path.join("models", "qwen2.5-3b-instruct-q4_k_m.gguf"),
    os.path.join("models", "Qwen2.5-3B-Instruct-Q4_K_M.gguf"),
])

GRAMMAR_PATH = find_file([
    os.path.join("src", "vlm_pipeline", "tests", "action.gbnf")
])

def try_server_inference(image_path: str, prompt: str, port: int = 8080) -> dict:
    """Attempts VLM inference via llama-server HTTP endpoint."""
    health_url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=1) as resp:
            if resp.status != 200:
                return None
    except Exception:
        return None

    # Server is healthy, send completions request
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        chat_url = f"http://127.0.0.1:{port}/v1/chat/completions"
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You are a robotic GUI agent. You must output ONLY a valid JSON action plan. Do not include conversational text or markdown formatting.\n\n" + prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }
            ],
            "max_tokens": 512,
            "temperature": 0.3,
            "frequency_penalty": 0.5,
            "response_format": {"type": "json_object"}
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(chat_url, data=data_bytes, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            content = res_json["choices"][0]["message"]["content"]
            
            # Extract JSON action plan
            json_match = re.search(r"(\{.*?\})", content, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1)
                try:
                    clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
                    clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
                    return json.loads(clean_json)
                except Exception:
                    return {"raw_output": raw_json.strip()}
            return {"raw_output": content.strip()}
    except Exception as e:
        print(f"[run_vlm_inference] HTTP inference call failed: {e}")
        return None


def try_text_server_inference(prompt: str, port: int = 8080) -> dict:
    """Attempts Text inference via llama-server HTTP endpoint to avoid GPU deadlock."""
    health_url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=1) as resp:
            if resp.status != 200:
                return None
    except Exception:
        return None

    try:
        chat_url = f"http://127.0.0.1:{port}/v1/chat/completions"
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
            "frequency_penalty": 0.5,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(chat_url, data=data_bytes, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            content = res_json["choices"][0]["message"]["content"]
            
            # Extract JSON plan
            json_match = re.search(r"(\[.*\])", content, re.DOTALL)
            if not json_match:
                json_match = re.search(r"(\{.*?\})", content, re.DOTALL)
                
            if json_match:
                raw_json = json_match.group(1)
                try:
                    clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
                    clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
                    return json.loads(clean_json)
                except Exception:
                    return {"raw_output": raw_json.strip()}
            return {"raw_output": content.strip()}
    except Exception as e:
        print(f"[run_text_inference] HTTP inference call failed: {e}")
        return None

def run_text_inference(prompt: str, grammar_file: str = None) -> dict:
    """
    Runs the text model (e.g. Qwen2.5-3B) using llama-server HTTP or CLI.
    """
    srv_res = try_text_server_inference(prompt)
    if srv_res is not None:
        return srv_res
        
    cli_path = LLAMA_CLI_PATH
    model_path = QWEN_PLANNER_MODEL_PATH

    if not os.path.exists(cli_path):
        raise FileNotFoundError(f"Cannot find llama CLI executable at {cli_path}.")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Cannot find Planner model gguf at {model_path}. Please download Qwen2.5-3B-Instruct-Q4_K_M.gguf.")

    env = os.environ.copy()
    env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
    env["ZES_ENABLE_SYSMAN"] = "1"
    env["GGML_SYCL_DEBUG"] = "0"
    
    cmd = [
        cli_path,
        "-m", model_path,
        "-p", prompt,
        "-n", "1024",
        "-c", "4096",
        "-b", "512",
        "--temp", "0.1",
        "--repeat-penalty", "1.15"
    ]
    
    if grammar_file and os.path.exists(grammar_file):
        cmd.extend(["--grammar-file", grammar_file])
    
    print(f"Running Text Inference via CLI...")
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        raise RuntimeError(f"Failed to execute llama CLI: {e}")
        
    output = result.stdout
    
    # Extract JSON array [] from output
    json_match = re.search(r"(\[.*\])", output, re.DOTALL)
    if not json_match:
        # fallback to {}
        json_match = re.search(r"(\{.*?\})", output, re.DOTALL)
        
    if json_match:
        raw_json = json_match.group(1)
        try:
            clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
            clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
            action_plan = json.loads(clean_json)
            return action_plan
        except json.JSONDecodeError:
            return {"raw_output": raw_json.strip()}
            
    return {"raw_output": output.strip()}

def run_vlm_inference(image_path: str, prompt: str) -> dict:
    """
    Runs the Forge VLM model using llama.cpp with SYCL backend or llama-server HTTP API.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}.")


    # 1. Try llama-server HTTP inference first if running
    srv_res = try_server_inference(image_path, prompt)
    if srv_res is not None:
        return srv_res

    # 2. Fall back to CLI execution
    cli_path = LLAMA_CLI_PATH
    model_path = MODEL_PATH
    mmproj_path = MMPROJ_PATH

    if not os.path.exists(cli_path):
        raise FileNotFoundError(f"Cannot find llama CLI executable at {cli_path}.")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Cannot find model gguf at {model_path}.")
    if not os.path.exists(mmproj_path):
        raise FileNotFoundError(f"Cannot find mmproj gguf at {mmproj_path}.")

    env = os.environ.copy()
    env["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
    env["ZES_ENABLE_SYSMAN"] = "1"
    env["GGML_SYCL_DEBUG"] = "0"
    
    cmd = [
        cli_path,
        "-m", model_path,
        "--mmproj", mmproj_path,
        "--image", image_path,
        "-p", prompt,
        "-n", "512",
        "-c", "2048",
        "-b", "512",
        "--temp", "0.3",
        "--repeat-penalty", "1.15",
        "--image-min-tokens", "1024"
    ]
    
    print(f"Running VLM Inference on {image_path} via CLI...")
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        raise RuntimeError(f"Failed to execute llama CLI: {e}")
        
    if result.returncode != 0:
        print("--- STDERR ---")
        print(result.stderr)
        raise RuntimeError(f"llama CLI failed with exit code {result.returncode}")
        
    output = result.stdout
    
    json_match = re.search(r"(\{.*?\})", output, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)
        try:
            clean_json = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', raw_json)
            clean_json = re.sub(r'(:\s*)([a-zA-Z0-9_]+)(\s*[,}])', r'\1"\2"\3', clean_json)
            action_plan = json.loads(clean_json)
            return action_plan
        except json.JSONDecodeError:
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
