import os
import sys
import asyncio
import tempfile
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plugin_manager import BaseForgePlugin, PluginManager
from src.plugins.dev_mode import DevModePlugin
from src.plugins.student_mode import StudentModePlugin
from src.agent_loop import execute_task_plan, plugin_manager as global_pm


def test_challenger_dynamic_discovery():
    """Task 1: Dynamic Discovery Test with dummy plugin file in src/plugins/."""
    plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugins'))
    dummy_plugin_path = os.path.join(plugins_dir, "test_dummy_plugin.py")

    dummy_code = '''from src.plugin_manager import BaseForgePlugin

class TestDummyPlugin(BaseForgePlugin):
    plugin_name = "TestDummyPlugin"
    plugin_version = "3.1.0"

    def initialize(self, config=None):
        self.initialized = True
        return True

    def filter_action(self, action_payload):
        if action_payload.get("action") == "dummy_block":
            return False
        return True

    def execute_action(self, action_payload):
        return {"success": True, "dummy_response": "Hello from TestDummyPlugin"}
'''

    try:
        # 1. Create dummy plugin script
        with open(dummy_plugin_path, "w", encoding="utf-8") as f:
            f.write(dummy_code)

        # 2. Instantiate PluginManager and invoke discover_plugins()
        pm = PluginManager()
        discovered = pm.discover_plugins()

        # 3. Verify auto-discovery and registration without core code modifications
        assert "TestDummyPlugin" in discovered, "TestDummyPlugin was not discovered!"
        assert "TestDummyPlugin" in pm.registered_plugins
        assert "TestDummyPlugin" in pm.active_plugins
        
        plugin_instance = pm.active_plugins["TestDummyPlugin"]
        assert plugin_instance.plugin_name == "TestDummyPlugin"
        assert plugin_instance.plugin_version == "3.1.0"

        # Verify functionality of auto-discovered plugin
        assert pm.filter_action({"action": "dummy_block"}) is False
        assert pm.filter_action({"action": "dummy_allow"}) is True
        
        route_res = pm.route_action({"plugin": "TestDummyPlugin", "action": "test"})
        assert route_res.get("success") is True
        assert route_res.get("dummy_response") == "Hello from TestDummyPlugin"

    finally:
        # Clean up test_dummy_plugin.py afterwards
        if os.path.exists(dummy_plugin_path):
            os.remove(dummy_plugin_path)
            sys.modules.pop("src.plugins.test_dummy_plugin", None)
            sys.modules.pop("test_dummy_plugin", None)


def test_challenger_devmode_studentmode_workflow_stress():
    """Task 2: DevMode & StudentMode Workflow Stress Test."""
    # --- DevMode Stress Test ---
    dev = DevModePlugin()
    assert dev.initialize() is True

    # Intercept window handles
    intercept_res = dev.execute_action({"action": "dev_intercept_window"})
    assert intercept_res.get("success") is True
    assert isinstance(intercept_res.get("intercepted_windows"), list)

    # Shell execution
    exec_res = dev.execute_action({"action": "dev_run_terminal", "command": "echo MILLSTONE_3_DEV_MODE_STRESS"})
    assert exec_res.get("success") is True
    assert exec_res.get("returncode") == 0
    assert "MILLSTONE_3_DEV_MODE_STRESS" in exec_res.get("stdout", "")

    # File I/O
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "stress_test.txt")
        w_res = dev.execute_action({"action": "dev_write_file", "path": file_path, "content": "Stress Test Data 12345"})
        assert w_res.get("success") is True
        assert w_res.get("written_bytes") == len("Stress Test Data 12345")

        r_res = dev.execute_action({"action": "dev_read_file", "path": file_path})
        assert r_res.get("success") is True
        assert r_res.get("content") == "Stress Test Data 12345"

    # Filter destructive command
    assert dev.filter_action({"action": "dev_run_terminal", "command": "format c:"}) is False
    assert dev.filter_action({"action": "dev_run_terminal", "command": "echo safe"}) is True

    # --- StudentMode Stress Test ---
    student = StudentModePlugin()
    student.initialize({
        "is_study_session_active": True,
        "focus_bounds": {"x_min": 200, "y_min": 200, "x_max": 1600, "y_max": 900},
        "prohibited_apps": ["steam", "discord"],
        "prohibited_sites": ["reddit.com", "tiktok.com"]
    })

    # Prohibited App & Site Filtering
    assert student.filter_action({"action": "open_app", "target": "steam.exe"}) is False
    assert student.filter_action({"action": "open_app", "target": "discord"}) is False
    assert student.filter_action({"action": "open_app", "target": "notepad.exe"}) is True

    assert student.filter_action({"action": "navigate_url", "url": "https://reddit.com/r/python"}) is False
    assert student.filter_action({"action": "navigate_url", "url": "https://tiktok.com/@user"}) is False
    assert student.filter_action({"action": "navigate_url", "url": "https://github.com"}) is True

    # Focus bounds coordinate filtering
    # Inside bounds (500, 500)
    assert student.filter_action({"action": "click", "x": 500, "y": 500}) is True
    # Outside bounds (100, 500) - x below x_min 200
    assert student.filter_action({"action": "click", "x": 100, "y": 500}) is False
    # Outside bounds (500, 1000) - y above y_max 900
    assert student.filter_action({"action": "click", "x": 500, "y": 1000}) is False
    # Point tuple bounds checking
    assert student.filter_action({"action": "click", "coordinates": (1700, 500)}) is False
    assert student.filter_action({"action": "click", "coordinates": (800, 400)}) is True

    # Toggle study session
    assert student.execute_action({"action": "stop_study_session"})["is_study_session_active"] is False
    # Prohibited target allowed when study session disabled
    assert student.filter_action({"action": "open_app", "target": "steam.exe"}) is True

    # Re-enable study session
    assert student.execute_action({"action": "start_study_session"})["is_study_session_active"] is True
    assert student.filter_action({"action": "open_app", "target": "steam.exe"}) is False

    # Dynamic status & management
    student.execute_action({"action": "add_prohibited_app", "app": "poker"})
    assert student.filter_action({"action": "open_app", "target": "poker"}) is False

    status = student.execute_action({"action": "get_student_status"})
    assert status.get("success") is True
    assert "poker" in status.get("prohibited_apps")


