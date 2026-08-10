# Forge OS 🚀

Forge OS is an incredibly fast, ultra-lightweight, zero-RAM GUI Agent for Windows that acts as the physical brain and hands for your PC.

Written entirely in **pure Go**, Forge achieves a true **Zero-RAM footprint** when idle. It combines real-time event-driven UI Automation (UIA), native Windows Hooks, local SQLite long-term memory, localized AI Planning, remote Telegram control, offline voice input, and a live glassmorphism HUD — all with zero cloud dependencies.

---

## Key Features ✨

- ⚡ **Zero-RAM Idle Footprint:** Pure Go binary — consumes effectively 0 MB of RAM while sleeping. Wakes instantly when summoned.
- 📡 **Telegram Remote Control:** Send natural language commands to Forge from anywhere in the world via your Telegram bot. Forge authenticates by Chat ID and sends back a reply with the result.
- 🎙️ **Offline Voice Push-to-Talk (`Ctrl+Shift+V`):** Speak and Forge listens — entirely offline using Windows SAPI (Speech Recognition). Zero network calls, zero cloud APIs, fully private.
- 🖥️ **Live Glassmorphism HUD Overlay:** A sleek bottom-right progress panel appears during every multi-step orchestration run — showing step number, progress bar fill, and action label with smooth fade-in/out animations.
- 🔴 **Watch-and-Learn Macro Recorder (`Ctrl+Shift+R`):** Record any workflow by performing it once. Forge captures mouse clicks and keystrokes via native Win32 hooks (`user32.dll`) and compiles it into a zero-hallucination `.json` skill.
- 🧠 **Embedded Local SQLite Brain (`brain.db`):** Uses `modernc.org/sqlite` (pure Go, zero-CGO). Stores long-term user preferences, macro mappings, and execution history.
- 👁️ **Closed-Loop UIA Perception (`WaitForElement`):** Powered by Windows `UIAutomationCore.dll`. Replaces fragile `Sleep()` delays with event-driven UIA element watchers and direct bounding-box coordinate clicking.
- 🔍 **Pure-Go Fuzzy Matcher Engine:** Tokenized Levenshtein distance algorithm with typo scoring and penalty safeguards. Handles typos gracefully (e.g. `"play spotfy"` → `"play spotify"`).
- 🛡️ **Targeted Safeguards:** Forge actively scans generated execution plans. If it detects a high-risk action (like `delete`, `pay`, `remove`, or `transfer`), it pauses and prompts for native user confirmation.
- 🌐 **100% Local & Private:** No cloud subscriptions, no telemetry, no data harvesting.

---

## What's New in Version 2.80 🚀

### 📡 Telegram Remote Control
A background Goroutine connects to the Telegram Bot API using long-polling. Set two environment variables and your phone becomes a remote control for your entire PC:
```bash
$env:TELEGRAM_BOT_TOKEN = "your-bot-token"
$env:TELEGRAM_CHAT_ID   = "your-chat-id"
.\forge.exe
```
Send any natural language command (e.g. *"open spotify and play lo-fi"*) and Forge executes it and replies with the result. Authentication is enforced by Chat ID — only you can control your machine.

### 🎙️ Offline Voice Push-to-Talk
Forge now listens for voice commands using Windows SAPI — completely offline, no Whisper, no OpenAI, no internet. The `pkg/voice` package handles:
- A mock-injection interface for unit testing (zero microphone needed in CI)
- A PowerShell SAPI fallback for maximum Windows compatibility
- `SetIntentHandler` wire-up so voice → planner → executor is a seamless pipeline

### 🖥️ Live Glassmorphism HUD Overlay
The old balloon tooltip notification has been replaced with a full WPF overlay window featuring:
- **Dark glassmorphism panel** (`#E0111111` background) pinned to the bottom-right corner
- **Teal progress bar** (`#00D4AA`) that fills step-by-step (e.g. `[3/15]`)
- **Animated status dot** in teal next to the current step label
- **Smooth fade-in / fade-out** — 250ms in, 300ms out, auto-dismisses after 2.5 seconds

---

## Architecture 🏗️

