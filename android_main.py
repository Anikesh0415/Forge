import sys
import os
import threading
import time
import asyncio
import websockets
import json

class Android_AIF_Server:
    def __init__(self):
        print("Initializing Android Native Server...")
        self.connected_clients = set()
        
        self.chat_history_file = os.path.join(os.path.dirname(__file__), "android_chat_history.json")
        self.chat_history = self._load_history()
        self.mode = "VOICE_ONLY"

    def _load_history(self):
        if os.path.exists(self.chat_history_file):
            try:
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        try:
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f)
        except Exception as e:
            print(f"Failed to save history: {e}")

    def append_to_history(self, sender, text):
        self.chat_history.append({"sender": sender, "text": text})
        self._save_history()

    async def ws_handler(self, websocket, path):
        self.connected_clients.add(websocket)
        print(f"Web UI Connected to Android Backend!")
        
        try:
            while True:
                # Handle incoming messages
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                    payload = json.loads(msg)
                    cmd = payload.get("command")
                    
                    if cmd == "GET_HISTORY":
                        await websocket.send(json.dumps({
                            "type": "CHAT_HISTORY",
                            "history": self.chat_history
                        }))
                    
                    elif cmd == "TEXT_INPUT":
                        text_cmd = payload.get("text")
                        if text_cmd:
                            # Log user input
                            self.append_to_history("USER", text_cmd)
                            
                            # Fake Processing for Android Standalone (Without LM Studio for now)
                            reply = f"Native Android Mode: You said '{text_cmd}'. (AI integration coming in next phase)"
                            self.append_to_history("SYSTEM", reply)
                            
                            await websocket.send(json.dumps({
                                "state": "IDLE",
                                "reply_text": reply,
                                "action_text": "Task Complete"
                            }))
                            
                except asyncio.TimeoutError:
                    pass
                
                await asyncio.sleep(0.05)
                
        except websockets.exceptions.ConnectionClosed:
            print("Web UI Disconnected.")
        finally:
            self.connected_clients.remove(websocket)

    async def main_server(self):
        print("Starting Android Native WebSocket Server on ws://0.0.0.0:8765")
        async with websockets.serve(self.ws_handler, "0.0.0.0", 8765):
            await asyncio.Future()

    def start_server(self):
        asyncio.run(self.main_server())

if __name__ == '__main__':
    server = Android_AIF_Server()
    server.start_server()
