# (str) Title of your application
title = First

# (str) Package name
package.name = First

# (str) Package domain (unique identifier for your app)
package.domain = org.charan

# (str) Source code directory
source.dir = .

# (str) Main Python file
source.include_exts = py,kv
main.py = main.py

# (str) Application version
version = 1.0

# (list) Application requirements (comma-separated Python modules and libraries)
requirements = python3,kivy,websockets

# (str) Application orientation
orientation = portrait

# (bool) Enable fullscreen mode
fullscreen = 1

# (str) Presplash image file
#presplash.filename = 

# (str) Icon image file
#icon.filename = 

# (str) Supported platforms (comma-separated list)
# Available options: android, ios, windows, macosx, linux
supported_platforms = android

# (bool) Build the application as a service (background process)
#android.service = False

# (str) Minimum API level for Android
android.minapi = 21

# (str) Android package requirements
android.permissions = INTERNET

# (list) Additional build options
# Example: add custom files to the APK
#android.add_assets = 

# (str) Kivy configuration (optional, for tuning)
kivy.requirements = kivy

# (str) Custom Java/Kotlin classes (optional)
#android.add_src = src

# (str) Keystore for signing the app (optional for release builds)
#android.release_keystore = <path to keystore>

# (bool) Whether to include the `buildozer.spec` file in the APK (default: False)
include.spec = False

# (bool) Verbose debug logging
debug = 1
