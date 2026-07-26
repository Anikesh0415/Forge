import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.macro_orchestrator import macro_orchestrator

prompts = [
    """Begin the 'Legacy Database Migration' protocol. Open the local directory C:\\Legacy_Records\\ containing 10,000 nested folders, each representing a client.
For every single folder, sequentially execute the following loop:
Open the folder, locate the PDF named client_data.pdf, and open it.
Use Semantic Copy (Ctrl+A) to grab all raw text and send it to the Hermes LLM Data Cleaner to extract the 'Account ID' and 'Current Balance'.
Open the target CRM web portal in Chrome.
Use OCR (PyTesseract) to locate the 'Global Search' bar, click it, and paste the 'Account ID'.
Wait for the client profile to load. Use VISTA Moondream to visually verify that the profile picture and 'Active' status badge have rendered on the screen.
If Moondream returns a Condition Failed (e.g., 'Not Found' or 'Inactive'), log 'FAILED' in a master audit.csv file and immediately move to the next client folder.
If Moondream returns Condition Met, use normal UI actions to scroll down, click the 'Update Balance' text box, and type the cleaned 'Current Balance'.
Click 'Save'.
Use Moondream to verify the green 'Saved Successfully' banner appears.
Close the CRM tab, close the PDF, and proceed to the next folder.
Continue this exact loop without stopping until all 10,000 folders have been processed."""
]

def run_tests():
    print("# Full Divided-Brain Pipeline Test Results\n", flush=True)
    macro_orchestrator.core.use_mock = True
    for i, prompt in enumerate(prompts):
        print(f"## Test {i+1}: 80+ Action Prompt Processing", flush=True)
        try:
            print("### Phase 1: Macro Orchestrator (Architect Brain)", flush=True)
            macro_plan = macro_orchestrator.analyze_instruction(prompt)
            assert isinstance(macro_plan, dict)
            assert "is_loop" in macro_plan
            print(json.dumps(macro_plan, indent=2), flush=True)

        except Exception as e:
            print(f"### Error:\n{e}", flush=True)
            raise e
        print("\n---\n", flush=True)

def test_stress():
    run_tests()

if __name__ == "__main__":
    run_tests()

