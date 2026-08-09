import json
import os

os.makedirs("skills_db", exist_ok=True)

skills = []

# List of 100 popular Windows applications and games
apps = [
    "notepad", "word", "excel", "powerpoint", "chrome", "firefox", "brave", "edge", 
    "steam", "valorant", "minecraft", "obs", "spotify", "slack", "zoom", "teams",
    "vscode", "visual studio", "cmd", "powershell", "settings", "control panel",
    "paint", "calculator", "calendar", "mail", "photos", "weather", "clock",
    "discord", "telegram", "whatsapp", "vlc", "epic games", "battlenet", "origin",
    "blender", "premiere", "photoshop", "illustrator", "after effects", "figma",
    "notion", "evernote", "obsidian", "todoist", "ticktick", "anydesk", "teamviewer",
    "winrar", "7zip", "rufus", "file explorer", "task manager", "device manager"
]

# Generate basic "open" macros for all 100 apps
for app in apps:
    skills.append({
        "intent": f"open {app}",
        "actions": [
            {"type": "key", "key": "win"},
            {"type": "sleep", "ms": 800},
            {"type": "type", "text": app},
            {"type": "sleep", "ms": 800},
            {"type": "key", "key": "enter"}
        ]
    })

# Add specialized / complex macros
specialized_skills = [
    {
        "intent": "mute discord",
        "actions": [{"type": "key", "key": "ctrl+shift+m"}]
    },
    {
        "intent": "deafen discord",
        "actions": [{"type": "key", "key": "ctrl+shift+d"}]
    },
    {
        "intent": "lock pc",
        "actions": [{"type": "key", "key": "win+l"}]
    },
    {
        "intent": "open task manager",
        "actions": [{"type": "key", "key": "ctrl+shift+esc"}]
    },
    {
        "intent": "take screenshot",
        "actions": [{"type": "key", "key": "win+shift+s"}]
    },
    {
        "intent": "open clipboard",
        "actions": [{"type": "key", "key": "win+v"}]
    },
    {
        "intent": "show desktop",
        "actions": [{"type": "key", "key": "win+d"}]
    },
    {
        "intent": "new virtual desktop",
        "actions": [{"type": "key", "key": "win+ctrl+d"}]
    },
    {
        "intent": "close virtual desktop",
        "actions": [{"type": "key", "key": "win+ctrl+f4"}]
    },
    {
        "intent": "switch virtual desktop right",
        "actions": [{"type": "key", "key": "win+ctrl+right"}]
    },
    {
        "intent": "switch virtual desktop left",
        "actions": [{"type": "key", "key": "win+ctrl+left"}]
    },
    {
        "intent": "open action center",
        "actions": [{"type": "key", "key": "win+a"}]
    },
    {
        "intent": "open emoji panel",
        "actions": [{"type": "key", "key": "win+."}]
    }
]

skills.extend(specialized_skills)

# Write them to the database
for skill in skills:
    safe_name = skill["intent"].replace(" ", "_")
    data = {
        "name": skill["intent"],
        "actions": skill["actions"]
    }
    with open(f"skills_db/learned_{safe_name}.json", "w") as f:
        json.dump(data, f, indent=2)

print(f"Generated {len(skills)} pre-trained skills in skills_db!")
