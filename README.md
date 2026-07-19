# Servent-AI: Action Intelligence Framework (AIF)

Servent-AI is a 100% local, privacy-first Windows OS automation agent. It enables users to control their operating systems entirely hands-free using natural voice commands and real-time hand gestures. By utilizing local reasoning models (Hermes 2 Pro) and vision models (Moondream), Servent-AI autonomously plans and executes complex, multi-step actions on your computer, verifying the visual state of the screen at every step.

This framework is built with **accessibility** at its heart, providing physically challenged or motor-impaired individuals a way to fully operate their computers, write code, and build digital careers independently.

---

## Key Features

* **🎤 Hands-Free Voice Control:** Uses local OpenAI Whisper models to transcribe voice commands (e.g. *"open Gemini, write a letter, and send it to my friend on WhatsApp"*).
* **🖐️ Real-Time Gesture Tracking:** Tracks hand coordinates and finger curls using MediaPipe to control mouse cursor movement, clicks, and page scrolling.
* **🧠 Aria Planning Brain:** Uses **Hermes 2 Pro 8B** (via LM Studio) to convert abstract voice instructions into structured, step-by-step JSON plan arrays.
* **👁️ VISTA Visual Verification:** Automatically captures screenshots and queries a local **Moondream** vision model to verify whether a page loaded or a loading animation has finished before proceeding.
* **📚 Skill Library (RAG):** Dynamically injects context-specific examples into the prompt to prevent hallucination without breaking context limits.
* **🪄 Semantic Copy & OCR Clicking:** Uses PyTesseract for native OCR-based clicking and leverages Hermes to semantically extract and clean messy clipboard data in real-time.
* **⚡ Native Accessibility & DOM Snapshotting:** Uses UIAutomation to instantaneously click desktop buttons and rips real-time DOM snapshots for perfect-context error recovery replanning.
* **🔒 100% Local & Private:** No APIs, no cloud dependencies, no paywalls, and completely offline. Your data never leaves your machine.

---

## Architecture Flow

```mermaid
graph TD
    User(("🗣️ User Request")) --> UI["💻 Ecosystem Control Center"]
    UI --> Planner{"🧠 ARIA Planner\n(Hermes 8B)"}
    SkillDB[("📚 Skill Library\n(RAG / skills.json)")] -.->|Injects Examples| Planner
    
    Planner -->|JSON Action Plan| AgentLoop(("⚙️ Central Agent Loop"))
    
    AgentLoop -->|Execute| ExecMgr["⚡ Execution Manager\n(PyAutoGUI / PyTesseract)"]
    AgentLoop -->|Verify| VistaWait["👁️ VISTA Moondream\n(smart_wait_for_completion)"]
    
    VistaWait -.->|Wait Condition Met ✓| AgentLoop
    
    ExecMgr --> TargetApp["🖥️ Target App\n(WhatsApp, Web, etc.)"]
    
    ExecMgr --> OCRClick["👀 OCR click_text"]
    OCRClick --> TargetApp
    
    ExecMgr --> SemanticCopy["🪄 Semantic Copy"]
    SemanticCopy --> HermesFilter{"🧹 Hermes LLM\nData Cleaner"}
    HermesFilter --> TargetApp
```

---

## Prerequisites & Installation

### 1. Set Up Local Models
* **LM Studio:** Download and run [LM Studio](https://lmstudio.ai/). Load **`Hermes-2-Pro-Llama-3-8B-GGUF`** (or a similar function-calling model) and start the local API server on port `1234`.
* **Ollama:** Install [Ollama](https://ollama.com/) and run the following in your terminal to pull the visual model:
  ```bash
  ollama pull moondream
  ```

### 2. Install Tesseract OCR
For the visual `click_text` capabilities to work, you must install Tesseract:
* **Windows:** Download and install the [Tesseract-OCR executable](https://github.com/UB-Mannheim/tesseract/wiki). Ensure the installation path is added to your Windows Environment Variables.

### 3. Install Project Dependencies
1. Clone the repository:
   ```bash
   git clone https://github.com/Anikesh0415/Servent-AI.git
   cd Servent-AI
   ```
2. Activate your virtual environment and install dependencies:
   ```bash
   .\venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytesseract pyperclip
   ```

---

## Usage

1. Start your local model servers (LM Studio on port `1234` and Ollama on port `11434`).
2. Run the bootstrapper script:
   ```bash
   Start_Ecosystem.bat
   ```
3. Open the locally served dashboard at `ui/index.html`.
4. Speak a command (e.g., *"open Gemini, ask for a letter, and copy it..."*) or use hand gestures to control the cursor!

---

## Contributing & License
Distributed under the MIT License. Feel free to open issues and pull requests to help make computing accessible for everyone!
