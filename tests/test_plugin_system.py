import sys
import os
import pytest
import asyncio
import tempfile
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plugin_manager import BaseForgePlugin, PluginManager
from src.plugins.dev_mode import DevModePlugin
from src.plugins.student_mode import StudentModePlugin
from src.agent_loop import execute_task_plan, plugin_manager as global_plugin_manager


def test_base_plugin_interface():
    """Verify BaseForgePlugin abstract interface constraints."""
    class DummyPlugin(BaseForgePlugin):
        def initialize(self, config=None):
            return True
        def execute_action(self, action_payload):
            return {"success": True}
        def filter_action(self, action_payload):
            return True

    p = DummyPlugin()
    assert p.plugin_name == "BasePlugin"
    assert p.plugin_version == "1.0.0"
    assert p.initialize() is True
    assert p.execute_action({"action": "test"}) == {"success": True}
    assert p.filter_action({"action": "test"}) is True


def test_plugin_manager_discovery_and_lifecycle():
    """Verify PluginManager dynamic discovery, registration, activation, and deactivation."""
    pm = PluginManager()
    plugins = pm.discover_plugins()

    assert "DevModePlugin" in plugins
    assert "StudentModePlugin" in plugins
    assert isinstance(pm.registered_plugins["DevModePlugin"], DevModePlugin)
    assert isinstance(pm.registered_plugins["StudentModePlugin"], StudentModePlugin)

    # Verify active state after discovery
    assert "DevModePlugin" in pm.active_plugins
    assert "StudentModePlugin" in pm.active_plugins

    # Deactivate StudentModePlugin
    assert pm.deactivate_plugin("StudentModePlugin") is True
    assert "StudentModePlugin" not in pm.active_plugins
    assert "StudentModePlugin" in pm.registered_plugins

    # Activate StudentModePlugin
    assert pm.activate_plugin("StudentModePlugin") is True
    assert "StudentModePlugin" in pm.active_plugins


def test_plugin_manager_auto_discovery_new_file():
    """Verify auto-discovery of newly created .py files in src/plugins/ using importlib & pkgutil."""
    pm = PluginManager()
    plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'plugins'))
    temp_plugin_path = os.path.join(plugins_dir, "temp_dynamic_test_plugin.py")

    temp_code = '''
from src.plugin_manager import BaseForgePlugin

class TempDynamicTestPlugin(BaseForgePlugin):
    plugin_name = "TempDynamicTestPlugin"
    plugin_version = "2.0.0"

    def initialize(self, config=None):
        return True

    def filter_action(self, action_payload):
        if action_payload.get("action") == "blocked_by_temp_plugin":
            return False
        return True

    def execute_action(self, action_payload):
        return {"success": True, "message": "Executed by temp plugin"}
'''

    try:
        with open(temp_plugin_path, "w", encoding="utf-8") as f:
            f.write(temp_code)

        # Run discovery
        discovered = pm.discover_plugins()
        assert "TempDynamicTestPlugin" in discovered
        assert "TempDynamicTestPlugin" in pm.active_plugins

        # Test filtering with newly discovered plugin
        assert pm.filter_action({"action": "blocked_by_temp_plugin"}) is False
        assert pm.filter_action({"action": "allowed_action"}) is True

        # Test routing with newly discovered plugin
        res = pm.route_action({"plugin": "TempDynamicTestPlugin", "action": "run_temp"})
        assert res.get("success") is True
        assert res.get("message") == "Executed by temp plugin"

    finally:
        if os.path.exists(temp_plugin_path):
            os.remove(temp_plugin_path)
            # Remove from sys.modules cache if present
            sys.modules.pop("src.plugins.temp_dynamic_test_plugin", None)
            sys.modules.pop("temp_dynamic_test_plugin", None)


def test_dev_mode_plugin():
    """Verify DevModePlugin window interception, shell command execution, and file I/O."""
    dev = DevModePlugin()
    dev.initialize()

    # 1. Action filtering
    assert dev.filter_action({"action": "dev_run_terminal", "command": "echo Hello"}) is True
    assert dev.filter_action({"action": "dev_run_terminal", "command": "format c:"}) is False

    # 2. Window Handle Interception
    intercept_res = dev.execute_action({"action": "dev_intercept_window"})
    assert intercept_res.get("success") is True
    assert "intercepted_windows" in intercept_res

    # 3. Terminal Execution
    term_res = dev.execute_action({"action": "dev_run_terminal", "command": "echo DevModePluginTest"})
    assert term_res.get("success") is True
    assert "DevModePluginTest" in term_res.get("stdout", "")

    # 4. File Read / Write
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "dev_test.txt")
        write_res = dev.execute_action({"action": "dev_write_file", "path": test_file, "content": "DevMode File Content"})
        assert write_res.get("success") is True

        read_res = dev.execute_action({"action": "dev_read_file", "path": test_file})
        assert read_res.get("success") is True
        assert read_res.get("content") == "DevMode File Content"


def test_student_mode_plugin():
    """Verify StudentModePlugin bounds checking and app/site filtering."""
    student = StudentModePlugin()
    student.initialize({
        "is_study_session_active": True,
        "focus_bounds": {"x_min": 100, "y_min": 100, "x_max": 1000, "y_max": 800},
        "prohibited_apps": ["steam", "discord"],
        "prohibited_sites": ["reddit.com", "youtube.com"]
    })

    # 1. Prohibited app & website filtering
    assert student.filter_action({"action": "open_app", "target": "Steam"}) is False
    assert student.filter_action({"action": "navigate_url", "url": "https://www.reddit.com"}) is False
    assert student.filter_action({"action": "open_app", "target": "VS Code"}) is True
    assert student.filter_action({"action": "navigate_url", "url": "https://docs.python.org"}) is True

    # 2. Focus window coordinate bounds checking
    # In bounds click
    assert student.filter_action({"action": "click", "x": 500, "y": 400}) is True
    # Out of bounds click (x = 50, below x_min 100)
    assert student.filter_action({"action": "click", "x": 50, "y": 400}) is False
    # Out of bounds click (y = 900, above y_max 800)
    assert student.filter_action({"action": "click", "x": 500, "y": 900}) is False

    # 3. Toggle Study Session
    stop_res = student.execute_action({"action": "stop_study_session"})
    assert stop_res.get("is_study_session_active") is False
    # When study session is off, filtering permits prohibited apps
    assert student.filter_action({"action": "open_app", "target": "Steam"}) is True

    start_res = student.execute_action({"action": "start_study_session"})
    assert start_res.get("is_study_session_active") is True
    assert student.filter_action({"action": "open_app", "target": "Steam"}) is False


def test_agent_loop_plugin_integration():
    """Verify core agent loop action filtering and action routing with PluginManager."""
    pm = PluginManager()
    pm.discover_plugins()

    # Ensure StudentMode is active and configured for testing
    student = pm.active_plugins.get("StudentModePlugin")
    assert student is not None
    student.initialize({
        "is_study_session_active": True,
        "focus_bounds": {"x_min": 100, "y_min": 100, "x_max": 1000, "y_max": 800},
        "prohibited_apps": ["discord"],
        "prohibited_sites": ["reddit.com"]
    })

    # Test blocked action in execute_task_plan
    blocked_plan = [{"action": "open_app", "target": "Discord"}]
    res = asyncio.run(execute_task_plan(blocked_plan))
    assert res is False

    # Test plugin routed action in execute_task_plan
    dev_plan = [{"action": "dev_run_terminal", "command": "echo AgentLoopPluginRouting"}]
    res = asyncio.run(execute_task_plan(dev_plan))
    assert res is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
