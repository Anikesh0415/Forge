import os
import sys
import json
import math
import asyncio
import pytest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.safety_logger import SafetyLogger, safety_logger
from src.agent_loop import handle_interactive_override, crop_target_element, execute_task_plan


@pytest.fixture
def temp_safety_env(tmp_path):
    """
    Creates a temporary directory with safety rules and isolated audit/shadow dataset logs.
    """
    rules_content = {
        "restricted_zones": [
            {
                "name": "Restricted Corner",
                "x_min": 1700,
                "y_min": 1040,
                "x_max": 1920,
                "y_max": 1080
            },
            {
                "name": "Array Zone",
                "bounds": [0, 0, 100, 100]
            }
        ],
        "restricted_keywords": [
            "del ",
            "format ",
            "rmdir",
            "powershell -enc"
        ],
        "restricted_apps": [
            "regedit.exe",
            "cmd.exe",
            "Restricted App"
        ]
    }
    
    rules_file = tmp_path / "safety_rules.json"
    rules_file.write_text(json.dumps(rules_content), encoding="utf-8")
    
    audit_file = str(tmp_path / "safety_audit.jsonl")
    shadow_file = str(tmp_path / "shadow_dataset.jsonl")

    logger_instance = SafetyLogger(
        rules_path=str(rules_file),
        shadow_dataset_path=shadow_file,
        safety_audit_path=audit_file
    )
    return logger_instance, tmp_path


def test_spatial_zone_violation(temp_safety_env):
    logger_instance, tmp_path = temp_safety_env
    
    # 1. Action inside restricted zone dict format
    action_inside = {"action": "click", "x": 1800, "y": 1050}
    assert logger_instance.check_boundary_violation(action_inside) is True

    # 2. Action inside array zone format
    action_inside_array = {"action": "click", "point": [50, 50]}
    assert logger_instance.check_boundary_violation(action_inside_array) is True

    # 3. Action outside restricted zones
    action_outside = {"action": "click", "x": 500, "y": 500}
    assert logger_instance.check_boundary_violation(action_outside) is False


def test_command_blacklist_violation(temp_safety_env):
    logger_instance, _ = temp_safety_env
    
    # Destructive keyword in target text
    destructive_action = {"action": "type_text", "target": "del C:\\System32"}
    assert logger_instance.check_boundary_violation(destructive_action) is True

    # Safe keyword
    safe_action = {"action": "type_text", "target": "hello world"}
    assert logger_instance.check_boundary_violation(safe_action) is False


def test_restricted_app_violation(temp_safety_env):
    logger_instance, _ = temp_safety_env
    
    # Restricted app target
    app_action = {"action": "open_app", "target": "regedit.exe"}
    assert logger_instance.check_boundary_violation(app_action) is True

    # Window title violation
    window_action = {"action": "focus_window", "window_title": "Restricted App Window"}
    assert logger_instance.check_boundary_violation(window_action) is True

    # Safe app
    safe_app = {"action": "open_app", "target": "notepad.exe"}
    assert logger_instance.check_boundary_violation(safe_app) is False


def test_log_safety_audit(temp_safety_env):
    logger_instance, _ = temp_safety_env
    audit_file = logger_instance.safety_audit_path

    breach_action = {"action": "click", "x": 1800, "y": 1050}
    logger_instance.check_boundary_violation(breach_action)

    assert os.path.exists(audit_file)
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        last_record = json.loads(lines[0])
        assert last_record["violation_type"] == "RESTRICTED_ZONE_BREACH"
        assert last_record["blocked"] is True
        assert "timestamp" in last_record
        assert last_record["action_payload"] == breach_action


def test_log_shadow_record(temp_safety_env):
    logger_instance, _ = temp_safety_env
    shadow_file = logger_instance.shadow_dataset_path

    payload = {
        "timestamp": "2026-07-27T16:00:00Z",
        "screen_dim": {"width": 1920, "height": 1080},
        "user_action": {"type": "click", "x": 450, "y": 300},
        "model_prediction": {"type": "click", "x": 480, "y": 300},
        "error_delta_px": 30.0,
        "context_history": [{"action": "open_app", "target": "browser"}]
    }

    logger_instance.log_shadow_record(payload)

    assert os.path.exists(shadow_file)
    with open(shadow_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["timestamp"] == "2026-07-27T16:00:00Z"
        assert record["error_delta_px"] == 30.0
        assert record["screen_dim"] == {"width": 1920, "height": 1080}
        assert len(record["context_history"]) == 1


def test_crop_target_element(tmp_path):
    img_path = str(tmp_path / "test_screenshot.png")
    img = Image.new("RGB", (800, 600), color="blue")
    img.save(img_path)

    crop_path = crop_target_element(img_path, x=400, y=300, crop_width=100, crop_height=100)
    assert crop_path != ""
    assert os.path.exists(crop_path)
    
    cropped_img = Image.open(crop_path)
    assert cropped_img.width <= 100
    assert cropped_img.height <= 100


def test_handle_interactive_override(tmp_path):
    img_path = str(tmp_path / "test_screen.png")
    img = Image.new("RGB", (1920, 1080), color="red")
    img.save(img_path)

    user_act = {"type": "click", "x": 500, "y": 400}
    model_pred = {"type": "click", "x": 530, "y": 440}
    ctx_hist = [{"action": "click", "target": "button1"}]

    record = handle_interactive_override(
        user_action=user_act,
        model_prediction=model_pred,
        screenshot_path=img_path,
        context_history=ctx_hist
    )

    assert record["error_delta_px"] == pytest.approx(50.0, abs=1e-2)
    assert "target_crop_path" in record["user_action"]
    assert os.path.exists(record["user_action"]["target_crop_path"])
    assert record["context_history"] == ctx_hist
    assert record["screen_dim"] == {"width": 1920, "height": 1080}


def test_agent_loop_safety_enforcement():
    # Attempting step in restricted zone defined in config/safety_rules.json (1700, 1040 to 1920, 1080)
    blocked_plan = [{"action": "click", "x": 1800, "y": 1050}]
    res = asyncio.run(execute_task_plan(blocked_plan))
    assert res is False