def test_challenger_agent_loop_integration():
    """Task 3: Core Agent Loop Integration Verification."""
    # Note: execute_task_plan uses global_pm from src.agent_loop
    student = global_pm.active_plugins.get("StudentModePlugin")
    assert student is not None
    student.initialize({
        "is_study_session_active": True,
        "focus_bounds": {"x_min": 100, "y_min": 100, "x_max": 1000, "y_max": 800},
        "prohibited_apps": ["steam", "discord", "league of legends"],
        "prohibited_sites": ["twitch.tv", "reddit.com"]
    })

    # 1. Step payload blocked by filter_action (Exact substring match: "steam")
    blocked_step_plan = [{"action": "open_app", "target": "steam"}]
    res_blocked = asyncio.run(execute_task_plan(blocked_step_plan))
    assert res_blocked is False, "execute_task_plan should have failed due to plugin filter block"

    # 2. Step payload routed via can_handle and route_action
    routed_dev_step_plan = [{"action": "dev_run_terminal", "command": "echo ROUTED_AGENT_LOOP_TEST"}]
    res_routed = asyncio.run(execute_task_plan(routed_dev_step_plan))
    assert res_routed is True, "execute_task_plan should have succeeded via plugin action routing"


def test_challenger_string_normalization_evasion():
    """Empirical finding: String normalization evasion in StudentModePlugin filter_action."""
    student = StudentModePlugin()
    student.initialize({
        "is_study_session_active": True,
        "prohibited_apps": ["league of legends"]
    })
    # Target "LeagueOfLegends" (no spaces) bypasses "league of legends" (with spaces) check
    # because 'league of legends' in 'leagueoflegends' is False.
    bypass_result = student.filter_action({"action": "open_app", "target": "LeagueOfLegends"})
    assert bypass_result is True, "Target without spaces bypassed prohibited app filter because substring check lacks space normalization!"



def test_challenger_adversarial_edge_cases():
    """Adversarial stress-testing of edge cases and invalid inputs."""
    pm = PluginManager()
    pm.discover_plugins()

    # 1. Non-dict payloads to can_handle and route_action
    assert pm.can_handle("invalid string payload") is False
    assert pm.can_handle(None) is False
    assert pm.route_action("invalid string payload")["success"] is False
    assert pm.route_action(12345)["success"] is False

    # 2. Malformed coordinates in StudentMode
    student = StudentModePlugin()
    student.initialize({
        "is_study_session_active": True,
        "focus_bounds": {"x_min": 100, "y_min": 100, "x_max": 1000, "y_max": 800}
    })
    # Non-numeric string coordinates should not crash the filter
    assert student.filter_action({"action": "click", "x": "invalid", "y": "invalid"}) is True
    # None coordinates with no bounds violation
    assert student.filter_action({"action": "click"}) is True

    # 3. DevMode execution with empty/missing command
    dev = DevModePlugin()
    dev.initialize()
    res_empty_cmd = dev.execute_action({"action": "dev_run_terminal", "command": ""})
    assert res_empty_cmd["success"] is False
    assert "No command provided" in res_empty_cmd["error"]

    # 4. Unknown action on plugins
    res_unknown_dev = dev.execute_action({"action": "dev_non_existent_action"})
    assert res_unknown_dev["success"] is False

    res_unknown_student = student.execute_action({"action": "non_existent_student_action"})
    assert res_unknown_student["success"] is False
