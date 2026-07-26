import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vlm_pipeline.tests.run_inference import run_vlm_inference

def test_moondream_point_vlm_coordinate_action():
    """Verify VLM inference correctly parses point/click target coordinates into JSON plan."""
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"action": "click", "target": "Gemini copy button", "x": 450, "y": 800}'
        mock_run.return_value = mock_result
        
        result = run_vlm_inference("dummy_screen.png", "Point at the Gemini copy button.")
        assert result.get("action") == "click"
        assert int(result.get("x")) == 450
        assert int(result.get("y")) == 800


if __name__ == "__main__":
    test_moondream_point_vlm_coordinate_action()

