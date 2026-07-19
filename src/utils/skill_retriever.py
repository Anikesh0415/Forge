import json
import os
from src.logger import logger

SKILLS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'skills.json')

def load_skills():
    """Loads the skills database from the JSON file."""
    if not os.path.exists(SKILLS_FILE):
        return []
    try:
        with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[SkillRetriever] Failed to load skills database: {e}")
        return []

def get_relevant_examples(instruction: str, max_examples: int = 2) -> str:
    """
    Retrieves the most relevant skill examples based on keyword matching.
    Returns a formatted string to inject into the LLM prompt.
    """
    skills = load_skills()
    if not skills:
        return ""
        
    instruction_lower = instruction.lower()
    scored_skills = []
    
    for skill in skills:
        score = 0
        for kw in skill.get("keywords", []):
            if kw.lower() in instruction_lower:
                score += 1
        
        if score > 0:
            scored_skills.append((score, skill))
            
    # Sort by score descending
    scored_skills.sort(key=lambda x: x[0], reverse=True)
    
    # Take top N
    top_skills = [skill for score, skill in scored_skills[:max_examples]]
    
    if not top_skills:
        return ""
        
    # Format for injection
    injection = "\nRELEVANT SKILL EXAMPLES:\n"
    for idx, skill in enumerate(top_skills):
        injection += f"--- Example {idx+1}: {skill.get('description', 'Action Sequence')} ---\n"
        injection += f"{skill.get('example_sequence', '')}\n\n"
        
    return injection
