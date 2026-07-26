import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vlm_pipeline.tests.run_inference import run_vlm_inference

def test_moondream_vlm_parsing():
    """Verify VLM inference pipeline correctly extracts JSON action structures."""
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'Loading VLM weights...\n{"action": "wait", "duration": 1.5}\nInference complete.'
        mock_run.return_value = mock_result
        
        result = run_vlm_inference("dummy_path.png", "Wait 1.5 seconds")
        assert isinstance(result, dict)
        assert result.get("action") == "wait"
        assert result.get("duration") == 1.5

if __name__ == "__main__":
    test_moondream_vlm_parsing()

