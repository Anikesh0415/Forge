# Milestone 3 Codebase Investigation & Implementation Strategy

## Executive Summary
This document presents the detailed architectural investigation and implementation strategy for **Milestone 3: Dynamic Plugin Ecosystem & Core Integration** in Forge AI OS.

Milestone 3 establishes a production-grade, extensible plugin framework based on Python's `importlib` and `pkgutil` modules. It introduces a standardized abstract interface (`BaseForgePlugin`), a dynamic plugin discovery and lifecycle manager (`PluginManager` in `src/plugin_manager.py`), two initial production plugins (`DevModePlugin` and `StudentModePlugin`), and direct integration into the core execution loop (`src/agent_loop.py`).

---

## 1. Current State & Requirements Analysis

### 1.1 Existing Codebase Findings
1. **Missing Component**: `src/plugin_manager.py` does not exist yet.
2. **Legacy Plugins Directory (`src/plugins/`)**:
   - Contains 7 legacy plugin scripts (`hello_world.py`, `notion_api.py`, `clock_manager.py`, `google_search.py`, `whatsapp_automation.py`, `windows_phone_link.py`, `youtube_player.py`).
   - Legacy plugins rely on a function-based hook `register_plugin(registry)` called by `src/action_library.py` (lines 385–406).
3. **Core Agent Loop (`src/agent_loop.py`)**:
   - `execute_task_plan()` (lines 114–188) enforces a basic hardcoded `is_safe_action` guardrail and dispatches to `ExecutionManager` (`exec_mgr`).
   - Lacks plugin discovery, dynamic action filtering, and action routing hooks.
4. **Developer Capabilities (`src/executors/dev_executor.py`)**:
   - Contains `DevExecutor` supporting `read_file`, `write_file`, `run_terminal`, and `search_knowledge_base`.
5. **Project Interface Contract (`PROJECT.md`)**:
   - Lines 28–34 define the required `BaseForgePlugin` contract:
     - `plugin_name: str`
     - `plugin_version: str`
     - `initialize(config: dict) -> bool`
     - `execute_action(action_payload: dict) -> dict`
     - `filter_action(action_payload: dict) -> bool`

---

## 2. Technical Architecture & Design

