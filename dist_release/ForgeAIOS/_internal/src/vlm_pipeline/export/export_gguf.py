import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
MODEL_DIR = os.path.join(EXPORT_DIR, "forge_vlm_model_merged")
LLAMA_CPP_DIR = os.path.join(BASE_DIR, "llama.cpp")
GGUF_F16_PATH = os.path.join(EXPORT_DIR, "Forge-VLM-v1-f16.gguf")
GGUF_Q4_PATH = os.path.join(EXPORT_DIR, "Forge-VLM-v1-Q4_K_M.gguf")

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(1)

def setup_llama_cpp():
    if not os.path.exists(LLAMA_CPP_DIR):
        print("Cloning llama.cpp...")
        run_cmd(f"git clone https://github.com/ggerganov/llama.cpp.git {LLAMA_CPP_DIR}")
    
    print("Installing llama.cpp python dependencies...")
    run_cmd(f"{sys.executable} -m pip install gguf protobuf sentencepiece")

    # Download prebuilt Intel SYCL binaries for Windows
    build_bin_dir = os.path.join(LLAMA_CPP_DIR, "build", "bin", "Release")
    os.makedirs(build_bin_dir, exist_ok=True)
    
    if not os.path.exists(os.path.join(build_bin_dir, "llama-quantize.exe")):
        print("Downloading prebuilt llama.cpp with Intel SYCL backend...")
        zip_path = os.path.join(LLAMA_CPP_DIR, "llama-sycl.zip")
        # Download the latest SYCL windows release (using b10107 as a known stable one)
        sycl_url = "https://github.com/ggml-org/llama.cpp/releases/download/b10107/llama-b10107-bin-win-sycl-x64.zip"
        run_cmd(f"powershell -Command \"Invoke-WebRequest -Uri '{sycl_url}' -OutFile '{zip_path}'\"")
        print("Extracting...")
        run_cmd(f"powershell -Command \"Expand-Archive -Path '{zip_path}' -DestinationPath '{build_bin_dir}' -Force\"")
        print("✅ Downloaded and extracted llama.cpp with SYCL successfully.")

def convert_to_gguf():
    print(f"Converting HF model at {MODEL_DIR} to GGUF f16...")
    convert_script = os.path.join(LLAMA_CPP_DIR, "convert_hf_to_gguf.py")
    if not os.path.exists(convert_script):
        # newer llama.cpp uses convert-hf-to-gguf.py
        convert_script = os.path.join(LLAMA_CPP_DIR, "convert-hf-to-gguf.py")
        
    run_cmd(f"{sys.executable} {convert_script} {MODEL_DIR} --outfile {GGUF_F16_PATH} --outtype f16")
    print(f"✅ GGUF f16 saved to {GGUF_F16_PATH}")

def quantize_model():
    print(f"Quantizing GGUF to Q4_K_M...")
    quantize_exe = os.path.join(LLAMA_CPP_DIR, "build", "bin", "Release", "llama-quantize.exe")
    if not os.path.exists(quantize_exe):
        quantize_exe = os.path.join(LLAMA_CPP_DIR, "build", "bin", "llama-quantize.exe")
        
    run_cmd(f"{quantize_exe} {GGUF_F16_PATH} {GGUF_Q4_PATH} Q4_K_M")
    print(f"✅ Quantized model saved to {GGUF_Q4_PATH}")

def main():
    print("="*50)
    print("📦 Forge VLM GGUF Packaging Pipeline (Intel SYCL)")
    print("="*50)
    
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Error: Model directory {MODEL_DIR} does not exist. Run Phase 3 training first.")
        sys.exit(1)
        
    setup_llama_cpp()
    convert_to_gguf()
    quantize_model()
    
    print("🎉 Pipeline complete. Final model:", GGUF_Q4_PATH)

if __name__ == "__main__":
    main()