```
         +----------------------------------------------+
         |  Input Sources                               |
         |  ┌─────────────┐ ┌───────────┐ ┌─────────┐  |
         |  │ WPF Prompt  │ │ Telegram  │ │  Voice  │  |
         |  │ (keyboard)  │ │ (remote)  │ │  SAPI   │  |
         |  └──────┬──────┘ └─────┬─────┘ └────┬────┘  |
         +─────────┼──────────────┼─────────────┼───────+
                   └──────────────┼─────────────┘
                                  │
                                  v
                   +─────────────────────────────+
                   │   DispatchIntent() Router   │
                   +──────────┬──────────────────+
                              │
               ┌──────────────┴──────────────┐
               │                             │
    [Skill Matched]                  [No Skill Match]
               │                             │
               v                             v
   +───────────────────+         +──────────────────────+
   │  Native Skill /   │         │  Qwen 0.5B Dynamic   │
   │  Learned Macro    │         │  AI Planner           │
   │  (.json)          │         +──────────┬───────────+
   +─────────┬─────────+                    │
             │                              │
             └──────────────┬───────────────┘
                            │
                            v
               +────────────────────────+
               │   Live HUD Overlay     │
               │   (Step X / 15 bar)    │
               +────────────┬───────────+
                            │
                            v
               +────────────────────────+
               │  Event-Driven UIA      │
               │  Closed-Loop Perception│
               +────────────┬───────────+
                            │
                            v
               +────────────────────────+
               │  Native Win32 Executor │
               +────────────────────────+
```

---

## The Skills Library 🛠️

Forge includes built-in skills and supports infinitely extendable dynamic skills:

- 📡 **Telegram Remote:** Control your PC from anywhere via Telegram bot messages.
- 🎙️ **Voice Commands:** Speak to Forge offline via `Ctrl+Shift+V` — no internet required.
- 🎵 **Spotify Web Player:** Auto-navigates, waits for UIA element load, and executes direct bounding-box clicks on track play buttons.
- 📖 **Study Mode:** Automatically opens Notion, creates a page, launches the Windows Clock, and starts a Focus Session.
- 💬 **AI Messenger:** Prompts local/web AI, waits for the response, copies it, and sends it to a contact via WhatsApp.
- 💻 **System Monitor:** Hooks into OS telemetry to provide instant native popups about CPU and RAM usage.
- 🌐 **600+ Dynamic Search Macros:** Native support across 200+ platforms (YouTube, Amazon, Reddit, GitHub, ChatGPT, etc.).
- 🔴 **Watch-and-Learn:** Any task you demonstrate with `Ctrl+Shift+R` is saved to `skills_db/` as a permanent skill.

---

## Getting Started 📥

### 1. Requirements
- Windows 10/11 (64-bit)
- Go 1.20+ (if building from source)

### 2. Required Models
Download the following `.gguf` files into the `models/` directory for dynamic fallback planning:
- **Qwen 2.5 (0.5B):** `qwen2.5-0.5b-instruct-q4_k_m.gguf`
- **Moondream2 (Optional Vision):** `moondream2-text-model-f16_ct-vicuna.gguf` & `mmproj`

### 3. Build & Run
```bash
# Clone the repository
git clone https://github.com/Anikesh0415/Forge.git
cd Forge

# Build executable
go build -ldflags="-H windowsgui" -o forge.exe main.go

# Launch Forge
.\forge.exe
```

### 4. Enable Telegram Remote (Optional)
```powershell
# Set your Telegram bot credentials (get a bot token from @BotFather)
$env:TELEGRAM_BOT_TOKEN = "123456:ABC-DEF..."
$env:TELEGRAM_CHAT_ID   = "987654321"
.\forge.exe
```

---

## How to Record a Macro 📹

1. Run `forge.exe`.
2. Press **`Ctrl + Shift + R`**. A HUD notification appears:  
   `🔴 Started recording macro... Press Ctrl+Shift+R to stop.`
3. Perform your task on your PC (click buttons, type text).
4. Press **`Ctrl + Shift + R`** again.  
   `✅ Saved macro: macro_...`
5. The macro is now saved in `skills_db/` and can be triggered anytime via natural language or fuzzy match!

---

## Disclaimer ⚠️

Forge has direct access to your physical mouse and keyboard. While targeted safeguards protect against high-risk keywords, always supervise the agent during dynamic AI execution.
