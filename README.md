# Forge OS 🚀

Forge OS is an incredibly fast, entirely local GUI Agent that acts as the physical brain and hands for your PC. By combining real-time screen capture with the ultra-lightweight Moondream2 Vision-Language Model, Forge OS is capable of observing your screen, planning complex actions using its ARIA Planner, and executing them flawlessly with zero cloud dependencies.

## Features ✨
- **1-Click Boot:** Double click `Start_FORGE_App.bat` and the entire backend, model, and UI boots up instantly.
- **1-Click Stop:** Double click `Stop_FORGE_App.bat` to safely shut down all local inference servers and python runtimes.
- **Moondream2 Powered:** 100% local, uncensored, and fast screen reasoning using a sub-2B parameter VLM running perfectly on standard laptop CPUs.
- **ARIA Planner:** A dedicated intelligence layer that combines Semantic Memory (RAG skills) and Episodic Memory (User preferences) to generate context-aware Action Plans.
- **Bulletproof Security:** Bound strictly to `127.0.0.1`. No external Wi-Fi hijacks possible.

## Installation 🛠️
1. Clone this repository.
2. Download the models manually (see Model Installation below).
3. Run `Start_FORGE_App.bat`.
4. The system will automatically launch the Web UI!

## Model Installation 📥
To keep this repository lightweight, the large model files are not included. You must download them manually into the `models/` directory:

**1. Primary Vision Model (Moondream2):**
- Download `moondream2-text-model-f16_ct-vicuna.gguf` and `moondream2-mmproj-f16-20250414.gguf` from [HuggingFace](https://huggingface.co/vikhyatk/moondream2/tree/main).
- Place both files inside the `models/` folder.

**2. Optional Advanced Planner (Hermes 8B):**
- If you wish to use the advanced `ARIA Planner` with a local 8B model instead of Moondream2, download [Hermes-2-Pro-Llama-3-8B-GGUF](https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B-GGUF).
- Place the `.gguf` file in the `models/` folder and configure `aria_planner.py` to point to it.

## Architecture 🧠
Forge operates on a highly decoupled node system:
1. **Semantic/Episodic Memory:** Retrieves user facts and skills.
2. **ARIA Planner:** Reads the screen and memory to generate a structured JSON Plan.
3. **Execution Manager:** Translates JSON coordinates into physical PyAutoGUI mouse clicks.

## Disclaimer ⚠️
This system has direct access to your physical mouse and keyboard. Always supervise the agent during complex workflows. Ensure no sensitive windows are active during execution.
