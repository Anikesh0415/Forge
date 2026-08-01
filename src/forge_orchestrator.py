import json
from src.logger import logger
from src.vlm_pipeline.tests.run_inference import run_text_inference, run_vlm_inference, GRAMMAR_PATH
from src.perception.ui_tree_parser import build_ui_tree
from src.perception.pruner import prune_ui_tree

class ForgeOrchestrator:
    """
    Implements the Proactive Hierarchical Planning loop (Manager-Worker-Critic)
    for Edge-Optimized UI Automation.
    """
    def __init__(self, memory_mgr, plugin_mgr):
        self.memory_mgr = memory_mgr
        self.plugin_mgr = plugin_mgr
        self.episodic_memory = []

    def generate_plan(self, instruction: str, screenshot_path: str, context_history: list) -> list:
        logger.info("[Orchestrator] Starting generate_plan (Single-Shot Blind OS Executor)")
        
        prompt = f"""You are a desktop automation agent.
Your task is: {instruction}

You operate in a blind OS mode without a UI tree. You MUST use keyboard shortcuts to accomplish the goal.

Generate ONLY a JSON array of atomic actions.
The ONLY supported actions are:
1. {{"action": "press", "key": "<key_name>"}} (e.g. "win", "enter", "tab", "esc", "space", "backspace")
2. {{"action": "type", "text": "<text_to_type>"}}
3. {{"action": "sleep", "time": <seconds>}}

CRITICAL RULE FOR OPENING APPS:
To open an app (like Gemini or WhatsApp), you MUST:
1. Press "win"
2. Sleep 1 second
3. Type the full name of the app (e.g. "Gemini" or "WhatsApp")
4. Sleep 1 second
5. Press "enter"

Example to open notepad and type hello:
[
  {{"action": "press", "key": "win"}},
  {{"action": "sleep", "time": 1}},
  {{"action": "type", "text": "notepad"}},
  {{"action": "sleep", "time": 1}},
  {{"action": "press", "key": "enter"}},
  {{"action": "sleep", "time": 2}},
  {{"action": "type", "text": "hello"}}
]

Now generate the exact JSON array for the task:"""

        try:
            # We don't use the restrictive grammar here so the model can output the full array structure
            result = run_text_inference(prompt)
            actions = []
            
            if isinstance(result, list):
                actions = result
            elif isinstance(result, dict) and "raw_output" in result:
                import re
                import json
                raw = result["raw_output"]
                # Robust parsing: Extract individual JSON objects matching the action schema
                # This bypasses issues where the LLM forgets commas between array items
                matches = re.finditer(r'\{[^{}]*"action"[^{}]*\}', raw)
                for m in matches:
                    try:
                        act = json.loads(m.group(0))
                        actions.append(act)
                    except json.JSONDecodeError:
                        pass
                        
            if actions:
                logger.info(f"[Orchestrator] Generated {len(actions)} executable actions.")
            else:
                logger.warning("[Orchestrator] Failed to parse any executable actions from LLM output.")
                
            return actions
        except Exception as e:
            logger.error(f"[Orchestrator] Execution planning failed: {e}")
            return []
