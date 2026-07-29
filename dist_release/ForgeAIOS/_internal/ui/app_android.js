// Android App JavaScript Logic
const serverSetup = document.getElementById('server-setup');
const ipInput = document.getElementById('ip-input');
const connectBtn = document.getElementById('connect-btn');

const wsStatus = document.getElementById('ws-status');
const statusDot = document.getElementById('status-dot');
const actionText = document.getElementById('action-text');
const chatLog = document.getElementById('chat-log');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');

let ws;

// Load saved IP
const savedIP = localStorage.getItem('servent_ip');
if (savedIP) {
    ipInput.value = savedIP;
}

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'USER' ? 'user-msg' : 'system-msg');
    
    const bubble = document.createElement('div');
    bubble.classList.add('msg-bubble');
    bubble.textContent = text;
    msgDiv.appendChild(bubble);
    
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function connectToBrain(ip) {
    if (!ip) return;
    
    wsStatus.textContent = 'Connecting...';
    
    // Connect to WebSocket on port 8765
    ws = new WebSocket(`ws://${ip}:8765`);
    
    ws.onopen = () => {
        serverSetup.style.display = 'none';
        wsStatus.textContent = 'Connected';
        statusDot.classList.add('active');
        localStorage.setItem('servent_ip', ip);
        ws.send(JSON.stringify({ command: "GET_HISTORY" }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === "CHAT_HISTORY") {
            chatLog.innerHTML = "";
            if (data.history.length === 0) {
                appendMessage('SYSTEM', 'Connected to Windows Brain.');
            } else {
                data.history.forEach(msg => {
                    appendMessage(msg.sender, msg.text);
                });
            }
            return;
        }
        
        if (data.reply_text) {
            appendMessage('SYSTEM', data.reply_text);
        }
        
        if (data.action_text) {
            actionText.style.display = 'block';
            actionText.textContent = data.action_text;
            if (data.state === 'IDLE') {
                actionText.style.display = 'none';
            }
        }
        
        const isBusy = data.state === 'PROCESSING_INTENT' || data.state === 'EXECUTING';
        textInput.disabled = isBusy;
        sendBtn.disabled = isBusy;
    };
    
    ws.onerror = (e) => {
        console.error("WS Error", e);
        wsStatus.textContent = 'Error';
    };
    
    ws.onclose = () => {
        wsStatus.textContent = 'Disconnected';
        statusDot.classList.remove('active');
        serverSetup.style.display = 'flex'; // Show connection screen again
    };
}

connectBtn.addEventListener('click', () => {
    connectToBrain(ipInput.value.trim());
});

function sendTextCommand() {
    const text = textInput.value.trim();
    if (text && ws && ws.readyState === WebSocket.OPEN) {
        appendMessage('USER', text);
        ws.send(JSON.stringify({
            command: "TEXT_INPUT",
            text: text
        }));
        textInput.value = '';
    }
}

sendBtn.addEventListener('click', sendTextCommand);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendTextCommand();
});
