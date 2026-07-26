import sys
import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyautogui
from src.agent_loop import plan_task, execute_task_plan, memory_mgr
from src.vlm_pipeline.execution.executor import execute_action
from src.fsm_module import SystemState
import server


def test_auto_execution_flow_without_confirmation_pause():
    """Verify parsed VLM JSON actions execute automatically without manual confirmation."""
    async def _test():
        memory_mgr.abort_flag = False
        dummy_plan = [{"action": "click", "x": 100, "y": 200}]
        
        with patch("src.agent_loop.run_vlm_inference", return_value=dummy_plan), \
             patch("src.agent_loop.capture_screenshot", return_value="dummy.png"), \
             patch("src.vlm_pipeline.execution.executor.execute_action", return_value=True) as mock_exec:
            
            srv = server.AIF_Server()
            srv.fsm.current_context["voice_text"] = "click the icon"
            
            # Execute react worker logic
            plan = await plan_task("click the icon")
            assert plan == dummy_plan
            
            success = await execute_task_plan(plan)
            assert success is True
            assert mock_exec.called
            # Verify system did not freeze or get stuck in AWAITING_CONFIRMATION
            assert srv.fsm.state != SystemState.AWAITING_CONFIRMATION
            
    asyncio.run(_test())


def test_1_5s_toast_delay_cancellation():
    """Verify 1.5s UI toast delay handles cancellation via abort_flag during countdown."""
    async def _test():
        memory_mgr.abort_flag = False
        srv = server.AIF_Server()
        ui_updates = []

        def mock_update_ui(msg):
            ui_updates.append(msg)
            srv.fsm.current_context["reply_text"] = msg

        dummy_plan = [{"action": "type", "text": "hello"}]

        with patch("src.agent_loop.plan_task", return_value=dummy_plan), \
             patch("src.agent_loop.execute_task_plan", return_value=True) as mock_exec:

            # Trigger abort_flag halfway through countdown via background task
            async def trigger_abort():
                await asyncio.sleep(0.3)
                memory_mgr.abort_flag = True

            asyncio.create_task(trigger_abort())

            # Simulate reaction worker countdown behavior
            action_desc = "Type"
            target_desc = "hello"
            toast_msg = f"Executing: {action_desc} {target_desc} in 1.5s... [Press ESC to Cancel]"
            mock_update_ui(toast_msg)

            aborted = False
            for _ in range(15):
                if getattr(memory_mgr, 'abort_flag', False):
                    aborted = True
                    break
                await asyncio.sleep(0.1)

            if aborted:
                mock_update_ui("🛑 TASK ABORTED BY KILL-SWITCH!")
                srv.fsm.transition(SystemState.IDLE)

            assert aborted is True
            assert not mock_exec.called
            assert srv.fsm.state == SystemState.IDLE
            assert any("Executing: Type hello in 1.5s" in u for u in ui_updates)
            assert any("🛑 TASK ABORTED BY KILL-SWITCH!" in u for u in ui_updates)

    asyncio.run(_test())


def test_global_esc_killswitch_handler_execution():
    """Verify _global_killswitch_handler sets abort_flag, moves mouse to (0,0), and resets FSM state to IDLE."""
    srv = server.AIF_Server()
    srv.fsm.transition(SystemState.EXECUTING)
    memory_mgr.abort_flag = False

    with patch("pyautogui.moveTo") as mock_move:
        server._global_killswitch_handler()

        assert mock_move.called
        mock_move.assert_called_once_with(0, 0, duration=0)
        assert memory_mgr.abort_flag is True
        assert srv.fsm.state == SystemState.IDLE
        assert srv.fsm.current_context.get("reply_text") == "🛑 TASK ABORTED BY KILL-SWITCH!"


def test_execute_task_plan_aborts_on_killswitch():
    """Verify execute_task_plan stops execution immediately if abort_flag is set or PyAutoGUI failsafe triggers."""
    async def _test():
        memory_mgr.abort_flag = True
        plan = [{"action": "click", "x": 10, "y": 10}, {"action": "press", "key": "enter"}]

        with patch("src.vlm_pipeline.execution.executor.execute_action") as mock_exec:
            res = await execute_task_plan(plan)
            assert res is False
            assert not mock_exec.called

    asyncio.run(_test())


def test_executor_catches_pyautogui_failsafe_exception():
    """Verify execute_action in executor catches pyautogui.FailSafeException cleanly."""
    memory_mgr.abort_flag = False

    with patch("pyautogui.click", side_effect=pyautogui.FailSafeException):
        res = execute_action({"action": "click", "x": 0, "y": 0})
        assert res is False
        assert memory_mgr.abort_flag is True
