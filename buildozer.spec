[app]
title = WebSocket Server App
package.name = websocket_server_app
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,websocket-client,plyer,android
#orientation = portrait
orientation = portrait, landscape, portrait-reverse, landscape-reverse
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.add_aars = ~/.buildozer/android/platform/android-sdk/extras/android/m2repository/com/android/support/support-v4/21.0.3/support-v4-21.0.3.aar
android.logcat_filters = *:S python:D
android.arch = armeabi-v7a
