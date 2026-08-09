# Forge OS 🚀

Forge OS is an incredibly fast, entirely local GUI Agent that acts as the physical brain and hands for your PC. 

Originally built as a simple Python wrapper, **Forge has been entirely rewritten in Go** to achieve a true **Zero-RAM footprint** when idle. It combines real-time screen capture, UI Automation (UIA), and localized AI Planning to execute complex multi-step workflows safely and securely on your machine.

## Features ✨
- **Zero-RAM Idle Footprint:** Written in Go, Forge consumes effectively 0MB of RAM when sleeping. It wakes instantly via an OS hook.
- **Two-Tier Hybrid Orchestrator:** 
  - Uses highly robust **Advanced Macros (Skills)** for complex, daily tasks (like "Study Mode" or "AI Messenger").
  - Seamlessly falls back to the dynamic **Qwen 0.5B AI Planner** for novel, unstructured requests.
- **Targeted Safeguards:** Forge actively scans generated execution plans. If it detects a high-risk action (like `delete`, `pay`, `remove`, or `transfer`), it pauses and spawns a native Windows dialog asking for your explicit permission before clicking or typing.
- **Moondream2 Powered Vision:** 100% local, uncensored, and fast screen reasoning using a sub-2B parameter VLM.
- **Bulletproof Security:** Fully local inference. No cloud subscriptions, no data harvesting.

## Architecture 🧠
Forge operates using a highly decoupled architecture:
1. **Hybrid Task Splitter (`pkg/orchestrator` & `pkg/skills`):** Analyzes your intent. If it matches a daily workflow, it routes it to a deterministic Go macro.
2. **AI Planner (`pkg/planner`):** If no skill is matched, the Qwen 0.5B model takes over, generating a sequence of high-level UI abstractions (e.g., `{"type": "click_element", "name": "Send"}`).
3. **Execution & Safeguards (`pkg/executor`):** Evaluates the plan for danger, extracts exact X/Y coordinates via the Windows UIA tree, and executes native Win32 inputs.

## The Skills Library 🛠️
Forge comes pre-loaded with advanced skills that run deterministically:
*   **Study Mode:** Automatically opens Notion, creates a page, launches the Windows Clock, and starts a Focus Session.
*   **AI Messenger:** Seamlessly prompts local/web AI, waits for the response, copies it, and sends it to a contact via WhatsApp.
*   **System Monitor:** Hooks into OS telemetry to provide instant native popups about CPU and RAM usage.
*   **Browser Search:** Instantly opens a browser and executes web searches.

## Installation 📥
1. Clone this repository.
2. Download the models manually (see below).
3. Run `forge.exe`. The background daemon will start instantly.

### Required Models:
To keep this repository lightweight, download the following `.gguf` files into the `models/` directory:
- **Qwen 2.5 (0.5B):** For the AI Planner (`qwen2.5-0.5b-instruct-q4_k_m.gguf`).
- **Moondream2:** For vision processing (`moondream2-text-model-f16_ct-vicuna.gguf` & `mmproj`).

## Disclaimer ⚠️
This system has direct access to your physical mouse and keyboard. While targeted safeguards protect against specific keywords, always supervise the agent during complex dynamic workflows.
