import json
import os

os.makedirs("skills_db", exist_ok=True)
skills = []

def generate_open_macro(intent_name, run_cmd_text):
    return {
        "intent": intent_name,
        "actions": [
            {"type": "key", "key": "win"},
            {"type": "sleep", "ms": 800},
            {"type": "type", "text": run_cmd_text},
            {"type": "sleep", "ms": 800},
            {"type": "key", "key": "enter"}
        ]
    }

# 1. EVERY WINDOWS / SYSTEM APP
windows_apps = [
    "calculator", "calendar", "camera", "clock", "cortana", "feedback hub",
    "get help", "groove music", "mail", "maps", "messaging", "mixed reality portal",
    "movies & tv", "paint 3d", "people", "photos", "print 3d", "settings",
    "skype", "snip & sketch", "snipping tool", "solitaire", "sticky notes",
    "tips", "voice recorder", "weather", "windows security", "xbox", "xbox game bar",
    "your phone", "3d viewer", "alarms & clock", "command prompt", "control panel",
    "device manager", "disk management", "event viewer", "file explorer",
    "microsoft edge", "microsoft store", "notepad", "powershell", "registry editor",
    "resource monitor", "run", "services", "system information", "task manager",
    "windows memory diagnostic", "wordpad", "steps recorder", "character map",
    "math input panel", "quick assist", "remote desktop connection", "windows fax and scan",
    "windows media player", "xps viewer", "paint", "calculator"
]

for app in windows_apps:
    skills.append(generate_open_macro(f"open {app}", app))

# 2. SOCIAL APPS / COMMUNICATION
social_apps = [
    "discord", "telegram", "whatsapp", "slack", "zoom", "microsoft teams",
    "skype", "viber", "signal", "line", "wechat", "kik", "snapchat", "instagram",
    "facebook messenger", "twitter", "reddit", "pinterest", "tumblr", "linkedin",
    "groupme", "cisco webex", "google meet", "teamspeak", "mumble", "guilded"
]

for app in social_apps:
    skills.append(generate_open_macro(f"open {app}", app))

# 3. WEBSITES (Top 200+)
websites = [
    "google", "youtube", "facebook", "twitter", "instagram", "baidu", "wikipedia",
    "yandex", "yahoo", "xvideos", "whatsapp", "pornhub", "amazon", "xhamster",
    "live", "netflix", "tiktok", "docomo", "bing", "reddit", "office", "linkedin",
    "dzen", "vk", "samsung", "turbopages", "mail", "naver", "discord", "twitch",
    "bilibili", "weather", "yahoo.co.jp", "qq", "yandex.ru", "pinterest", "zoom",
    "duckduckgo", "quora", "globo", "ebay", "msn", "stripchat", "roblox", "aliexpress",
    "canva", "bbc", "nytimes", "cnn", "foxnews", "espn", "imdb", "apple", "microsoft",
    "github", "stackoverflow", "chatgpt", "openai", "craigslist", "walmart",
    "target", "bestbuy", "hulu", "disneyplus", "hbomax", "primevideo", "paypal",
    "chase", "bankofamerica", "wellsfargo", "capitalone", "zillow", "realtor",
    "booking", "expedia", "airbnb", "tripadvisor", "yelp", "ign", "gamespot",
    "pcgamer", "polygon", "kotaku", "theverge", "engadget", "wired", "techcrunch",
    "medium", "vimeo", "dailymotion", "soundcloud", "bandcamp", "patreon", "kickstarter",
    "indiegogo", "gofundme", "etsy", "shopify", "wordpress", "wix", "squarespace",
    "weebly", "blogger", "tumblr", "flickr", "imgur", "giphy", "deviantart",
    "artstation", "behance", "dribbble", "fiverr", "upwork", "freelancer", "toptal",
    "guru", "peopleperhour", "99designs", "udemy", "coursera", "edx", "khanacademy",
    "datacamp", "leetcode", "hackerrank", "codewars", "projecteuler", "spoj",
    "claude", "perplexity", "anthropic", "midjourney", "huggingface", "replit",
    "poe", "civitai"
]

