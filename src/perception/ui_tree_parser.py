import time
from typing import Dict, List, Any
from src.logger import logger

def build_ui_tree() -> List[Dict[str, Any]]:
    """
    [EMERGENCY PATCH]
    pywinauto COM interop is deadlocking on the user's environment due to WebView2/UIA conflicts.
    We disable it completely and return an empty UI tree.
    The Worker LLM will naturally fallback to using keyboard shortcuts (Win+S, Tab, Enter)
    which is faster and more reliable than UIA clicking anyway.
    """
    start_time = time.time()
    logger.info(f"UI-Tree extraction took 0.000s. Total nodes: 0 (UIA Disabled to prevent hang)")
    return []

if __name__ == "__main__":
    print(build_ui_tree())
