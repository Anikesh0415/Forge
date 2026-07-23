import time
import textwrap
import asyncio
from src.executors.base_executor import BaseExecutor
from src.llm_core import LocalLLMCore
from src.logger import logger

class DynamicExecutor(BaseExecutor):
    """
    Dynamic Executor for Forge.
    Instead of relying on hardcoded macros, it uses an LLM to generate
    and execute PyAutoGUI scripts on the fly for novel tasks.
    """

    def __init__(self):
        super().__init__(name="DynamicExecutor")
        self.llm = LocalLLMCore(use_mock=False)

    def can_handle(self, action_type: str, step_data: dict) -> bool:
        return action_type.lower() == "dynamic_task"

    async def execute(self, action_type: str, step_data: dict) -> tuple[bool, str]:
        target_task = step_data.get("target", "")
        if not target_task:
            return False, "No target task provided for dynamic execution."

        logger.info(f"[{self.name}] Analyzing dynamic task: {target_task}")

        prompt = textwrap.dedent(f"""
        You are an expert Python automation developer.
        Write a robust python script using `pyautogui`, `time`, and `webbrowser` to fulfill the following user request:
        "{target_task}"
        
        Rules:
        - Output ONLY valid, executable Python code.
        - Do NOT include markdown blocks like ```python or ```. Just the raw python code.
        - Add small `time.sleep()` delays between GUI interactions.
        - If opening a website, use `webbrowser.open('url')`.
        - Keep the script concise and focused.
        """)

        try:
            # Get code from LLM
            code_response = await self.llm.process_vision(prompt, []) # process_vision returns raw text instead of strictly parsed JSON
            if not code_response:
                return False, "LLM failed to generate code."
            
            # Clean the code just in case it added markdown
            code = code_response.replace('```python', '').replace('```', '').strip()
            
            logger.info(f"[{self.name}] Executing dynamic code:\n{code}")
            
            # Execute the code in an isolated namespace with safe imports
            import pyautogui
            import webbrowser
            namespace = {
                "time": time,
                "pyautogui": pyautogui,
                "webbrowser": webbrowser
            }
            
            # Run in a separate thread so it doesn't block the async event loop
            def run_code():
                exec(code, namespace)
                
            await asyncio.to_thread(run_code)
            
            return True, f"Dynamically executed: {target_task}"
        except Exception as e:
            logger.error(f"[{self.name}] Dynamic execution failed: {e}")
            return False, f"Dynamic execution failed: {str(e)}"