for site in websites:
    skills.append(generate_open_macro(f"open {site}", f"{site}.com"))

# 4. GAMES & GAMING PLATFORMS
gaming = [
    "steam", "epic games", "battlenet", "origin", "ubisoft connect", "gog galaxy",
    "riot client", "league of legends", "csgo", "dota 2", "apex legends", "fortnite",
    "roblox", "genshin impact", "overwatch", "world of warcraft", "final fantasy xiv",
    "cyberpunk 2077", "gta v", "red dead redemption 2", "witcher 3", "skyrim",
    "fallout 4", "valorant", "minecraft", "terraria", "stardew valley", "among us",
    "fall guys", "rocket league", "hades", "hollow knight", "celeste", "dead cells",
    "slay the spire", "binding of isaac", "enter the gungeon", "spelunky", "risk of rain 2",
    "factorio", "rimworld", "dyson sphere program", "satisfactory", "subnautica"
]

for game in gaming:
    skills.append(generate_open_macro(f"open {game}", game))

# 5. DEV TOOLS & PRODUCTIVITY
dev_tools = [
    "vscode", "visual studio", "intellij", "pycharm", "webstorm", "eclipse",
    "sublime text", "android studio", "xcode", "vim", "emacs", "nano", "gedit",
    "notepad++", "atom", "brackets", "postman", "insomnia", "docker", "kubernetes",
    "virtualbox", "vmware", "hyper-v", "putty", "mobaxterm", "teraterm", "winscp",
    "filezilla", "cyberduck", "wireshark", "fiddler", "charles", "burp suite",
    "git bash", "github desktop", "sourcetree", "gitkraken", "tortoisegit",
    "notion", "evernote", "obsidian", "todoist", "ticktick", "anydesk", "teamviewer",
    "winrar", "7zip", "rufus", "blender", "premiere", "photoshop", "illustrator",
    "after effects", "figma", "word", "excel", "powerpoint", "access", "publisher",
    "cursor", "zed", "warp", "fleet", "datagrip", "rubymine", "clion"
]

for tool in dev_tools:
    skills.append(generate_open_macro(f"open {tool}", tool))

# 6. SYSTEM SETTINGS (ms-settings URIs)
settings = [
    ("display settings", "ms-settings:display"),
    ("sound settings", "ms-settings:sound"),
    ("notifications", "ms-settings:notifications"),
    ("power settings", "ms-settings:powersleep"),
    ("storage settings", "ms-settings:storagesense"),
    ("wifi settings", "ms-settings:network-wifi"),
    ("ethernet settings", "ms-settings:network-ethernet"),
    ("bluetooth settings", "ms-settings:bluetooth"),
    ("printers", "ms-settings:printers"),
    ("mouse settings", "ms-settings:mousetouchpad"),
    ("keyboard settings", "ms-settings:typing"),
    ("pen settings", "ms-settings:pen"),
    ("personalization", "ms-settings:personalization"),
    ("background settings", "ms-settings:personalization-background"),
    ("lock screen settings", "ms-settings:lockscreen"),
    ("themes settings", "ms-settings:themes"),
    ("fonts", "ms-settings:fonts"),
    ("apps and features", "ms-settings:appsfeatures"),
    ("default apps", "ms-settings:defaultapps"),
    ("startup apps", "ms-settings:startupapps"),
    ("accounts", "ms-settings:emailandaccounts"),
    ("sign-in options", "ms-settings:signinoptions"),
    ("family settings", "ms-settings:family"),
    ("time and language", "ms-settings:dateandtime"),
    ("region settings", "ms-settings:regionlanguage"),
    ("gaming settings", "ms-settings:gaming-gamebar"),
    ("game mode", "ms-settings:gaming-gamemode"),
    ("accessibility", "ms-settings:easeofaccess-narrator"),
    ("privacy", "ms-settings:privacy"),
    ("location privacy", "ms-settings:privacy-location"),
    ("camera privacy", "ms-settings:privacy-webcam"),
    ("microphone privacy", "ms-settings:privacy-microphone"),
    ("windows update", "ms-settings:windowsupdate"),
    ("windows security", "ms-settings:windowsdefender"),
    ("troubleshoot", "ms-settings:troubleshoot")
]

