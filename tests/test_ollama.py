import sys
import os
import json
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.llm_core import LocalLLMCore

def test_ollama_llm_core_mock_mode():
    """Verify LocalLLMCore in mock mode returns expected action response."""
    core = LocalLLMCore(use_mock=True)
    payload = {
        "voice_command": "open browser",
        "gesture_context": {}
    }
    result = asyncio.run(core.process_intent("Process user command", payload))
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0].get("action") == "speak"

def test_ollama_fallback_parsing():
    """Verify _fallback_to_ollama parses JSON responses correctly from mocked httpx client."""
    core = LocalLLMCore(use_mock=False)
    payload = {"voice_command": "open notepad"}
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={"response": '[{"action": "open_app", "target": "notepad"}]'})
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = asyncio.run(core._fallback_to_ollama("Open notepad", payload))
        assert result == [{"action": "open_app", "target": "notepad"}]

if __name__ == "__main__":
    test_ollama_llm_core_mock_mode()
    test_ollama_fallback_parsing()

