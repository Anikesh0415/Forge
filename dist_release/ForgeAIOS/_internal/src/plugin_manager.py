import os
import sys
import pkgutil
import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from src.logger import logger


class BaseForgePlugin(ABC):
    """
    Abstract Base Class for all Forge AI OS Plugins.
    """
    plugin_name: str = "BasePlugin"
    plugin_version: str = "1.0.0"

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize plugin state and configuration."""
        pass

    @abstractmethod
    def execute_action(self, action_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action assigned to this plugin. Returns result dictionary."""
        pass

    @abstractmethod
    def filter_action(self, action_payload: Dict[str, Any]) -> bool:
        """
        Evaluate whether an action is permitted.
        Returns True if action is allowed, False if blocked by plugin policy.
        """
        pass


class PluginManager:
    """
    Dynamic Plugin Loader and Lifecycle Manager for Forge AI OS.
    Discovers, registers, activates, deactivates, filters, and routes plugin actions.
    """
    def __init__(self, plugins_dir: Optional[str] = None):
        if plugins_dir is None:
            self.plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins"))
        else:
            self.plugins_dir = os.path.abspath(plugins_dir)
            
        self.registered_plugins: Dict[str, BaseForgePlugin] = {}
        self.active_plugins: Dict[str, BaseForgePlugin] = {}

    def discover_plugins(self, plugins_dir: Optional[str] = None) -> Dict[str, BaseForgePlugin]:
        """
        Scans directory using pkgutil and importlib to dynamically discover and register plugins
        implementing BaseForgePlugin.
        """
        target_dir = os.path.abspath(plugins_dir) if plugins_dir else self.plugins_dir
        if not os.path.exists(target_dir):
            logger.warning(f"Plugin directory not found: {target_dir}")
            return self.registered_plugins

        importlib.invalidate_caches()

        # Add target_dir parent to sys.path if not present
        parent_dir = os.path.dirname(target_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        modules_to_scan = []
        for finder, name, ispkg in pkgutil.iter_modules([target_dir]):
            if name.startswith("__"):
                continue
            modules_to_scan.append(name)

        for module_name in modules_to_scan:
            try:
                full_module_name = f"src.plugins.{module_name}"
                try:
                    mod = importlib.import_module(full_module_name)
                except (ImportError, ModuleNotFoundError):
                    mod = importlib.import_module(module_name)

                for attr_name, attr_value in inspect.getmembers(mod, inspect.isclass):
                    if (
                        issubclass(attr_value, BaseForgePlugin)
                        and attr_value is not BaseForgePlugin
                    ):
                        try:
                            instance = attr_value()
                            instance.initialize()
                            self.register_plugin(instance)
                            self.activate_plugin(instance.plugin_name)
                            logger.info(f"Discovered and activated plugin: {instance.plugin_name} (v{instance.plugin_version})")
                        except Exception as inst_err:
                            logger.error(f"Error instantiating plugin {attr_name} in {module_name}: {inst_err}")
            except Exception as e:
                logger.error(f"Failed to scan/load plugin module '{module_name}': {e}")

        return self.registered_plugins

    def register_plugin(self, plugin: BaseForgePlugin) -> bool:
        """Register a plugin instance."""
        if not isinstance(plugin, BaseForgePlugin):
            logger.error(f"Plugin {plugin} does not implement BaseForgePlugin")
            return False
        name = plugin.plugin_name
        self.registered_plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")
        return True

    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a registered plugin."""
        if plugin_name in self.registered_plugins:
            self.active_plugins[plugin_name] = self.registered_plugins[plugin_name]
            logger.info(f"Activated plugin: {plugin_name}")
            return True
        logger.warning(f"Cannot activate plugin {plugin_name}: not registered.")
        return False

    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin."""
        if plugin_name in self.active_plugins:
            del self.active_plugins[plugin_name]
            logger.info(f"Deactivated plugin: {plugin_name}")
            return True
        logger.warning(f"Cannot deactivate plugin {plugin_name}: not active.")
        return False

    def filter_action(self, action_payload: Dict[str, Any]) -> bool:
        """
        Passes action through active plugins.
        Returns False if any active plugin blocks the action, True otherwise.
        """
        for name, plugin in list(self.active_plugins.items()):
            try:
                allowed = plugin.filter_action(action_payload)
                if isinstance(allowed, tuple):
                    allowed = allowed[0]
                if not allowed:
                    logger.warning(f"Action blocked by plugin '{name}': {action_payload}")
                    return False
            except Exception as e:
                logger.error(f"Error in plugin '{name}' filter_action: {e}")
                return False
        return True

    def can_handle(self, action_payload: Dict[str, Any]) -> bool:
        """
        Determines whether any active plugin can handle the action payload.
        """
        if not isinstance(action_payload, dict):
            return False

        target_plugin = action_payload.get("plugin") or action_payload.get("target_plugin")
        if target_plugin and target_plugin in self.active_plugins:
            return True

        action_type = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()

        for name, plugin in self.active_plugins.items():
            if hasattr(plugin, "can_handle") and callable(getattr(plugin, "can_handle")):
                if plugin.can_handle(action_payload):
                    return True
            if name == "DevModePlugin":
                if action_type.startswith("dev_") or action_type in ["run_terminal", "intercept_window", "read_file", "write_file"]:
                    return True
            elif name == "StudentModePlugin":
                if action_type in ["start_study_session", "stop_study_session", "set_focus_bounds", "get_student_status", "add_prohibited_app", "add_prohibited_site"]:
                    return True

        return False

    def route_action(self, action_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches plugin action payload to target plugin's execute_action.
        Returns result dict from target plugin.
        """
        if not isinstance(action_payload, dict):
            return {"success": False, "error": "Invalid action payload format"}

        target_plugin_name = action_payload.get("plugin") or action_payload.get("target_plugin")

        if target_plugin_name and target_plugin_name in self.active_plugins:
            plugin = self.active_plugins[target_plugin_name]
            try:
                return plugin.execute_action(action_payload)
            except Exception as e:
                logger.error(f"Error executing action on targeted plugin '{target_plugin_name}': {e}")
                return {"success": False, "error": str(e)}

        action_type = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()

        for name, plugin in list(self.active_plugins.items()):
            if hasattr(plugin, "can_handle") and callable(getattr(plugin, "can_handle")):
                if plugin.can_handle(action_payload):
                    try:
                        return plugin.execute_action(action_payload)
                    except Exception as e:
                        return {"success": False, "error": str(e)}
            if name == "DevModePlugin" and (action_type.startswith("dev_") or action_type in ["run_terminal", "intercept_window", "read_file", "write_file"]):
                try:
                    return plugin.execute_action(action_payload)
                except Exception as e:
                    return {"success": False, "error": str(e)}
            if name == "StudentModePlugin" and action_type in ["start_study_session", "stop_study_session", "set_focus_bounds", "get_student_status", "add_prohibited_app", "add_prohibited_site"]:
                try:
                    return plugin.execute_action(action_payload)
                except Exception as e:
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": f"No active plugin found to handle action '{action_type}'"}
