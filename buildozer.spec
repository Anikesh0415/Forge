[app]

# (str) Title of your application
title = Forge Native

# (str) Package name
package.name = forgenative

# (str) Package domain (needed for android/ios packaging)
package.domain = org.anikesh

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,websockets,asyncio

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android entry point, default is ok for Kivy-based app
# For our backend without UI, we might need a custom service or use a basic Kivy WebView
# android.entrypoint = org.kivy.android.PythonActivity
