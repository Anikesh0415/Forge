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

# 7. UNIVERSAL PARAMETERIZED MACROS
universal_skills = [
    {"intent": "open {app}", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "{app}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {site}", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://{site}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "browse {site}", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://{site}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "send {message} to {contact} on whatsapp", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "whatsapp"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"},
        {"type": "sleep", "ms": 4000},
        {"type": "key", "key": "ctrl+f"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "{contact}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "{message}"},
        {"type": "sleep", "ms": 500},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "play {song} on spotify", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "spotify"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"},
        {"type": "sleep", "ms": 4000},
        {"type": "key", "key": "ctrl+l"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "{song}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"},
        {"type": "sleep", "ms": 1000},
        {"type": "key", "key": "tab"},
        {"type": "sleep", "ms": 100},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "google {query}", "actions": [
        {"type": "key", "key": "win"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"},
        {"type": "sleep", "ms": 2000},
        {"type": "key", "key": "ctrl+l"},
        {"type": "sleep", "ms": 500},
        {"type": "type", "text": "{query}"},
        {"type": "sleep", "ms": 500},
        {"type": "key", "key": "enter"}
    ]}
]

skills.extend(universal_skills)


# AUTO-GENERATED 200+ UNIVERSAL MACROS
more_universal = [
    {"intent": "search {query} on youtube", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.youtube.com/results?search_query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on amazon", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.amazon.com/s?k={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ebay", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ebay.com/sch/i.html?_nkw={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on reddit", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.reddit.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on wikipedia", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://en.wikipedia.org/wiki/Special:Search?search={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on github", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://github.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on stackoverflow", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://stackoverflow.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on twitter", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://twitter.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on x", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://twitter.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on facebook", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.facebook.com/search/top/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on linkedin", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.linkedin.com/search/results/all/?keywords={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on pinterest", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.pinterest.com/search/pins/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on netflix", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.netflix.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on hulu", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.hulu.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on disney plus", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.disneyplus.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on prime video", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.amazon.com/s?k={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on twitch", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.twitch.tv/search?term={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open spotify", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://open.spotify.com/search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on soundcloud", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://soundcloud.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on imdb", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.imdb.com/find?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on bing", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.bing.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on yahoo", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://search.yahoo.com/search?p={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on duckduckgo", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://duckduckgo.com/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on baidu", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.baidu.com/s?wd={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on yandex", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://yandex.com/search/?text={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on chatgpt", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://chatgpt.com/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on claude", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://claude.ai/new?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on perplexity", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.perplexity.ai/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on phind", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.phind.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on you", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://you.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on quora", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.quora.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on medium", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://medium.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on cnn", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://edition.cnn.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on bbc", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.bbc.co.uk/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on fox news", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.foxnews.com/search-results/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on nytimes", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.nytimes.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on wsj", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.wsj.com/search?keyword={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on the guardian", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.theguardian.com/info/developer-blog/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on forbes", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.forbes.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on bloomberg", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.bloomberg.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on reuters", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.reuters.com/search/news?blob={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open al jazeera", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.aljazeera.com/search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on walmart", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.walmart.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on target", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.target.com/s?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on best buy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.bestbuy.com/site/searchpage.jsp?st={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open home depot", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.homedepot.com/s/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on lowes", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.lowes.com/search?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on costco", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.costco.com/CatalogSearch?dept=All&keyword={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open macys", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.macys.com/shop/featured/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on nordstrom", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.nordstrom.com/sr?origin=keywordsearch&keyword={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ikea", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ikea.com/us/en/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on wayfair", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.wayfair.com/keyword.php?keyword={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on etsy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.etsy.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on aliexpress", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.aliexpress.com/wholesale?SearchText={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on alibaba", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.alibaba.com/trade/search?SearchText={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open zillow", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.zillow.com/homes/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open trulia", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.trulia.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open realtor", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.realtor.com/realestateandhomes-search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on craigslist", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://craigslist.org/search/sss?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on tripadvisor", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.tripadvisor.com/Search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open expedia", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.expedia.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open kayak", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.kayak.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on booking", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.booking.com/searchresults.html?ss={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open airbnb", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.airbnb.com/s/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open uber", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.uber.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open lyft", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.lyft.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on yelp", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.yelp.com/search?find_desc={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open doordash", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.doordash.com/search/store/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ubereats", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ubereats.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on grubhub", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.grubhub.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on postmates", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://postmates.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on instacart", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.instacart.com/store/s?k={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on coursera", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.coursera.org/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on udemy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.udemy.com/courses/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on edx", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.edx.org/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on khan academy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.khanacademy.org/search?page_search_query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on skillshare", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.skillshare.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on masterclass", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.masterclass.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on codecademy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.codecademy.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on datacamp", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.datacamp.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on leetcode", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://leetcode.com/problemset/all/?search={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open hackerrank", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.hackerrank.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on codewars", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.codewars.com/users/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on npm", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.npmjs.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on pypi", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://pypi.org/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on docker hub", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://hub.docker.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on crates", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://crates.io/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on nuget", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.nuget.org/packages?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on maven", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mvnrepository.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on packagist", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://packagist.org/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on rubygems", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://rubygems.org/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on godoc", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://pkg.go.dev/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on mdn", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://developer.mozilla.org/en-US/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open w3schools", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.w3schools.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open geeksforgeeks", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.geeksforgeeks.org/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on tutorialspoint", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.tutorialspoint.com/search.htm?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open javatpoint", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.javatpoint.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on fandom", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://community.fandom.com/wiki/Special:Search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ign", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ign.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on gamespot", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.gamespot.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on polygon", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.polygon.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on kotaku", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://kotaku.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on pcgamer", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.pcgamer.com/search/?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on rockpapershotgun", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.rockpapershotgun.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on eurogamer", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.eurogamer.net/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on destructoid", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.destructoid.com/?s={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on giantbomb", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.giantbomb.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on gamefaqs", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://gamefaqs.gamespot.com/search?game={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open metacritic", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.metacritic.com/search/all/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on rotten tomatoes", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.rottentomatoes.com/search?search={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on vimeo", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://vimeo.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open dailymotion", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.dailymotion.com/search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on tiktok", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.tiktok.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open snapchat", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.snapchat.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open instagram", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.instagram.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open whatsapp", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://web.whatsapp.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open telegram", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://web.telegram.org/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open discord", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://discord.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open slack", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://slack.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open teams", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://teams.microsoft.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open zoom", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://zoom.us/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open skype", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.skype.com/en/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open webex", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.webex.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open meet", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://meet.google.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open gmail", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mail.google.com/mail/u/0/#search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open outlook", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://outlook.live.com/mail/0/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open yahoo mail", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mail.yahoo.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open protonmail", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://protonmail.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open icloud", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.icloud.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on drive", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://drive.google.com/drive/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open dropbox", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.dropbox.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open onedrive", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://onedrive.live.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open box", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.box.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open mega", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://mega.io/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open mediafire", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.mediafire.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on civitai", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://civitai.com/search/models?sortBy=models_v9&query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on huggingface", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://huggingface.co/search/full-text?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open poe", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://poe.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on replit", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://replit.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]}
]
skills.extend(more_universal)


# AUTO-GENERATED 60+ MORE UNIVERSAL MACROS
more_universal_2 = [
    {"intent": "search {query} on walgreens", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.walgreens.com/search/results.jsp?Ntt={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on cvs", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.cvs.com/search/?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on rite aid", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.riteaid.com/shop/catalogsearch/result/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on sephora", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.sephora.com/search?keyword={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ulta", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ulta.com/search?search={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on gamestop", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.gamestop.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open barnes and noble", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.barnesandnoble.com/s/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on zappos", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.zappos.com/search?term={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on overstock", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.overstock.com/search?keywords={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on chewy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.chewy.com/s?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on petco", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.petco.com/shop/SearchDisplay?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on petsmart", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.petsmart.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open staples", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.staples.com/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on office depot", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.officedepot.com/catalog/search.do?Ntt={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on dick's sporting goods", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.dickssportinggoods.com/f/?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on rei", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.rei.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on foot locker", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.footlocker.com/search?query={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on nike", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.nike.com/w?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on adidas", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.adidas.com/us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on under armour", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.underarmour.com/en-us/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on puma", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.puma.com/us/en/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on h&m", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www2.hm.com/en_us/search-results.html?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on zara", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.zara.com/us/en/search?searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open forever 21", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.forever21.com/us/shop/Search/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on asos", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.asos.com/us/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open shein", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://us.shein.com/pdsearch/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on boohoo", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://us.boohoo.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on missguided", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.missguidedus.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on nasty gal", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.nastygal.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on fashion nova", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.fashionnova.com/pages/search-results-page?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on urban outfitters", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.urbanoutfitters.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on anthropologie", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.anthropologie.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on free people", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.freepeople.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on gap", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.gap.com/browse/search.do?searchText={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on old navy", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://oldnavy.gap.com/browse/search.do?searchText={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on banana republic", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://bananarepublic.gap.com/browse/search.do?searchText={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on j.crew", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.jcrew.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on madewell", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.madewell.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on abercrombie & fitch", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.abercrombie.com/shop/us/search?departmentCategoryId=10000&searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on hollister", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.hollisterco.com/shop/us/search?departmentCategoryId=10000&searchTerm={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "open american eagle", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ae.com/us/en/s/"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on aeropostale", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.aeropostale.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on pacsun", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.pacsun.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on zumiez", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.zumiez.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on tillys", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.tillys.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on vans", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.vans.com/en-us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on converse", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.converse.com/shop/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on new balance", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.newbalance.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on asics", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.asics.com/us/en-us/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on brooks", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.brooksrunning.com/en_us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on saucony", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.saucony.com/en/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on hoka", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.hoka.com/en/us/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on on running", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.on-running.com/en-us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on merrell", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.merrell.com/en/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on keen", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.keenfootwear.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on columbia", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.columbia.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on the north face", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.thenorthface.com/en-us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on patagonia", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.patagonia.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on marmot", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.marmot.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on arcteryx", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://arcteryx.com/us/en/c/search?search={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on salomon", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.salomon.com/en-us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on timberland", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.timberland.com/en-us/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on drmartens", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.drmartens.com/us/en/search/?text={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on ugg", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.ugg.com/search/?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]},
    {"intent": "search {query} on crocs", "actions": [
        {"type": "key", "key": "win+r"},
        {"type": "sleep", "ms": 800},
        {"type": "type", "text": "brave https://www.crocs.com/search?q={query}"},
        {"type": "sleep", "ms": 800},
        {"type": "key", "key": "enter"}
    ]}
]
skills.extend(more_universal_2)

# Write to disk
for skill in skills:
    safe_name = skill["intent"].replace(" ", "_").replace("{", "").replace("}", "")
    data = {
        "name": skill["intent"],
        "actions": skill["actions"]
    }
    with open(f"skills_db/learned_{safe_name}.json", "w") as f:
        json.dump(data, f, indent=2)

print(f"Generated {len(skills)} pre-trained skills in skills_db!")
