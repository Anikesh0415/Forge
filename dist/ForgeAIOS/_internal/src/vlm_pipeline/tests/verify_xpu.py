import torch

if __name__ == "__main__":
    if torch.xpu.is_available():
        print(f"✅ SUCCESS: Intel XPU (Arc iGPU) is available! Found {torch.xpu.device_count()} device(s).")
        for i in range(torch.xpu.device_count()):
            print(f"Device {i}: {torch.xpu.get_device_name(i)}")
    else:
        print("❌ ERROR: Intel XPU is NOT available. Please check drivers or installation.")
