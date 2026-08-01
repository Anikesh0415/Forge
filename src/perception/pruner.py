from typing import List, Dict, Any
from src.logger import logger

def prune_ui_tree(tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggressively prunes the UI tree to reduce token count.
    Removes invisible, disabled, and purely structural nodes.
    """
    pruned = []
    
    # Types that are generally not interactive or just structural containers
    STRUCTURAL_TYPES = {"Pane", "Group", "Window", "Custom", "TitleBar"}
    
    for node in tree:
        # Filter 1: Must be visible and enabled
        if not node.get("is_visible") or not node.get("is_enabled"):
            continue
            
        # Filter 2: Must have a valid bounding box (not 0x0)
        rect = node.get("rect", {})
        if rect.get("width", 0) <= 0 or rect.get("height", 0) <= 0:
            continue
            
        # Filter 3: Semantic check - keep if it has a name, OR if it's an interactive type
        node_type = node.get("type", "")
        has_name = bool(node.get("name") and str(node["name"]).strip())
        
        is_interactive = node_type in {"Button", "Edit", "MenuItem", "ListItem", "Hyperlink", "CheckBox", "RadioButton", "TabItem", "ComboBox"}
        
        # If it's a structural type and has no name, we can probably drop it unless it's a known interactive exception
        if node_type in STRUCTURAL_TYPES and not has_name:
            continue
            
        if not has_name and not is_interactive:
            # Drop empty elements that aren't inherently interactive
            continue
            
        # Create a condensed version for the LLM
        condensed_node = {
            "id": node["id"],
            "type": node_type,
        }
        if has_name:
            condensed_node["name"] = node["name"]
            
        pruned.append(condensed_node)
        
    logger.info(f"[Pruner] Reduced tree from {len(tree)} to {len(pruned)} nodes.")
    return pruned
