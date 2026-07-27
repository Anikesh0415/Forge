from typing import Dict, Any, Optional, Set
from src.plugin_manager import BaseForgePlugin
from src.logger import logger


class StudentModePlugin(BaseForgePlugin):
    """
    Student Mode Plugin for Forge AI OS.
    Enforces focus window coordinate bounds and filters prohibited applications
    and websites during active study sessions.
    """
    plugin_name: str = "StudentModePlugin"
    plugin_version: str = "1.0.0"

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        self.config = config or {}
        self.is_study_session_active: bool = self.config.get("is_study_session_active", True)

        self.focus_bounds: Optional[Dict[str, int]] = self.config.get(
            "focus_bounds",
            {"x_min": 100, "y_min": 100, "x_max": 1800, "y_max": 1000}
        )

        self.prohibited_apps: Set[str] = set(self.config.get(
            "prohibited_apps",
            ["steam", "discord", "spotify", "league of legends", "valorant", "epic games", "battlenet"]
        ))

        self.prohibited_sites: Set[str] = set(self.config.get(
            "prohibited_sites",
            ["youtube.com", "reddit.com", "twitter.com", "x.com", "facebook.com", "tiktok.com", "netflix.com", "twitch.tv", "instagram.com"]
        ))

        return True

    def filter_action(self, action_payload: Dict[str, Any]) -> bool:
        """
        Enforces focus window bounds and filters prohibited apps/sites during active study sessions.
        Returns False if blocked, True if allowed.
        """
        if not self.is_study_session_active:
            return True

        action_type = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()
        target = str(
            action_payload.get("target")
            or action_payload.get("url")
            or action_payload.get("name")
            or action_payload.get("app")
            or action_payload.get("text")
            or ""
        ).lower()

        # 1. Prohibited application/website filter
        for app in self.prohibited_apps:
            if app in target:
                logger.warning(f"[StudentModePlugin] Blocked prohibited application target: '{target}' (matches '{app}')")
                return False

        for site in self.prohibited_sites:
            if site in target:
                logger.warning(f"[StudentModePlugin] Blocked prohibited website target: '{target}' (matches '{site}')")
                return False

        # 2. Focus window coordinate bounds enforcement
        if action_type in ["click", "double_click", "right_click", "mouse_move", "drag"]:
            x = action_payload.get("x")
            y = action_payload.get("y")
            if x is None or y is None:
                coords = action_payload.get("coordinates") or action_payload.get("point")
                if isinstance(coords, (tuple, list)) and len(coords) >= 2:
                    x, y = coords[0], coords[1]

            if x is not None and y is not None and self.focus_bounds:
                try:
                    x_val, y_val = int(x), int(y)
                    x_min = self.focus_bounds.get("x_min", 0)
                    x_max = self.focus_bounds.get("x_max", 1920)
                    y_min = self.focus_bounds.get("y_min", 0)
                    y_max = self.focus_bounds.get("y_max", 1080)

                    if not (x_min <= x_val <= x_max and y_min <= y_val <= y_max):
                        logger.warning(f"[StudentModePlugin] Blocked action coordinate ({x_val}, {y_val}) outside focus bounds ({x_min}, {y_min}, {x_max}, {y_max})")
                        return False
                except (ValueError, TypeError):
                    pass

        return True

    def can_handle(self, action_payload: Dict[str, Any]) -> bool:
        action_type = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()
        student_actions = [
            "start_study_session", "stop_study_session", "set_focus_bounds",
            "get_student_status", "add_prohibited_app", "add_prohibited_site"
        ]
        return action_type in student_actions

    def execute_action(self, action_payload: Dict[str, Any]) -> Dict[str, Any]:
        action_type = str(action_payload.get("action", "") or action_payload.get("action_type", "")).lower()

        if action_type == "start_study_session":
            self.is_study_session_active = True
            return {
                "success": True,
                "is_study_session_active": True,
                "message": "Study session activated. Focus bounds and prohibited app/site filters enabled."
            }
        elif action_type == "stop_study_session":
            self.is_study_session_active = False
            return {
                "success": True,
                "is_study_session_active": False,
                "message": "Study session deactivated."
            }
        elif action_type == "set_focus_bounds":
            bounds = action_payload.get("focus_bounds") or action_payload.get("bounds") or action_payload
            if isinstance(bounds, dict):
                self.focus_bounds = {
                    "x_min": bounds.get("x_min", 0),
                    "y_min": bounds.get("y_min", 0),
                    "x_max": bounds.get("x_max", 1920),
                    "y_max": bounds.get("y_max", 1080)
                }
                return {"success": True, "focus_bounds": self.focus_bounds, "message": "Focus bounds updated."}
            return {"success": False, "error": "Invalid focus_bounds dictionary provided"}
        elif action_type == "get_student_status":
            return {
                "success": True,
                "is_study_session_active": self.is_study_session_active,
                "focus_bounds": self.focus_bounds,
                "prohibited_apps": list(self.prohibited_apps),
                "prohibited_sites": list(self.prohibited_sites)
            }
        elif action_type == "add_prohibited_app":
            app = action_payload.get("app") or action_payload.get("target")
            if app:
                self.prohibited_apps.add(app.lower())
                return {"success": True, "message": f"Added '{app}' to prohibited applications."}
            return {"success": False, "error": "No application name provided"}
        elif action_type == "add_prohibited_site":
            site = action_payload.get("site") or action_payload.get("target")
            if site:
                self.prohibited_sites.add(site.lower())
                return {"success": True, "message": f"Added '{site}' to prohibited websites."}
            return {"success": False, "error": "No website domain provided"}
        else:
            return {"success": False, "error": f"Unknown StudentMode action: {action_type}"}
