import os
from huggingface_hub import hf_hub_download

repo_id = "Qwen/Qwen2.5-3B-Instruct-GGUF"
filename = "qwen2.5-3b-instruct-q4_k_m.gguf"
local_dir = r"E:\AIF_Project\models"

print(f"Downloading {filename} from {repo_id}...")
print("This may take several minutes depending on your internet connection.")

try:
    os.makedirs(local_dir, exist_ok=True)
    downloaded_path = hf_hub_download(
        repo_id=repo_id, 
        filename=filename, 
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
    print(f"\nSuccess! Model downloaded to: {downloaded_path}")
except Exception as e:
    print(f"\nError downloading model: {e}")
