import os
import sys
import socket
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import forge_launcher

def test_missing_llama_exe_raises_runtime_error():
    with patch("forge_launcher.find_llama_server_binary", return_value="C:\\nonexistent\\llama-server.exe"):
        with pytest.raises(RuntimeError) as exc_info:
            forge_launcher.boot_llama_server({"model_path": "fake", "mmproj_path": "fake"})
        assert "llama-server executable not found at" in str(exc_info.value)

def test_port_conflict_raises_runtime_error():
    with patch("forge_launcher.find_llama_server_binary", return_value=__file__): # Existing dummy file
        with patch("forge_launcher.is_port_in_use", return_value=True):
            with patch("forge_launcher.is_llama_server_running", return_value=False):
                with pytest.raises(RuntimeError) as exc_info:
                    forge_launcher.boot_llama_server({"model_path": "fake", "mmproj_path": "fake"}, port=8080)
                assert "Port conflict detected" in str(exc_info.value)

def test_health_check_timeout_raises_runtime_error():
    with patch("os.chdir"):
        with patch("forge_launcher.ensure_models_downloaded", return_value={"model_path": "fake", "mmproj_path": "fake"}):
            with patch("forge_launcher.is_llama_server_running", return_value=False):
                mock_proc = MagicMock()
                mock_proc.poll.return_value = None
                with patch("forge_launcher.boot_llama_server", return_value=mock_proc):
                    with patch("forge_launcher.poll_llama_server_health", return_value=False):
                        with pytest.raises(RuntimeError) as exc_info:
                            forge_launcher.boot_forge_app()
                        assert "llama-server health check failed" in str(exc_info.value)
                        # Verify finally block terminated the process
                        mock_proc.terminate.assert_called_once()

def test_sys_path_safe_append():
    with patch("os.chdir"):
        with patch("forge_launcher.ensure_models_downloaded", return_value={"model_path": "fake", "mmproj_path": "fake"}):
            with patch("forge_launcher.is_llama_server_running", return_value=True):
                with patch("server.AIF_Server") as mock_server:
                    mock_instance = MagicMock()
                    mock_server.return_value = mock_instance
                    forge_launcher.boot_forge_app()
                    assert forge_launcher.BASE_DIR in sys.path
                    # BASE_DIR should be at the end, not index 0
                    assert sys.path[0] != forge_launcher.BASE_DIR or len(sys.path) == 1

def test_is_port_in_use_detects_open_port():
    # Bind a temporary socket to check detection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = sock.getsockname()[1]
    try:
        assert forge_launcher.is_port_in_use("127.0.0.1", port) is True
    finally:
        sock.close()
