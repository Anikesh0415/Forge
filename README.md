# Forge OS 🚀

Forge OS is an incredibly fast, ultra-lightweight, zero-RAM GUI Agent for Windows that acts as the physical brain and hands for your PC. 

Originally built as a simple Python wrapper, **Forge has been entirely rewritten in Go** to achieve a true **Zero-RAM footprint** when idle. It combines real-time event-driven UI Automation (UIA), native Windows Hooks, local SQLite long-term memory, and localized AI Planning to execute complex multi-step workflows with 100% precision.

---

## Key Features ✨

- ⚡ **Zero-RAM Idle Footprint:** Written in pure Go, Forge consumes effectively 0MB of RAM while sleeping. It wakes instantly when summoned.
- 🔴 **Watch-and-Learn Macro Recorder:** 
  - Press `Ctrl + Shift + R` at any time to record a workflow.
  - Perform your task physically—Forge captures mouse clicks and keystrokes via native Win32 hooks (`user32.dll`).
  - Press `Ctrl + Shift + R` again to compile it into a zero-hallucination `.json` skill with live Windows Toast Notifications.
- 🧠 **Embedded Local SQLite Brain (`brain.db`):** 
  - Uses `modernc.org/sqlite` (pure Go, zero-CGO).
  - Stores long-term user preferences, macro mappings, and execution history without bloating the LLM prompt memory.
- 👁️ **Closed-Loop UIA Perception (`WaitForElement`):** 
  - Powered by Windows `UIAutomationCore.dll`.
  - Replaces fragile blind `Sleep()` delays and `Tab` sequences with event-driven UIA element watchers and direct bounding-box coordinate clicking.
- 🔍 **Pure-Go Fuzzy Matcher Engine:** 
  - Tokenized Levenshtein distance algorithm with typo scoring and penalty safeguards.
  - Handles typos gracefully (e.g. `"play spotfy"` -> `"play spotify"`) while preventing false positives.
- 🛡️ **Targeted Safeguards:** 
  - Forge actively scans generated execution plans. If it detects a high-risk action (like `delete`, `pay`, `remove`, or `transfer`), it pauses and prompts for native user confirmation.
- 🌐 **100% Local & Private:** No cloud subscriptions, no telemetry, no data harvesting.

---

## What's New in Version 2.64 🔥

- 🧠 **Smart Semantic Macro Recorder:** The `Ctrl+Shift+R` recorder is no longer blind! When you click, Forge instantly and asynchronously queries Windows UIA to find the *semantic name* of the element you clicked on (e.g., "Send Button") instead of just saving exact `(X,Y)` coordinates. This means your recorded macros will now work flawlessly even if you resize, minimize, or move your app windows around!

## What's New in Version 2.63 ✨

- 🪟 **Draggable & Minimizable Overlay:** The main Forge floating input window is now fully draggable across the screen and includes a dedicated minimize button. This allows you to smoothly record macros (`Ctrl+Shift+R`) or read text without the bar blocking the center of your screen!

---

## Architecture 🏗️

```
                         +-------------------+
                         |  User Prompt /    |
                         |  Ctrl+Shift+R Rec |
                         +---------+---------+
                                   |
                                   v
                      +-------------------------+
                      | Pure-Go Fuzzy Matcher   |
                      +----+---------------+----+
                           |               |
           [Skill Matched] |               | [No Skill Match]
                           v               v
               +---------------+       +------------------+
               | Native Skill  |       | Qwen 0.5B        |
               | / Learned     |       | Dynamic AI       |
               | Macro (.json) |       | Planner          |
               +-------+-------+       +--------+---------+
                       |                        |
                       +-----------+------------+
                                   |
                                   v
                      +-------------------------+
                      | Event-Driven UIA        |
                      | Closed-Loop Perception  |
                      +------------+------------+
                                   |
                                   v
                      +-------------------------+
                      | Native Win32 Executor   |
                      +-------------------------+
```

---

## The Skills Library 🛠️

Forge includes built-in skills and supports infinitely extendable dynamic skills:
* 🎵 **Spotify Web Player Integration:** Auto-navigates, waits for UIA element load, and executes direct bounding-box clicks on track play buttons.
* 📖 **Study Mode:** Automatically opens Notion, creates a page, launches the Windows Clock, and starts a Focus Session.
* 💬 **AI Messenger:** Prompts local/web AI, waits for the response, copies it, and sends it to a contact via WhatsApp.
* 💻 **System Monitor:** Hooks into OS telemetry to provide instant native popups about CPU and RAM usage.
* 🔴 **Watch-and-Learn Macros:** Any custom multi-step task you demonstrate using `Ctrl + Shift + R` is saved to `skills_db/` as a permanent skill.

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

# Build executable (headless mode)
go build -ldflags="-H windowsgui" -o forge.exe main.go

# Launch Forge
.\forge.exe
```

---

## How to Record a Macro 📹

1. Run `forge.exe`.
2. Press **`Ctrl + Shift + R`**. You will see a Windows Toast notification:  
   `🔴 Started recording macro... Press Ctrl+Shift+R to stop.`
3. Perform your task on your PC (click buttons, type text).
4. Press **`Ctrl + Shift + R`** again.  
   `⏹️ Stopped recording.`  
   `✅ Saved macro: macro_...`
5. The macro is now saved in `skills_db/` and can be triggered anytime via natural language or fuzzy match!

---

## Disclaimer ⚠️

Forge has direct access to your physical mouse and keyboard. While targeted safeguards protect against high-risk keywords, always supervise the agent during dynamic AI execution.
