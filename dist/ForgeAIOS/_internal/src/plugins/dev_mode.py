import os
import sys
import subprocess
from typing import Dict, Any, Optional, List
from src.plugin_manager import BaseForgePlugin
from src.logger import logger


class DevModePlugin(BaseForgePlugin):
    """
    Developer Mode Plugin for Forge AI OS.
    Intercepts Terminal/IDE window handles (VS Code, Cursor, PowerShell, CMD, etc.)
    and executes direct shell commands and developer file operations.
    """
    plugin_name: str = "DevModePlugin"
    plugin_version: str = "1.0.0"

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        self.config = config or {}
        self.target_ide_patterns = self.config.get(
            "target_ide_patterns",
            ["visual studio code", "vscode", "cursor", "powershell", "cmd", "terminal", "pycharm", "windsurf", "bash"]
        )
        self.intercepted_handles: List[Dict[str, Any]] = []
        return True

    def filter_action(self, action_payload: Dict[str, Any]) -> bool:
        """
        Evaluates safety of dev actions. Standard dev actions are allowed.
        Returns False if prohibited destructive action detected, True otherwise.
        """
        action = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()
        target = str(action_payload.get("target") or action_payload.get("cmd") or action_payload.get("command") or "")

        forbidden = ["format ", "rmdir /s /q c:", "del /f /s /q c:\\"]
        if any(bad in target.lower() for bad in forbidden):
            return False
        return True

    def can_handle(self, action_payload: Dict[str, Any]) -> bool:
        action = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()
        dev_actions = [
            "dev_intercept_window", "intercept_window", "dev_intercept",
            "dev_run_terminal", "run_terminal", "dev_execute_shell",
            "dev_read_file", "dev_write_file"
        ]
        return action in dev_actions or action.startswith("dev_")

    def execute_action(self, action_payload: Dict[str, Any]) -> Dict[str, Any]:
        action = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()

        if action in ["dev_intercept_window", "intercept_window", "dev_intercept"]:
            return self._intercept_window_handles(action_payload)
        elif action in ["dev_run_terminal", "run_terminal", "dev_execute_shell"]:
            return self._run_terminal_command(action_payload)
        elif action in ["dev_read_file", "read_file"]:
            return self._read_file(action_payload)
        elif action in ["dev_write_file", "write_file"]:
            return self._write_file(action_payload)
        else:
            return {"success": False, "error": f"Unknown DevMode action: {action}"}

    def _intercept_window_handles(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_pattern = payload.get("pattern") or payload.get("target")
        patterns = [target_pattern.lower()] if target_pattern else self.target_ide_patterns

        intercepted = []
        try:
            import pygetwindow as gw
            all_windows = gw.getAllTitles()
            for title in all_windows:
                if title and any(pat in title.lower() for pat in patterns):
                    intercepted.append({"title": title, "type": "gui_window"})
        except Exception as e:
            logger.info(f"pygetwindow lookup note: {e}")

        if not intercepted and sys.platform == "win32":
            try:
                res = subprocess.run(["tasklist", "/FO", "CSV", "/V"], capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        line_lower = line.lower()
                        if any(pat in line_lower for pat in patterns):
                            parts = line.split('","')
                            title = parts[-1].strip('"') if len(parts) > 1 else line
                            intercepted.append({"title": title, "raw": line, "type": "process"})
            except Exception as task_err:
                logger.warning(f"tasklist fallback error: {task_err}")

        self.intercepted_handles = intercepted
        return {
            "success": True,
            "count": len(intercepted),
            "intercepted_windows": intercepted,
            "message": f"Intercepted {len(intercepted)} IDE/Terminal window handles."
        }

    def _run_terminal_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cmd = payload.get("command") or payload.get("cmd") or payload.get("target") or ""
        if not cmd:
            return {"success": False, "error": "No command provided for terminal execution."}

        cwd = payload.get("cwd") or os.getcwd()
        timeout = payload.get("timeout", 30)

        try:
            res = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "message": f"Executed command with return code {res.returncode}"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command execution timed out after {timeout} seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _read_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        file_path = payload.get("path") or payload.get("file_path") or payload.get("target")
        if not file_path:
            return {"success": False, "error": "No file path specified"}
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return {"success": True, "path": file_path, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _write_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        file_path = payload.get("path") or payload.get("file_path") or payload.get("target")
        content = payload.get("content", "")
        if not file_path:
            return {"success": False, "error": "No file path specified"}
        try:
            parent = os.path.dirname(file_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "path": file_path, "written_bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
