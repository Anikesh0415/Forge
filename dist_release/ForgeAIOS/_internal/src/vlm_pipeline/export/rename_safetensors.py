import os
import gc
import safetensors
from safetensors.torch import safe_open, save_file

def rename_keys(file_path):
    print(f"Loading {file_path}...")
    tensors = {}
    with safe_open(file_path, framework="pt", device="cpu") as f:
        for key in f.keys():
            new_key = key
            if key.startswith("model.visual."):
                new_key = key.replace("model.visual.", "visual.", 1)
            tensors[new_key] = f.get_tensor(key)
    
    print(f"Saving to {file_path}...")
    save_file(tensors, file_path)
    print("Done!")

if __name__ == "__main__":
    rename_keys(r"E:\AIF_Project\src\vlm_pipeline\export\forge_vlm_model_merged\model.safetensors")
