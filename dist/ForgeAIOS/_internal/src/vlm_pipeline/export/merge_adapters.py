import torch
from peft import PeftModel
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

def main():
    print("Loading base Qwen2-VL model on CPU...")
    # Load the base model natively
    base_model = Qwen2VLForConditionalGeneration.from_pretrained(
        "unsloth/Qwen2-VL-2B-Instruct",
        device_map="cpu",
        torch_dtype=torch.float16,
    )
    
    print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(
        base_model,
        "E:/AIF_Project/src/vlm_pipeline/export/forge_vlm_model"
    )
    
    print("Merging adapters into base weights...")
    merged_model = model.merge_and_unload()
    
    print("Saving full merged model and processor...")
    merged_model.save_pretrained("E:/AIF_Project/src/vlm_pipeline/export/forge_vlm_model_merged")
    
    processor = AutoProcessor.from_pretrained("E:/AIF_Project/src/vlm_pipeline/export/forge_vlm_model")
    processor.save_pretrained("E:/AIF_Project/src/vlm_pipeline/export/forge_vlm_model_merged")
    print("✅ Merging complete!")

if __name__ == "__main__":
    main()
