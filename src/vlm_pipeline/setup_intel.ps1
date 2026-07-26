Write-Host "Installing PyTorch for Intel XPU..."
.\venv\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu

Write-Host "Installing other dependencies..."
.\venv\Scripts\pip.exe install transformers pillow pydantic pyautogui datasets

Write-Host "Cloning and installing Unsloth for Intel GPU..."
if (-not (Test-Path "unsloth")) {
    git clone https://github.com/unslothai/unsloth.git
}
cd unsloth
..\venv\Scripts\pip.exe install -e ".[intel-gpu]"
cd ..

Write-Host "Done setting up environment!"
