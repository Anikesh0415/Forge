import sys
import os
import threading
import time
import math
import numpy as np
import pyautogui
import asyncio
import websockets
import json
import re
import keyboard

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.stt_module import SpeechRecognizer
from src.fsm_module import AIF_StateMachine, SystemState
from src.fusion_engine import FusionEngine
from src.agent_loop import execute_react_loop, execute_task_plan, plan_task, memory_mgr
from src.action_library import type_action, key_action
from src.context_manager import ContextManager
from src.execution_manager import ExecutionManager
from src.security import SecurityManager
from src.logger import logger
from src.event_bus import event_bus
from src.utils.migrate_memory import migrate_skills
from src.config import WAKE_WORDS, NOISE_GATE_THRESHOLD
from src.tts_module import tts_manager

_server_instance = None

# Global Killswitch Listener
def _global_killswitch_handler():
    print("\n[KILLSWITCH] ESC/Ctrl+E pressed! Halting PyAutoGUI instantly...")
    pyautogui.FAILSAFE = True
    # Moving mouse to corner triggers failsafe exception in pyautogui immediately
    try:
        pyautogui.moveTo(0, 0, duration=0)
    except Exception:
        pass

    try:
        memory_mgr.abort_flag = True
    except Exception:
        pass

    global _server_instance
    if _server_instance is not None:
        try:
            _server_instance.fsm.transition(SystemState.IDLE)
            _server_instance.fsm.current_context["reply_text"] = "🛑 TASK ABORTED BY KILL-SWITCH!"
        except Exception:
            pass

# Bind killswitch
try:
    keyboard.add_hotkey('esc', _global_killswitch_handler)
    keyboard.add_hotkey('ctrl+e', _global_killswitch_handler)
except Exception as e:
    print(f"Keyboard listener binding warning: {e}")

