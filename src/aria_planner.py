import os
import json
from src.logger import logger
from src.vlm_pipeline.tests.run_inference import run_vlm_inference

class AriaPlanner:
    """
    ARIA Planner (Advanced Reasoning & Intelligence Architecture)
    Responsible for generating high-level action plans by combining Semantic Memory (RAG/Skills),
    Episodic Memory (User Preferences), Dynamic Plugins context, and visual data.
    """
    
    def __init__(self, memory_mgr, plugin_mgr):
        self.memory_mgr = memory_mgr
        self.plugin_mgr = plugin_mgr

    def generate_plan(self, instruction: str, screenshot_path: str, context_history: list) -> list:
        """
        Generates an action plan by injecting memories and querying the VLM.
        """
        logger.info(f"[ARIA Planner] Ingesting instruction: '{instruction}'")

        # 1. Gather Memories
        semantic_memory = self.memory_mgr.get_semantic_memory(instruction)
        episodic_memory = self.memory_mgr.get_episodic_memory()
        
        # 2. Gather Plugin Capabilities
        plugin_context = self.plugin_mgr.get_active_plugins_context() if hasattr(self.plugin_mgr, 'get_active_plugins_context') else ""

        # 3. Construct ARIA Prompt
        aria_prompt = f"Goal: {instruction}\n"
        
        if semantic_memory:
            aria_prompt += f"\n[Learned Skills (Semantic Memory)]:\n{semantic_memory}\n"
            
        if episodic_memory:
            aria_prompt += f"\n[User Preferences (Episodic Memory)]:\n{json.dumps(episodic_memory, indent=2)}\n"
            
        if plugin_context:
            aria_prompt += f"\n[Available Plugins]:\n{plugin_context}\n"
            
        if context_history:
            history_str = json.dumps([{"action": h["action"], "target": h["target"]} for h in context_history], indent=2)
            aria_prompt += f"\n[Recent Actions Context]:\n{history_str}\n"

        aria_prompt += "\nBased on the screen and the above context, output ONLY a valid JSON array of actions to achieve the goal."

        logger.info(f"[ARIA Planner] Context assembled. Calling Model (Moondream2)...")
        
        # 4. Generate Plan (Currently defaults to local Moondream2 via unified pipeline)
        # In the future, this can easily route to a local Hermes 8B GGUF or external API
        vlm_result = run_vlm_inference(screenshot_path, aria_prompt)

        # 5. Parse output
        if isinstance(vlm_result, list):
            plan = vlm_result
        elif isinstance(vlm_result, dict):
            if "plan" in vlm_result and isinstance(vlm_result["plan"], list):
                plan = vlm_result["plan"]
            elif "actions" in vlm_result and isinstance(vlm_result["actions"], list):
                plan = vlm_result["actions"]
            else:
                plan = [vlm_result]
        else:
            plan = [{"raw_output": str(vlm_result)}]

        logger.info(f"[ARIA Planner] Generated Action Plan: {plan}")
        return plan
