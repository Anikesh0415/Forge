import json
import re
import requests


# ---------------------------------------------------------------------------
# RESILIENT JSON PARSING HELPERS
# ---------------------------------------------------------------------------

def clean_and_parse_json(raw_text: str):
    """Strips markdown fences and whitespace before calling json.loads."""
    raw_text = raw_text.strip()
    # Strip opening fence (e.g. ```json or ```)
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1]
    # Strip closing fence
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("\n", 1)[0]
    return json.loads(raw_text.strip())


def extract_steps(parsed_data) -> list:
    """
    Self-healing converter: accepts a list or a dict wrapper and always
    returns a flat list of action steps.
    """
    if isinstance(parsed_data, list):
        return parsed_data

    if isinstance(parsed_data, dict):
        # Heuristic 1: look for common wrapper keys
        for key in ["steps", "plan", "actions", "task_steps", "sequence"]:
            if key in parsed_data and isinstance(parsed_data[key], list):
                print(f"[ARIA Parser] Extracted steps from dict key: '{key}'")
                return parsed_data[key]

        # Heuristic 2: single-step dict — wrap it in a list
        if "action" in parsed_data or "type" in parsed_data or "description" in parsed_data:
            print("[ARIA Parser] Wrapped single-action dict into list.")
            return [parsed_data]

    raise ValueError(f"Could not extract a valid steps list from: {type(parsed_data)}")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Phase 1: Downsized to 3B (2.2 GB RAM) so ARIA + VISTA fit simultaneously.
PLANNER_MODEL = "qwen2.5:3b-instruct-q4_K_M"

# ---------------------------------------------------------------------------
# ARIA SYSTEM PROMPT
# ---------------------------------------------------------------------------
PLANNER_SYSTEM_PROMPT = """You are ARIA, the Master Planner for a desktop automation system.
Break the user's request into a JSON action plan.

AVAILABLE ACTIONS (use ONLY these):
  {"action": "open_app",        "app": "<name>"}
  {"action": "navigate_browser","url": "<full_url>"}
  {"action": "type",            "text": "<text>",  "anchor_check": "<what VISTA should see after this>"}
  {"action": "key",             "key": "<key_name>","anchor_check": "<what VISTA should see after this>"}
  {"action": "copy_all"}
  {"action": "paste"}
  {"action": "click",           "x": <int>, "y": <int>}
  {"action": "scroll",          "amount": <int>}

STRICT RULES:
1. Output ONLY a raw JSON array. No markdown. No explanation. No trailing text.
2. NEVER use "click" if a keyboard shortcut achieves the same result.
3. After every "type" action into a search bar or AI prompt box, you MUST add a {"action":"key","key":"enter"} step.
4. Every "type" and "key" step MUST include an "anchor_check" field: a short description of what should be visible on screen after the step succeeds (e.g. "cursor in chat box", "YouTube homepage is visible").
5. Use "navigate_browser" (not "open_app") when the browser is already open and you need to go to a URL.
6. Do NOT output any keys other than those listed above.

EXAMPLE — "open gemini and ask it to write a poem":
[
  {"action": "open_app", "app": "gemini"},
  {"action": "type", "text": "write a poem about the ocean", "anchor_check": "text visible in Gemini prompt box"},
  {"action": "key", "key": "enter", "anchor_check": "Gemini response is loading or visible"}
]

EXAMPLE — "search for python tutorials on youtube":
[
  {"action": "open_app", "app": "youtube"},
  {"action": "type", "text": "python tutorials", "anchor_check": "search text visible in YouTube search bar"},
  {"action": "key", "key": "enter", "anchor_check": "YouTube search results page is visible"}
]"""


def generate_plan(instruction: str) -> list:
    """
    Calls ARIA (qwen2.5:3b) to generate a structured action plan.
    - keep_alive: -1  → model pinned in RAM permanently.
    - format: json    → Ollama enforces valid JSON at the token level.
    - temperature: 0  → Fully deterministic / no hallucinations.
    Uses clean_and_parse_json + extract_steps for bulletproof parsing.
    """
    prompt = f"User Request: {instruction}\nOutput the JSON action plan now."

    payload = {
        "model": PLANNER_MODEL,
        "system": PLANNER_SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": -1,
        "options": {
            "temperature": 0.0,
            "num_predict": 512,
        }
    }

    result_text = ""
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result_text = response.json().get("response", "").strip()

        # Step 1: Strip markdown fences and parse JSON
        parsed = clean_and_parse_json(result_text)

        # Step 2: Self-heal dict wrappers into a flat list
        return extract_steps(parsed)

    except json.JSONDecodeError as e:
        print(f"[ARIA Planner] JSON decode error: {e}")
        print(f"[ARIA Planner] Raw response was: {result_text[:300]}")
        # Last-resort regex fallback: find any [...] or {...} block
        for pattern in [r'\[.*?\]', r'\{.*?\}']:
            match = re.search(pattern, result_text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    return extract_steps(parsed)
                except Exception:
                    pass
        return []
    except ValueError as e:
        print(f"[ARIA Parser Error] {e}")
        return []
    except Exception as e:
        print(f"[ARIA Planner Error] {e}")
        return []


if __name__ == "__main__":
    plan = generate_plan("open notepad and type hello world")
    print(f"Generated Plan:\n{json.dumps(plan, indent=2)}")