### 2.1 Standardized Plugin Interface (`BaseForgePlugin`)
To enforce strict type safety and interface consistency across all plugins, an abstract base class `BaseForgePlugin` will be implemented using Python's `abc` module.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseForgePlugin(ABC):
    """
    Abstract Base Class for all Forge AI OS Plugins.
    """
    plugin_name: str = "BasePlugin"
    plugin_version: str = "1.0.0"

    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None) -> bool:
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
```

---

### 2.2 Dynamic Plugin Loader & Lifecycle Manager (`src/plugin_manager.py`)
`PluginManager` will manage the lifecycle of all plugins: discovery, registration, activation/deactivation, action filtering, and action routing.

#### Key Mechanics:
1. **Dynamic Scanning**: Uses `pkgutil.iter_modules([plugins_dir])` and `importlib.import_module()` to dynamically scan and import all Python modules in `src/plugins/`.
2. **Type Inspection**: Uses `inspect.getmembers()` and `issubclass()` to find classes that inherit from `BaseForgePlugin` (excluding `BaseForgePlugin` itself).
3. **Legacy Compatibility**: Safely detects legacy `register_plugin(registry)` hooks without throwing errors, ensuring smooth backward compatibility.
4. **Registry & State Management**:
   - `registered_plugins`: Dict mapping `plugin_name` to instantiated plugin object.
   - `active_plugins`: Dict mapping `plugin_name` to active plugin object.
5. **Action Filtering (`filter_action`)**:
   - Iterates through all `active_plugins`.
   - Calls `plugin.filter_action(action_payload)`.
   - If any active plugin returns `False`, the action is blocked immediately.
6. **Action Routing (`route_action`)**:
   - Checks if an action payload target or type matches any active plugin's capabilities.
   - Dispatches execution to the appropriate plugin's `execute_action()`.

---

### 2.3 Initial Production Plugins

#### 1. DevModePlugin (`src/plugins/dev_mode.py`)
- **Purpose**: Intercepts Terminal/IDE window handles and executes direct shell commands and developer file operations.
- **Class**: `DevModePlugin(BaseForgePlugin)`
- **Capabilities**:
  - Window Handle Interception: Detects active IDEs (VS Code, Cursor, PyCharm, etc.) and Terminals (PowerShell, Windows Terminal, CMD, Bash) via window title pattern matching (`pygetwindow` or system fallbacks).
  - Terminal Command Execution: Direct shell execution with configurable working directory, timeout handling, and output truncation.
  - Developer File Operations: Direct high-speed code file reading and writing.
- **Action Payloads**: `dev_run_terminal`, `dev_intercept_window`, `dev_read_file`, `dev_write_file`.

#### 2. StudentModePlugin (`src/plugins/student_mode.py`)
- **Purpose**: Enforces focus window bounds and filters prohibited applications/websites during study sessions.
- **Class**: `StudentModePlugin(BaseForgePlugin)`
- **Capabilities**:
  - Active Study Session Tracking: Configurable focus state (`is_study_session_active`).
  - Prohibited Application & Site Filtering: Blocks launched applications or browser URLs matching blacklisted patterns (e.g., gaming apps, social media: Steam, Discord, Twitter/X, Reddit, YouTube, TikTok).
  - Focus Window Bounds Enforcement: Validates click coordinates `(x, y)` against a defined bounding box `{x_min, y_min, x_max, y_max}`. Blocks clicks that land outside designated focus regions.
- **Action Payloads**: `start_study_session`, `stop_study_session`, `set_focus_bounds`, `get_student_status`.

---

### 2.4 Core Integration (`src/agent_loop.py`)
`src/agent_loop.py` will integrate `PluginManager` directly into `execute_task_plan()`:

```python
# 1. PLUGIN ACTION FILTERING GUARDRAIL
allowed, filter_reason = plugin_manager.filter_action(step)
if not allowed:
    notify(f"[TRACE] 🛑 PLUGIN FILTER ALERT: {filter_reason}")
    memory_mgr.log_action(action_type, str(target), filter_reason, False)
    return False

# 2. PLUGIN ACTION ROUTING
if plugin_manager.can_handle(action_type):
    success, exec_msg = plugin_manager.route_action(step)
```

---

## 3. Recommended Implementation Roadmap (for Implementer Agent)

1. **Step 1: Implement `src/plugin_manager.py`**
   - Define `BaseForgePlugin` abstract class.
   - Implement `PluginManager` with `importlib` and `pkgutil` dynamic loading.
   - Implement plugin lifecycle methods (`register`, `activate`, `deactivate`, `filter_action`, `route_action`, `list_plugins`).

2. **Step 2: Implement `src/plugins/dev_mode.py`**
   - Subclass `BaseForgePlugin`.
   - Implement window handle interception, shell command execution, and file I/O operations.

3. **Step 3: Implement `src/plugins/student_mode.py`**
   - Subclass `BaseForgePlugin`.
   - Implement study session toggles, application/URL blacklists, and focus window bounding box coordinate checks.

4. **Step 4: Integrate into `src/agent_loop.py`**
   - Initialize global `plugin_manager`.
   - Add plugin scanning during startup.
   - Add `filter_action()` guardrail check and `route_action()` execution check in `execute_task_plan()`.

5. **Step 5: Add Unit & Integration Tests**
   - Create `tests/test_plugin_system.py` to test plugin discovery, lifecycle management, dev mode execution, student mode filtering, and `agent_loop` integration.

---

## 4. Verification Plan
- Run unit tests for `PluginManager`, `DevModePlugin`, and `StudentModePlugin`.
- Execute `pytest tests/test_plugin_system.py`.
- Run existing architectural tests (`python tests/test_architecture.py`) to verify no regressions.