for name, uri in settings:
    skills.append({
        "intent": f"open {name}",
        "actions": [
            {"type": "key", "key": "win+r"},
            {"type": "sleep", "ms": 800},
            {"type": "type", "text": uri},
            {"type": "sleep", "ms": 800},
            {"type": "key", "key": "enter"}
        ]
    })

advanced_skills = [
    # SPOTIFY
    {"intent": "play spotify", "actions": [{"type": "key", "key": "playpause"}]},
    {"intent": "pause spotify", "actions": [{"type": "key", "key": "playpause"}]},
    {"intent": "next track", "actions": [{"type": "key", "key": "audio_next"}]},
    {"intent": "previous track", "actions": [{"type": "key", "key": "audio_prev"}]},
    {"intent": "volume up", "actions": [{"type": "key", "key": "audio_vol_up"}]},
    {"intent": "volume down", "actions": [{"type": "key", "key": "audio_vol_down"}]},
    {"intent": "mute volume", "actions": [{"type": "key", "key": "audio_mute"}]},
    
    # GMAIL
    {"intent": "open gmail", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mail.google.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "compose email", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mail.google.com/mail/u/0/#inbox?compose=new"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    
    # GOOGLE
    {"intent": "search google", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://google.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},

    # REDDIT
    {"intent": "search reddit", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://reddit.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},

    # INSTAGRAM
    {"intent": "open instagram", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://instagram.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "instagram messages", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://instagram.com/direct"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},

    # WHATSAPP
    {"intent": "whatsapp web", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://web.whatsapp.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},

    # ONENOTE
    {"intent": "open onenote", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "onenote"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "new page in onenote", "actions": [
        {"type": "key", "key": "ctrl+n"}
    ]},

    # NOTION
    {"intent": "open notion", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "notion"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "new page in notion", "actions": [
        {"type": "key", "key": "ctrl+n"}
    ]},
    {"intent": "search notion", "actions": [
        {"type": "key", "key": "ctrl+p"}
    ]},
    
    # NOTEPAD
    {"intent": "save notepad", "actions": [
        {"type": "key", "key": "ctrl+s"}
    ]},
    {"intent": "save as notepad", "actions": [
        {"type": "key", "key": "ctrl+shift+s"}
    ]},
    {"intent": "find in notepad", "actions": [
        {"type": "key", "key": "ctrl+f"}
    ]},
    {"intent": "replace in notepad", "actions": [
        {"type": "key", "key": "ctrl+h"}
    ]},

    # GEMINI ANTIGRAVITY (Itself!)
    {"intent": "open gemini", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://gemini.google.com"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "ask antigravity", "actions": [
        {"type": "key", "key": "ctrl+k"}
    ]},
    {"intent": "lock computer", "actions": [
        {"type": "key", "key": "win+l"}
    ]},
    {"intent": "open task manager", "actions": [
        {"type": "key", "key": "ctrl+shift+esc"}
    ]},
    {"intent": "show desktop", "actions": [
        {"type": "key", "key": "win+d"}
    ]},
    {"intent": "open clipboard history", "actions": [
        {"type": "key", "key": "win+v"}
    ]},
    {"intent": "take screenshot", "actions": [
        {"type": "key", "key": "win+shift+s"}
    ]},
    {"intent": "open emoji keyboard", "actions": [
        {"type": "key", "key": "win+."}
    ]}
]

skills.extend(advanced_skills)

# Write to disk
for skill in skills:
    safe_name = skill["intent"].replace(" ", "_")
    data = {
        "name": skill["intent"],
        "actions": skill["actions"]
    }
    with open(f"skills_db/learned_{safe_name}.json", "w") as f:
        json.dump(data, f, indent=2)

print(f"Generated {len(skills)} pre-trained skills in skills_db!")
