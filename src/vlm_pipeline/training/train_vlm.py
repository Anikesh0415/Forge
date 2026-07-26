import os
import json
import torch
from unsloth import FastVisionModel, is_bfloat16_supported
from unsloth import UnslothVisionDataCollator
from datasets import load_dataset, Dataset
import datasets
datasets.disable_caching()

# Monkeypatch datasets fingerprinting to bypass dill crash on Python 3.14
import datasets.fingerprint
datasets.fingerprint.generate_fingerprint = lambda *args, **kwargs: "dummy_fingerprint_12345"
datasets.fingerprint.Hasher.hash = lambda *args, **kwargs: "dummy_hash_12345"
datasets.fingerprint.Hasher.hash_bytes = lambda *args, **kwargs: "dummy_hash_bytes_12345"

from trl import SFTTrainer, SFTConfig

# Paths
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")
JSONL_FILE = os.path.join(DATASET_DIR, "forge_vlm_data.jsonl")
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "export", "forge_vlm_model")

def format_dataset(jsonl_path):
    """Loads and formats the JSONL dataset for Qwen2-VL training."""
    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"Dataset not found at {jsonl_path}")
        
    data = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            entry = json.loads(line)
            # Fix relative image paths to absolute paths
            for msg in entry["messages"]:
                if isinstance(msg["content"], str):
                    msg["content"] = [{"type": "text", "text": msg["content"]}]
                if isinstance(msg["content"], list):
                    for item in msg["content"]:
                        if item["type"] == "image":
                            # Make path absolute
                            item["image"] = os.path.join(DATASET_DIR, item["image"])
            data.append(entry)
            
    # Save to temp JSONL and load via HuggingFace to avoid Python 3.14 dill pickle bug
    tmp_path = jsonl_path + ".tmp.jsonl"
    with open(tmp_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
            
    return load_dataset("json", data_files=tmp_path, split="train")

def main():
    print("="*50)
    print("🚀 Forge VLM Unsloth QLoRA Training Engine")
    print("="*50)
    
    # 1. Load Model & Tokenizer
    model_name = "unsloth/Qwen2-VL-2B-Instruct"
    print("Loading unsloth/Qwen2-VL-2B-Instruct in 16-bit precision...")
    model, tokenizer = FastVisionModel.from_pretrained(
        model_name="unsloth/Qwen2-VL-2B-Instruct",
        load_in_4bit=False, # Disable 4-bit to bypass bitsandbytes/Triton compilation on Windows without MSVC
        use_gradient_checkpointing="unsloth",
    )
    
    # 2. Add LoRA Adapters
    print("Configuring QLoRA Adapters...")
    model = FastVisionModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj", 
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        finetune_vision_layers=False,
        finetune_language_layers=True,
        random_state=3407,
    )
    
    FastVisionModel.for_training(model)
    
    # 3. Prepare Dataset
    print("Loading dataset...")
    dataset = format_dataset(JSONL_FILE)
    
    # 4. Configure Trainer
    print("Initializing Trainer...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=UnslothVisionDataCollator(model, tokenizer),
        train_dataset=dataset,
        dataset_text_field="messages", # Bypass validation by providing a valid column
        dataset_kwargs={"skip_prepare_dataset": True},
        args=SFTConfig(
            dataset_text_field="messages",
            dataset_kwargs={"skip_prepare_dataset": True},
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            remove_unused_columns=False,
            optim="adamw_torch", # Force standard PyTorch optimizer to avoid bitsandbytes Triton kernels
            warmup_steps=5,
            max_steps=30, # For testing. Change to num_train_epochs=3 for real training.
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir="outputs",
            report_to="none",
        ),
    )
    
    # 5. Train
    print("Starting Training...")
    trainer.train()
    
    # 6. Export Model
    print(f"Saving MERGED fine-tuned model to {EXPORT_DIR}...")
    model.save_pretrained_merged(EXPORT_DIR, tokenizer, save_method="merged_16bit")
    print("✅ Training and export complete!")

if __name__ == "__main__":
    main()