class AIF_Server:
    def __init__(self):
        print("Initializing AIF Headless Server...")
        global _server_instance
        _server_instance = self

        migrate_skills()
        self.fsm = AIF_StateMachine()
        self.stt = SpeechRecognizer(noise_threshold=NOISE_GATE_THRESHOLD)
        self.fusion = FusionEngine()
        
        # Core Architectural Managers
        self.context_mgr = ContextManager()
        self.memory_mgr = memory_mgr
        self.exec_mgr = ExecutionManager()
        self.security_mgr = SecurityManager(safe_mode=True)
        logger.info("AIF Server initialized with Context, Memory, Execution, and Security Managers.")
        
        self.latest_gesture_coords = None
        self.listening_thread = None
        self.is_listening_mode = False  # Boot in Standby mode
        self.is_tracking_mode = False   # Boot in Standby mode
        
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # CRITICAL: Fixes the massive 10 FPS lag cap
        self.screen_w, self.screen_h = pyautogui.size()
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 3  # Reduced smoothing for much faster, snappier cursor response
        self.is_pinching = False
        
        # Dwell-Clicking state
        self.dwell_start_time = None
        self.dwell_threshold = 0.6  # 600ms default
        self.last_dwell_x = 0
        self.last_dwell_y = 0
        
        self.connected_clients = set()
        self.hand_data_for_ui = []

        self.mode = "BOTH"
        self.is_dictating = False
        self.is_meeting = False
        self.dictation_thread = None
        
        # Start continuous STT worker
        self.stt_thread = threading.Thread(target=self._stt_worker, daemon=True)
        self.stt_thread.start()
        
        self.chat_history_file = os.path.join(os.path.dirname(__file__), "chat_history.json")
        self.chat_history = self._load_history()

        event_bus.subscribe("update_noise_gate", self.on_noise_gate_update)
        
    def on_noise_gate_update(self, threshold: float):
        self.stt.noise_threshold = threshold
        logger.info(f"Noise gate updated to {threshold}")

    def _load_history(self):
        if os.path.exists(self.chat_history_file):
            try:
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def append_to_history(self, sender, text):
        if not text:
            return
        self.chat_history.append({"sender": sender, "text": text})
        # Keep only last 100 messages to prevent massive bloat
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]
        try:
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f)
        except Exception as e:
            print(f"Failed to save history: {e}")
            
        import asyncio
        if hasattr(self, 'connected_clients') and self.connected_clients:
            msg = json.dumps({"type": "CHAT_HISTORY", "history": self.chat_history})
            for client in list(self.connected_clients):
                try:
                    if hasattr(self, 'loop') and self.loop:
                        asyncio.run_coroutine_threadsafe(client.send(msg), self.loop)
                except Exception as e:
                    print(f"WS push error: {e}")

    def _toggle_site_blocking(self, block: bool):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        blocked_sites = ["www.youtube.com", "youtube.com", "www.twitter.com", "twitter.com", "www.reddit.com", "reddit.com", "www.facebook.com", "facebook.com"]
        redirect_ip = "127.0.0.1"
        
        try:
            with open(hosts_path, 'r') as f:
                lines = f.readlines()
                
            if block:
                # Add blocks if not present
                with open(hosts_path, 'a') as f:
                    for site in blocked_sites:
                        if not any(site in line for line in lines):
                            f.write(f"{redirect_ip} {site}\n")
                print("Focus Mode: Distracting sites blocked in hosts file.")
            else:
                # Remove blocks
                with open(hosts_path, 'w') as f:
                    for line in lines:
                        if not any(site in line for site in blocked_sites) or line.strip() == "":
                            f.write(line)
                print("Focus Mode: Distracting sites unblocked.")
        except PermissionError:
            print("[Warning] Could not modify hosts file. Please run the server as Administrator for OS-level distraction blocking.")
        except Exception as e:
            print(f"Error toggling site blocking: {e}")


    def _stt_worker(self):
        while True:
            if self.mode in ["BOTH", "VOICE_ONLY"]:
                if self.fsm.state == SystemState.IDLE:
                    text = self.stt.listen()
                    if text:
                        if self.is_dictating:
                            print(f"Dictating: {text}")
                            # Immediately type what is spoken and press enter
                            type_action(text)
                            time.sleep(0.1)
                            key_action('enter')
                        else:
                            self.fsm.current_context["voice_text"] = text
                            if any(ww.lower() in text.lower() for ww in WAKE_WORDS):
                                print(f"Wake word detected! Intent: {text}")
                                self.fsm.transition(SystemState.PROCESSING_INTENT)
            time.sleep(0.1)



    def process_state(self):
        if self.fsm.state == SystemState.IDLE:
            # Clear old context to prevent UI duplication bugs
            self.fsm.current_context["voice_text"] = ""
            self.fsm.current_context["autonomous_goal"] = ""
            pass
        elif self.fsm.state == SystemState.LISTENING:
            pass # Listening state is now handled continuously by _stt_worker

        elif self.fsm.state == SystemState.PROCESSING_INTENT:
            if getattr(self, 'intent_task', None) is None or self.intent_task.done():
                async def _react_worker():
                    context = self.fsm.get_context()
                    instruction = context.get("voice_text", "")
                    
                    def update_ui(msg):
                        # Use reply_text for logs to the UI
                        self.fsm.current_context["reply_text"] = msg

                    # --- Conversational Bypass ---
                    clean_text = instruction.strip().lower()
                    conversational_phrases = ["hi", "hello", "hey", "sup", "what's up", "how are you", "who are you", "thanks", "thank you"]
                    if clean_text in conversational_phrases:
                        update_ui(f"Hello! I am your AI assistant. How can I help you today?")
                        try:
                            tts_manager.speak_async("Hello! I am your AI assistant.")
                        except Exception:
                            pass
                        self.fsm.transition(SystemState.IDLE)
                        return
                    # -----------------------------
                    
                    try:
                        # --- Smart Intent Router ---
                        settings = self.fsm.current_context.get("settings", {})
                        
                        if clean_text in ["generate-flashcard", "generate-snippet", "generate-handwritten", "generate-mindmap"]:
                            # Fetch recent context for the LLM
                            recent_context = self.fsm.current_context.get("reply_text", "")
                            plan = [
                                {
                                    "action": "generate_ui_component", 
                                    "target": clean_text,
                                    "context": recent_context
                                }
                            ]
                        elif clean_text in ["format-project", "run-tests", "build-prod", "start-server", "review-code"]:
                            # Map developer macros to terminal commands
                            cmd_map = {
                                "format-project": "npx prettier --write .",
                                "run-tests": "npm run test",
                                "build-prod": "npm run build",
                                "start-server": "npm run dev",
                                "review-code": "git diff"
                            }
                            plan = [
                                {
                                    "action": "run_terminal",
                                    "command": cmd_map.get(clean_text, "echo 'Unknown command'"),
                                    "cwd": self.fsm.current_context.get("settings", {}).get("devFolder", "E:\\AIF_Project\\ui")
                                }
                            ]
                        else:
                            # ── USE UNIFIED FORGE VLM PIPELINE VIA AGENT_LOOP ──
                            update_ui("Running unified VLM inference pipeline...")
                            try:
                                memory_mgr.abort_flag = False
                                plan_list = await plan_task(instruction, update_ui)
                                self.fsm.current_context["pending_plan"] = plan_list

                                if plan_list and isinstance(plan_list, list) and len(plan_list) > 0:
                                    first_step = plan_list[0] if isinstance(plan_list[0], dict) else {}
                                    action = first_step.get('action', '').replace('_', ' ').title()
                                    target = first_step.get('target', first_step.get('name', first_step.get('url', first_step.get('text', first_step.get('keys', '')))))
                                    
                                    # 1.5-Second UI Toast Delay with 100ms interval countdown/abort check
                                    toast_msg = f"Executing: {action} {target} in 1.5s... [Press ESC to Cancel]".strip()
                                    update_ui(toast_msg)
                                    try:
                                        event_bus.publish("ui_status", toast_msg)
                                    except Exception:
                                        pass

                                    aborted = False
                                    for _ in range(15):
                                        if getattr(memory_mgr, 'abort_flag', False):
                                            aborted = True
                                            break
                                        await asyncio.sleep(0.1)

                                    if aborted or getattr(memory_mgr, 'abort_flag', False):
                                        update_ui("🛑 TASK ABORTED BY KILL-SWITCH!")
                                        self.fsm.transition(SystemState.IDLE)
                                        return

                                    # Execute immediately without manual confirmation pause
                                    update_ui("Executing action...")
                                    self.fsm.transition(SystemState.EXECUTING)

                                    success = await execute_task_plan(plan_list, update_ui)

                                    if getattr(memory_mgr, 'abort_flag', False):
                                        update_ui("🛑 TASK ABORTED BY KILL-SWITCH!")
                                    elif success:
                                        update_ui("Action executed successfully.")
                                    else:
                                        update_ui("Action failed or unknown.")
                                else:
                                    update_ui("VLM produced empty plan.")

                                self.fsm.transition(SystemState.IDLE)
                            except Exception as e:
                                update_ui(f"VLM Inference Error: {e}")
                                self.fsm.transition(SystemState.IDLE)
                        # ---------------------------
                    except Exception as e:
                        update_ui(f"Error: {e}")
                        self.fsm.transition(SystemState.IDLE)
                    
                import asyncio
                self.intent_task = asyncio.create_task(_react_worker())
            
        elif self.fsm.state == SystemState.EXECUTING:
            # ReAct loop is running in thread, updates are sent via callback
            pass

        elif self.fsm.state == SystemState.AWAITING_CONFIRMATION:
            pass

    async def ws_handler(self, websocket):
        self.connected_clients.add(websocket)
        print("Web UI Connected!")
        try:
            while True:
                # Process AI state
                self.process_state()
                
                # Send data to UI
                context = self.fsm.get_context()
                
                action_text = "Standby"
                if self.fsm.state == SystemState.EXECUTING:
                    cmds = context.get("json_command", [])
                    if cmds and isinstance(cmds, list) and len(cmds) > 0:
                        first_cmd = cmds[0]
                        action_text = f"{first_cmd.get('action', '').upper()}: {first_cmd.get('target', '')}"
                elif self.fsm.state == SystemState.PROCESSING_INTENT:
                    action_text = "Analyzing intent..."
                elif self.fsm.state == SystemState.AWAITING_CONFIRMATION:
                    action_text = "Awaiting confirmation..."
                
                reply_text = context.get("reply_text", "")
                data = {
                    "state": self.fsm.state.name,
                    "hand": [{"id": p[0], "x": p[1], "y": p[2], "z": p[3]} for p in self.hand_data_for_ui],
                    "voice_text": context.get("voice_text", ""),
                    "reply_text": reply_text,
                    "action_text": action_text
                }
                await websocket.send(json.dumps(data))
                
                inject_html = context.get("inject_html", "")
                if inject_html:
                    await websocket.send(json.dumps({"type": "INJECT_UI", "html": inject_html}))
                    self.fsm.current_context["inject_html"] = ""
                
                # Clear reply text after sending to prevent loops
                if reply_text:
                    self.append_to_history("SYSTEM", reply_text)
                    self.fsm.current_context["reply_text"] = ""
                    await websocket.send(json.dumps({"type": "CHAT_HISTORY", "history": self.chat_history}))
                    
                # Check for commands from UI
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                    payload = json.loads(msg)
                    cmd = payload.get("command")
                    if cmd == "TOGGLE_DICTATION":
                        self.is_dictating = payload.get("state", False)
                        print(f"Dictation Mode: {self.is_dictating}")
                    elif cmd == "SET_MODE":
                        mode = payload.get("mode")
                        self.mode = mode
                        if mode == "BOTH":
                            self.is_listening_mode = True
                            self.is_tracking_mode = True
                        elif mode == "CAMERA_ONLY":
                            self.is_listening_mode = False
                            self.is_tracking_mode = True
                        elif mode == "VOICE_ONLY":
                            self.is_listening_mode = True
                            self.is_tracking_mode = False
                        elif mode == "STANDBY":
                            self.is_listening_mode = False
                            self.is_tracking_mode = False
                        
                        if hasattr(self, 'exec_mgr') and hasattr(self.exec_mgr, 'headless_executor'):
                            self.exec_mgr.headless_executor.llm_core.swap_model(mode)
                            
                        print(f"Ecosystem mode changed to: {mode}")
                    elif cmd == "BLOCK_SITES":
                        self._toggle_site_blocking(True)
                    elif cmd == "UNBLOCK_SITES":
                        self._toggle_site_blocking(False)
                    elif cmd == "CLEAR_HISTORY":
                        self.fsm.current_context["history"] = []
                        self.fsm.current_context["voice_text"] = ""
                        self.fsm.current_context["reply_text"] = ""
                        self.fsm.current_context["pending_plan"] = []
                        self.fsm.state = SystemState.IDLE
                        self.chat_history = []
                        try:
                            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                                json.dump([], f)
                        except Exception as e:
                            print(f"Failed to clear history file: {e}")
                            
                        if hasattr(self, 'connected_clients') and self.connected_clients:
                            msg = json.dumps({"type": "CHAT_HISTORY", "history": self.chat_history})
                            for client in list(self.connected_clients):
                                try:
                                    asyncio.create_task(client.send(msg))
                                except Exception:
                                    pass
                        print("Chat history cleared by UI.")
                    elif cmd == "ABORT_EXECUTION":
                        print("KILL-SWITCH ACTIVATED via UI!")
                        self.memory_mgr.abort_flag = True
                        self.fsm.current_context["reply_text"] = "🛑 TASK ABORTED BY KILL-SWITCH!"
                        if self.fsm.state == SystemState.EXECUTING:
                            self.fsm.transition(SystemState.IDLE)
                    elif cmd == "SELECT_FOLDER":
                        import tkinter as tk
                        from tkinter import filedialog
                        root = tk.Tk()
                        root.attributes('-topmost', True)
                        root.withdraw()
                        folder_path = filedialog.askdirectory()
                        root.destroy()
                        if folder_path:
                            # Normalize path for JSON/Websocket
                            folder_path = folder_path.replace("/", "\\")
                            await websocket.send(json.dumps({"type": "FOLDER_SELECTED", "path": folder_path}))
                    elif cmd == "IMAGE_UPLOAD":
                        img_data = payload.get("image")
                        if img_data:
                            import base64
                            import os
                            try:
                                img_bytes = base64.b64decode(img_data.split(',')[1])
                                img_path = os.path.abspath("uploaded_image.png")
                                with open(img_path, "wb") as f:
                                    f.write(img_bytes)
                                self.fsm.current_context["uploaded_image"] = img_path
                                print(f"Image uploaded and saved to {img_path}")
                            except Exception as e:
                                print(f"Failed to process image: {e}")
                    elif cmd == "TEXT_INPUT":
                        text_cmd = payload.get("text")
                        if text_cmd:
                            # Reset system state if stuck
                            if self.fsm.state != SystemState.IDLE:
                                self.fsm.transition(SystemState.IDLE)
                                
                            img_path = self.fsm.current_context.get("uploaded_image")
                            if img_path:
                                text_cmd = f"[IMAGE_ATTACHED: {img_path}] " + text_cmd
                            
                            # Log user input to history
                            display_text = payload.get("text")
                            self.append_to_history("USER", display_text)

                            self.fsm.current_context["voice_text"] = text_cmd
                            self.fsm.current_context["reply_text"] = ""
                            self.fsm.transition(SystemState.PROCESSING_INTENT)
                            self.process_state()
                                
                    elif cmd == "GET_HISTORY":
                        await websocket.send(json.dumps({
                            "type": "CHAT_HISTORY",
                            "history": self.chat_history
                        }))
                    elif cmd == "UPDATE_SETTINGS":
                        self.fsm.current_context["settings"] = payload.get("settings", {})
                        print(f"Settings updated: {self.fsm.current_context['settings']}")
                except asyncio.TimeoutError:
                    pass
                    
                await asyncio.sleep(1/60) # 60 FPS UI update rate
        except websockets.exceptions.ConnectionClosed:
            print("Web UI Disconnected.")
        finally:
            self.connected_clients.remove(websocket)
            self.is_listening_mode = False
            self.is_tracking_mode = False
            if self.fsm.state == SystemState.LISTENING:
                self.fsm.transition(SystemState.IDLE)

    async def main_server(self):
        import asyncio
        self.loop = asyncio.get_running_loop()
        print("Starting WebSocket Server on ws://127.0.0.1:8765 (Localhost Only)")
        async with websockets.serve(self.ws_handler, "127.0.0.1", 8765):
            await asyncio.Future()

    def start_server(self):
        # Run WebSocket server in a background thread
        ws_thread = threading.Thread(target=lambda: asyncio.run(self.main_server()), daemon=True)
        ws_thread.start()
        
        # Check if HUD is enabled in config.json
        enable_hud = False
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    enable_hud = config.get("ENABLE_HUD", False)
        except Exception:
            pass

        if enable_hud:
            try:
                from src.hud import launch_hud
                from src.fsm_module import SystemState
                
                def kill_callback():
                    self.memory_mgr.abort_flag = True
                    self.fsm.current_context["reply_text"] = "🛑 TASK ABORTED BY KILL-SWITCH!"
                    if self.fsm.state == SystemState.EXECUTING:
                        self.fsm.transition(SystemState.IDLE)
                        
                launch_hud(killswitch_cb=kill_callback)
            except Exception as e:
                print(f"[HUD] HUD GUI closed or not supported ({e}). Running in background mode.")
        else:
            print("[HUD] HUD GUI disabled via config.json. Running in headless background mode.")

        # CRITICAL: Keep main thread alive so closing HUD window NEVER terminates the backend!
        print("[AIF Server] Backend active & listening on ws://127.0.0.1:8765. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[AIF Server] Shutting down.")

if __name__ == '__main__':
    try:
        from forge_launcher import boot_forge_app
        boot_forge_app()
    except Exception as e:
        print(f"[AIF Server] Bootloader notice ({e}). Starting standalone server...")
        server = AIF_Server()
        server.start_server()
