import os
import sys

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from src.logger import logger

from src.forge_orchestrator import ForgeOrchestrator
from src.memory_manager import MemoryManager
from src.plugin_manager import PluginManager

def test_prompt():
    print("Initializing components...")
    mem_mgr = MemoryManager()
    plug_mgr = PluginManager()
    
    orch = ForgeOrchestrator(mem_mgr, plug_mgr)
    
    prompt = "open gemini,and give it a prompt asking to generate letter to balram from anikesh asking how balram is?,now wait for the gemini to generate the letter, once letter is generated copy the letter and open whatsapp and paste the letter and send it to Balram."
    
    print(f"\nSubmitting prompt to Forge Orchestrator:\n'{prompt}'\n")
    
    try:
        plan = orch.generate_plan(prompt, "dummy.png", [])
        print("\n--- FINAL GENERATED PLAN ---")
        import json
        print(json.dumps(plan, indent=2))
        print("----------------------------\n")
        print("Test completely successfully without hanging!")
    except Exception as e:
        print(f"\nTest failed with exception: {e}")

if __name__ == "__main__":
    test_prompt()
