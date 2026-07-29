import os
import json
import threading
from datetime import datetime, timezone

DEFAULT_RULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "safety_rules.json")
)
DATASET_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "dataset")
)
SHADOW_DATASET_PATH = os.path.join(DATASET_DIR, "shadow_dataset.jsonl")
SAFETY_AUDIT_PATH = os.path.join(DATASET_DIR, "safety_audit.jsonl")


def _get_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SafetyLogger:
    def __init__(
        self,
        rules_path: str = DEFAULT_RULES_PATH,
        shadow_dataset_path: str = None,
        safety_audit_path: str = None
    ):
        self.rules_path = rules_path
        self._lock = threading.Lock()
        self.rules = self._load_rules()
        
        self.shadow_dataset_path = shadow_dataset_path or SHADOW_DATASET_PATH
        self.safety_audit_path = safety_audit_path or SAFETY_AUDIT_PATH

        os.makedirs(os.path.dirname(self.shadow_dataset_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.safety_audit_path), exist_ok=True)

    def _load_rules(self) -> dict:
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[SafetyLogger] Warning: failed to load rules from {self.rules_path} ({e})")
        return {"restricted_zones": [], "restricted_keywords": [], "restricted_apps": []}

    def reload_rules(self) -> None:
        with self._lock:
            self.rules = self._load_rules()

    def check_boundary_violation(self, action_payload: dict) -> bool:
        """
        Checks target (x,y) coordinates, command string, or target window against rules in config/safety_rules.json.
        If a boundary violation occurs, logs the breach via log_safety_audit and returns True (blocked).
        Returns False if safe.
        """
        if not isinstance(action_payload, dict):
            return False

        action_type = str(action_payload.get("action", "")).lower()
        target_text = str(
            action_payload.get("target")
            or action_payload.get("text")
            or action_payload.get("command")
            or action_payload.get("url")
            or action_payload.get("name")
            or ""
        )

        # 1. Command / Keyword Blacklist Check
        keywords = self.rules.get("restricted_keywords", [])
        for kw in keywords:
            if not kw:
                continue
            kw_lower = str(kw).lower()
            if kw_lower in target_text.lower() or kw_lower in action_type:
                breach_payload = {
                    "timestamp": _get_utc_timestamp(),
                    "violation_type": "COMMAND_BLACKLIST_VIOLATION",
                    "action_payload": action_payload,
                    "matched_rule": {
                        "rule_type": "keyword",
                        "keyword": kw
                    },
                    "blocked": True
                }
                self.log_safety_audit(breach_payload)
                return True

        # 2. Restricted Application Window Check
        app_name = str(
            action_payload.get("app")
            or action_payload.get("window_title")
            or action_payload.get("process_name")
            or (target_text if action_type in ["open_app", "switch_window", "launch", "app"] else "")
        )
        restricted_apps = self.rules.get("restricted_apps", [])
        for app in restricted_apps:
            if not app:
                continue
            app_lower = str(app).lower()
            if app_name and (app_lower in app_name.lower() or app_name.lower() in app_lower):
                breach_payload = {
                    "timestamp": _get_utc_timestamp(),
                    "violation_type": "RESTRICTED_APP_VIOLATION",
                    "action_payload": action_payload,
                    "matched_rule": {
                        "rule_type": "app",
                        "app": app
                    },
                    "blocked": True
                }
                self.log_safety_audit(breach_payload)
                return True

        # 3. Spatial Desktop Zone Boundary Check
        x = action_payload.get("x")
        if x is None:
            x = action_payload.get("target_x")
        y = action_payload.get("y")
        if y is None:
            y = action_payload.get("target_y")

        if x is None or y is None:
            point = action_payload.get("point")
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                x, y = point[0], point[1]
            elif isinstance(point, dict):
                x = point.get("x")
                y = point.get("y")

        if x is not None and y is not None:
            try:
                x_val = float(x)
                y_val = float(y)
                zones = self.rules.get("restricted_zones", [])
                for zone in zones:
                    x_min, y_min, x_max, y_max = None, None, None, None
                    zone_name = "Restricted Desktop Zone"

                    if isinstance(zone, dict):
                        zone_name = zone.get("name", zone_name)
                        if "bounds" in zone and isinstance(zone["bounds"], (list, tuple)) and len(zone["bounds"]) == 4:
                            x_min, y_min, x_max, y_max = zone["bounds"]
                        else:
                            x_min = zone.get("x_min")
                            y_min = zone.get("y_min")
                            x_max = zone.get("x_max")
                            y_max = zone.get("y_max")
                    elif isinstance(zone, (list, tuple)) and len(zone) == 4:
                        x_min, y_min, x_max, y_max = zone

                    if None not in (x_min, y_min, x_max, y_max):
                        if float(x_min) <= x_val <= float(x_max) and float(y_min) <= y_val <= float(y_max):
                            breach_payload = {
                                "timestamp": _get_utc_timestamp(),
                                "violation_type": "RESTRICTED_ZONE_BREACH",
                                "action_payload": action_payload,
                                "matched_rule": {
                                    "rule_type": "zone",
                                    "name": zone_name,
                                    "bounds": zone
                                },
                                "blocked": True
                            }
                            self.log_safety_audit(breach_payload)
                            return True
            except (ValueError, TypeError):
                pass

        return False

    def log_shadow_record(self, record_payload: dict) -> None:
        """
        Appends teach mode override record payloads to dataset/shadow_dataset.jsonl.
        Schema: timestamp, screen_dim, user_action, model_prediction, error_delta_px, context_history.
        """
        if not isinstance(record_payload, dict):
            return

        formatted_payload = {
            "timestamp": record_payload.get("timestamp") or _get_utc_timestamp(),
            "screen_dim": record_payload.get("screen_dim", {"width": 1920, "height": 1080}),
            "user_action": record_payload.get("user_action", {}),
            "model_prediction": record_payload.get("model_prediction", {}),
            "error_delta_px": record_payload.get("error_delta_px"),
            "context_history": record_payload.get("context_history", [])
        }

        os.makedirs(os.path.dirname(self.shadow_dataset_path), exist_ok=True)
        with self._lock:
            with open(self.shadow_dataset_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(formatted_payload) + "\n")

    def log_safety_audit(self, breach_payload: dict) -> None:
        """
        Appends security breach logs to dataset/safety_audit.jsonl containing
        (timestamp, violation_type, action_payload, matched_rule, blocked).
        """
        if not isinstance(breach_payload, dict):
            return

        formatted_payload = {
            "timestamp": breach_payload.get("timestamp") or _get_utc_timestamp(),
            "violation_type": breach_payload.get("violation_type", "SECURITY_BREACH"),
            "action_payload": breach_payload.get("action_payload", {}),
            "matched_rule": breach_payload.get("matched_rule", {}),
            "blocked": breach_payload.get("blocked", True)
        }

        os.makedirs(os.path.dirname(self.safety_audit_path), exist_ok=True)
        with self._lock:
            with open(self.safety_audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(formatted_payload) + "\n")


safety_logger = SafetyLogger()
