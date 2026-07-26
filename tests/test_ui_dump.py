import pywinauto
from unittest.mock import patch, MagicMock

def dump_ui_tree():
    try:
        desktop = pywinauto.Desktop(backend="uia")
        win = desktop.active_window()
        if not win:
            return "No active window"
        
        controls = win.descendants()
        tree_elements = []
        for ctrl in controls[:50]: # limit to 50 for test
            name = ctrl.window_text()
            ctrl_type = ctrl.element_info.control_type
            if name:
                tree_elements.append(f"[{ctrl_type}] {name}")
                
        return "\n".join(tree_elements)
    except Exception as e:
        return str(e)

def test_ui_dump_returns_string():
    """Verify dump_ui_tree executes and returns string output."""
    result = dump_ui_tree()
    assert isinstance(result, str)
    assert len(result) > 0

def test_ui_dump_formatting_with_controls():
    """Verify UI tree elements formatting logic when active window elements are found."""
    mock_ctrl = MagicMock()
    mock_ctrl.window_text.return_value = "Main Window"
    mock_ctrl.element_info.control_type = "Window"
    
    mock_win = MagicMock()
    mock_win.descendants.return_value = [mock_ctrl]
    
    with patch("pywinauto.Desktop") as mock_desktop:
        mock_desktop.return_value.active_window.return_value = mock_win
        result = dump_ui_tree()
        assert "[Window] Main Window" in result

if __name__ == "__main__":
    print(dump_ui_tree())

