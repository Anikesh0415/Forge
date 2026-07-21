# Forge API Documentation

## WebSocket API (`server.py`)

The main communication between the UI (or Mobile App) and the Backend happens over WebSockets.
The server runs on `ws://localhost:8765` (and broadcasts to `ws://<local-ip>:8765` for remote access).

### Message Format (Client -> Server)
Messages sent to the backend must be stringified JSON objects.

#### 1. Voice Command / Instruction
```json
{
  "type": "VOICE_COMMAND",
  "text": "Open Chrome and go to youtube.com"
}
```
**Action**: Triggers the Smart Intent Router to determine whether to reply in chat, run a background task, or execute a complex automation plan.

#### 2. Settings Update
```json
{
  "type": "UPDATE_SETTINGS",
  "settings": {
    "developer_mode": false,
    "student_mode": true
  }
}
```
**Action**: Updates the server's context.

#### 3. Execution Feedback
```json
{
  "type": "EXECUTION_FEEDBACK",
  "status": "APPROVED" // or "REJECTED" or "REPLAN"
}
```
**Action**: Approves or rejects a proposed Macro Automation plan.

#### 4. Get History
```json
{
  "type": "GET_HISTORY"
}
```
**Action**: Requests the entire chat history.

### Message Format (Server -> Client)

#### 1. Chat History Payload
```json
{
  "type": "HISTORY",
  "data": [
    {"sender": "USER", "text": "hi"},
    {"sender": "SYSTEM", "text": "Hello! How can I assist you today?"}
  ]
}
```

#### 2. System Settings Sync
```json
{
  "type": "SYSTEM_SETTINGS",
  "settings": {
    "developer_mode": false,
    "student_mode": false,
    "volume_muted": false
  }
}
```

#### 3. Log Messages
```json
{
  "type": "LOG",
  "message": "[Macro Orchestrator] Generating plan..."
}
```

## Intent Router Modes
- **Conversational**: For simple greetings and generic chat. Bypasses execution.
- **Headless Background**: For tasks like downloading a YouTube transcript, generating flashcards, or querying a web API silently.
- **GUI Takeover (Macro)**: Full UI automation utilizing mouse, keyboard, and Vision (Moondream) to control apps on the screen.
