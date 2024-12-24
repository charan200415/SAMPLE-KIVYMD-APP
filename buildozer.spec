[app]
title = WebSocket Server App
package.name = websocket_server_app
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,websocket-client,plyer,android,pyjnius,openssl,kivy-garden.qrcode
#orientation = portrait
orientation = portrait, landscape, portrait-reverse, landscape-reverse
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.add_aars = ~/.buildozer/android/platform/android-sdk/extras/android/m2repository/com/android/support/support-v4/21.0.3/support-v4-21.0.3.aar
android.logcat_filters = *:S python:D
android.minapi = 21
android.ndk = 25b
android.arch = armeabi-v7a
android.allow_backup = True
android.enable_androidx = True
android.meta_data = android.net.conn.CONNECTIVITY_CHANGE.broadcast.receiver
android.uses-library = org.apache.http.legacy
android.enable_network_discovery = true
