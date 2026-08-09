import json
import os

os.makedirs("skills_db", exist_ok=True)

skills = []

apps = [
    "notepad", "word", "excel", "powerpoint", "chrome", "firefox", "brave", "edge", 
    "steam", "valorant", "minecraft", "obs", "spotify", "slack", "zoom", "teams",
    "vscode", "visual studio", "cmd", "powershell", "settings", "control panel",
    "paint", "calculator", "calendar", "mail", "photos", "weather", "clock",
    "discord", "telegram", "whatsapp", "vlc", "epic games", "battlenet", "origin",
    "blender", "premiere", "photoshop", "illustrator", "after effects", "figma",
    "notion", "evernote", "obsidian", "todoist", "ticktick", "anydesk", "teamviewer",
    "winrar", "7zip", "rufus", "file explorer", "task manager", "device manager",
    "postman", "git bash", "docker", "putty", "wireshark", "android studio",
    "intellij", "pycharm", "webstorm", "eclipse", "sublime text", "vmware",
    "virtualbox", "itunes", "netflix", "hulu", "amazon prime", "disney plus",
    "xbox", "ea app", "ubisoft connect", "gog galaxy", "riot client", "league of legends",
    "csgo", "dota 2", "apex legends", "fortnite", "roblox", "genshin impact",
    "overwatch", "world of warcraft", "final fantasy xiv", "cyberpunk 2077",
    "gta v", "red dead redemption 2", "witcher 3", "skyrim", "fallout 4"
]

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

websites = [
    "youtube.com", "google.com", "facebook.com", "twitter.com", "instagram.com",
    "reddit.com", "wikipedia.org", "amazon.com", "netflix.com", "twitch.tv",
    "linkedin.com", "github.com", "stackoverflow.com", "chatgpt.com", "openai.com",
    "bing.com", "yahoo.com", "pinterest.com", "tumblr.com", "tiktok.com",
    "quora.com", "medium.com", "nytimes.com", "cnn.com", "bbc.com", "foxnews.com",
    "ebay.com", "craigslist.org", "walmart.com", "target.com", "bestbuy.com",
    "apple.com", "microsoft.com", "spotify.com", "soundcloud.com", "hulu.com",
    "disneyplus.com", "hbomax.com", "primevideo.com", "paypal.com", "chase.com",
    "bankofamerica.com", "wellsfargo.com", "capitalone.com", "zillow.com",
    "realtor.com", "booking.com", "expedia.com", "airbnb.com", "tripadvisor.com",
    "yelp.com", "imdb.com", "ign.com", "gamespot.com", "pcgamer.com", "polygon.com",
    "kotaku.com", "theverge.com", "engadget.com", "wired.com", "techcrunch.com"
]

for site in websites:
    clean_name = site.replace(".com", "").replace(".org", "").replace(".tv", "")
    skills.append({
        "intent": f"open {clean_name}",
        "actions": [
            {"type": "key", "key": "win"},
            {"type": "sleep", "ms": 800},
            {"type": "type", "text": site},
            {"type": "sleep", "ms": 800},
            {"type": "key", "key": "enter"}
        ]
    })

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
    },
    {
        "intent": "open run",
        "actions": [{"type": "key", "key": "win+r"}]
    },
    {
        "intent": "open file explorer",
        "actions": [{"type": "key", "key": "win+e"}]
    },
    {
        "intent": "minimize all",
        "actions": [{"type": "key", "key": "win+m"}]
    },
    {
        "intent": "restore all",
        "actions": [{"type": "key", "key": "win+shift+m"}]
    },
    {
        "intent": "project screen",
        "actions": [{"type": "key", "key": "win+p"}]
    },
    {
        "intent": "open dictation",
        "actions": [{"type": "key", "key": "win+h"}]
    },
    {
        "intent": "open quick link",
        "actions": [{"type": "key", "key": "win+x"}]
    },
    {
        "intent": "close app",
        "actions": [{"type": "key", "key": "alt+f4"}]
    },
    {
        "intent": "switch app",
        "actions": [{"type": "key", "key": "alt+tab"}]
    },
    {
        "intent": "copy",
        "actions": [{"type": "key", "key": "ctrl+c"}]
    },
    {
        "intent": "paste",
        "actions": [{"type": "key", "key": "ctrl+v"}]
    },
    {
        "intent": "cut",
        "actions": [{"type": "key", "key": "ctrl+x"}]
    },
    {
        "intent": "undo",
        "actions": [{"type": "key", "key": "ctrl+z"}]
    },
    {
        "intent": "redo",
        "actions": [{"type": "key", "key": "ctrl+y"}]
    },
    {
        "intent": "select all",
        "actions": [{"type": "key", "key": "ctrl+a"}]
    },
    {
        "intent": "save",
        "actions": [{"type": "key", "key": "ctrl+s"}]
    },
    {
        "intent": "print",
        "actions": [{"type": "key", "key": "ctrl+p"}]
    },
    {
        "intent": "find",
        "actions": [{"type": "key", "key": "ctrl+f"}]
    },
    {
        "intent": "new window",
        "actions": [{"type": "key", "key": "ctrl+n"}]
    },
    {
        "intent": "new tab",
        "actions": [{"type": "key", "key": "ctrl+t"}]
    },
    {
        "intent": "close tab",
        "actions": [{"type": "key", "key": "ctrl+w"}]
    },
    {
        "intent": "reopen closed tab",
        "actions": [{"type": "key", "key": "ctrl+shift+t"}]
    },
    {
        "intent": "refresh",
        "actions": [{"type": "key", "key": "f5"}]
    },
    {
        "intent": "hard refresh",
        "actions": [{"type": "key", "key": "ctrl+f5"}]
    },
    {
        "intent": "fullscreen",
        "actions": [{"type": "key", "key": "f11"}]
    },
    {
        "intent": "open dev tools",
        "actions": [{"type": "key", "key": "f12"}]
    },
    {
        "intent": "open history",
        "actions": [{"type": "key", "key": "ctrl+h"}]
    },
    {
        "intent": "open downloads",
        "actions": [{"type": "key", "key": "ctrl+j"}]
    },
    {
        "intent": "open bookmarks",
        "actions": [{"type": "key", "key": "ctrl+b"}]
    },
    {
        "intent": "bookmark this page",
        "actions": [{"type": "key", "key": "ctrl+d"}]
    }
]

skills.extend(specialized_skills)

for skill in skills:
    safe_name = skill["intent"].replace(" ", "_")
    data = {
        "name": skill["intent"],
        "actions": skill["actions"]
    }
    with open(f"skills_db/learned_{safe_name}.json", "w") as f:
        json.dump(data, f, indent=2)

print(f"Generated {len(skills)} pre-trained skills in skills_db!")
