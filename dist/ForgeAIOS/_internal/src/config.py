import os
import json


# Comprehensive Universal Service Map
_default_browser_map = {
    # AI Portals
    "antigravity": "https://antigravity.google.com",
    "gemini": "https://gemini.google.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "perplexity": "https://perplexity.ai",
    "copilot": "https://copilot.microsoft.com",
    "deepseek": "https://chat.deepseek.com",
    "mistral": "https://chat.mistral.ai",
    "huggingface": "https://huggingface.co",

    # Search & Media
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "yt": "https://youtube.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://netflix.com",
    "twitch": "https://twitch.tv",

    # Social & Community
    "telegram": "https://web.telegram.org",
    "discord": "https://discord.com/app",
    "reddit": "https://reddit.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",

    # Developer & Productivity
    "github": "https://github.com",
    "gitlab": "https://gitlab.com",
    "stackoverflow": "https://stackoverflow.com",
    "notion": "https://notion.so",
    "figma": "https://figma.com",
    "gmail": "https://mail.google.com",
}
try:
    BROWSER_APP_MAP = json.loads(os.environ.get("BROWSER_APP_MAP", "{}"))
    if not BROWSER_APP_MAP:
        BROWSER_APP_MAP = _default_browser_map
except Exception:
    BROWSER_APP_MAP = _default_browser_map

# Phase 7 & 8: Acoustic Neutrality
try:
    WAKE_WORDS = json.loads(
        os.environ.get("WAKE_WORDS", '["servent", "servant", "forge"]')
    )
except Exception:
    WAKE_WORDS = ["servent", "servant", "forge"]

NOISE_GATE_THRESHOLD = float(os.environ.get("NOISE_GATE_THRESHOLD", "0.05"))
