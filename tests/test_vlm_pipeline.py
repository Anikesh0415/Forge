import sys
import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_loop import capture_screenshot, plan_task, execute_task_plan, execute_react_loop
from src.vlm_pipeline.tests.run_inference import run_vlm_inference

def test_agent_loop_imports():
    """Verify src.agent_loop imports correctly without legacy planner dependency."""
    import src.agent_loop
    assert hasattr(src.agent_loop, "plan_task")
    assert hasattr(src.agent_loop, "execute_task_plan")
    assert hasattr(src.agent_loop, "execute_react_loop")
    assert hasattr(src.agent_loop, "capture_screenshot")

def test_sycl_flags_preset_in_inference_wrapper():
    """Verify SYCL environment variables are set during run_vlm_inference."""
    with patch("subprocess.run") as mock_run, \
         patch("os.path.exists", return_value=True):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"action": "open_github"}'
        mock_run.return_value = mock_result
        
        dummy_img = os.path.abspath("test_dummy.png")
        res = run_vlm_inference(dummy_img, "Open github")
        
        assert mock_run.called
        kwargs = mock_run.call_args[1]
        env = kwargs.get("env", {})
        
        assert env.get("SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS") == "1"
        assert env.get("ZES_ENABLE_SYSMAN") == "1"
        assert env.get("GGML_SYCL_DEBUG") == "0"
        assert res == {"action": "open_github"}

def test_capture_screenshot_creates_file(tmp_path):
    """Verify capture_screenshot snaps a file to disk."""
    out_file = str(tmp_path / "test_screen.png")
    result_path = capture_screenshot(out_file)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0

def test_plan_task_triggers_vlm_and_returns_plan():
    """Verify plan_task captures screenshot and invokes run_vlm_inference."""
    async def _test():
        expected_action = {"action": "click", "x": 500, "y": 300}
        with patch("src.agent_loop.run_vlm_inference", return_value=expected_action) as mock_vlm, \
             patch("src.agent_loop.capture_screenshot", return_value="mock_screen.png") as mock_snap:
            
            callbacks = []
            plan = await plan_task("Click the button", update_callback=lambda msg: callbacks.append(msg))
            
            assert mock_snap.called
            assert mock_vlm.called
            mock_vlm.assert_called_once_with("mock_screen.png", "Click the button")
            assert plan == [expected_action]
            assert any("Analyzing instruction with VLM" in c for c in callbacks)
    asyncio.run(_test())

def test_execute_task_plan_executes_step():
    """Verify execute_task_plan executes VLM step successfully."""
    from src.agent_loop import memory_mgr
    memory_mgr.abort_flag = False
    async def _test():
        step = {"action": "open_github"}
        with patch("src.vlm_pipeline.execution.executor.execute_action", return_value=True) as mock_exec:
            success = await execute_task_plan([step])
            assert success is True
            assert mock_exec.called
    asyncio.run(_test())

def test_execute_react_loop_wiring():
    """Verify execute_react_loop triggers plan_task and execute_task_plan."""
    expected_action = {"action": "click", "x": 100, "y": 200}
    with patch("src.agent_loop.plan_task", return_value=[expected_action]) as mock_plan, \
         patch("src.agent_loop.execute_task_plan", return_value=True) as mock_exec:
        res = asyncio.run(execute_react_loop("test instruction"))
        assert res is True
        mock_plan.assert_called_once()
        mock_exec.assert_called_once()

def test_server_imports_vlm_pipeline():
    """Verify server.py references plan_task from agent_loop."""
    with patch("keyboard.add_hotkey"):
        import server
        assert hasattr(server, "plan_task")
        assert hasattr(server, "execute_task_plan")

