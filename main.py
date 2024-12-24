import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
import threading
import traceback
import logging
from kivy.logger import Logger
import websocket
import socket
import ssl
from kivy.utils import platform
from jnius import autoclass
from android.permissions import check_permission, Permission
from kivy.lang import Builder #import the builder class
from permissions import AndroidPermissions

# Set up logging
logging.basicConfig(level=logging.DEBUG)

Builder.load_string('''
<RootLayout>:
    orientation: 'vertical'

    BoxLayout:
        orientation: 'horizontal'
        Label:
            text: "Server IP Address:"
        TextInput:
            id: ip_input
            multiline: False

    Button:
        id: connect_button
        text: "Connect"
        on_press: root.start_websocket()

    Label:
        id: status_label
        text: root.received_text
    Button:
        id: retry_button
        text: "Retry Permissions"
        on_press: root.request_and_check()
    Label:
        id: internet_permission_label
        text: "Internet: Unknown"
    Label:
        id: network_state_permission_label
        text: "Network State: Unknown"
    Label:
        id: wifi_state_permission_label
        text: "Wifi State: Unknown"
''')

class RootLayout(BoxLayout):
    received_text = StringProperty("Waiting for messages...")
    websocket_url = StringProperty("ws://192.168.29.193:8765")
    websocket = None
    permissions_granted = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_input = self.ids.ip_input
        self.status_label = self.ids.status_label
        self.connect_button = self.ids.connect_button
        self.retry_button = self.ids.retry_button
        self.internet_permission_label = self.ids.internet_permission_label
        self.network_state_permission_label = self.ids.network_state_permission_label
        self.wifi_state_permission_label = self.ids.wifi_state_permission_label

    def on_start(self):
        """Called when the application starts."""
        try:
            Logger.info('App: Application starting...')
            if platform == 'android':
                # Request permissions immediately on startup
                self.request_and_check()
                socket.setdefaulttimeout(10)
        except Exception as e:
            Logger.error(f'App: Error during startup: {str(e)}')
            Logger.error(f'App: {traceback.format_exc()}')
    
    def request_and_check(self):
        if platform == 'android':
            self.permissions_granted = all([
                check_permission(Permission.INTERNET),
                check_permission(Permission.ACCESS_NETWORK_STATE),
                check_permission(Permission.ACCESS_WIFI_STATE)
            ])
            self.update_permission_labels()
            if not self.permissions_granted:
                self.received_text = "Permissions not granted. Please restart app."
    
    def update_permission_labels(self):
        if platform == 'android':
            self.internet_permission_label.text = f"Internet: {'Granted' if check_permission(Permission.INTERNET) else 'Denied'}"
            self.network_state_permission_label.text = f"Network State: {'Granted' if check_permission(Permission.ACCESS_NETWORK_STATE) else 'Denied'}"
            self.wifi_state_permission_label.text = f"Wifi State: {'Granted' if check_permission(Permission.ACCESS_WIFI_STATE) else 'Denied'}"
    
    # Remove request_android_permissions method as it's no longer needed

    def check_permissions(self):
        """Check if all required permissions are granted"""
        if platform == 'android':
            from android.permissions import check_permission, Permission
            permissions = [
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
                Permission.ACCESS_WIFI_STATE
            ]
            return all(check_permission(permission) for permission in permissions)
        return True

    def on_message(self, ws, message):
        Clock.schedule_once(lambda dt: setattr(self, 'received_text', f"Received: {message}"))

    def on_error(self, ws, error):
        error_msg = f"Error: {str(error)}"
        Logger.error(f'WebSocket: {error_msg}')
        Clock.schedule_once(lambda dt: setattr(self, 'received_text', error_msg))

    def on_close(self, ws, close_status_code, close_msg):
        Logger.info('WebSocket: Connection closed')
        Clock.schedule_once(lambda dt: setattr(self, 'received_text', "Connection Closed"))

    def on_open(self, ws):
        Logger.info('WebSocket: Connection opened')
        Clock.schedule_once(lambda dt: setattr(self, 'received_text', "Connected!"))
        ws.send("Hello, Server!")

    def start_websocket(self):
        if platform == 'android' and not self.permissions_granted:
            self.received_text = "Permissions not granted. Please grant permissions and retry."
            return
        
        try:
            if not self.check_permissions():
                self.received_text = "Missing required permissions!"
                return

            ip_address = self.ip_input.text
            self.websocket_url = f"ws://{ip_address}:8765"
            self.received_text = "Connecting..."

            # Android-specific network setup
            if platform == 'android':
                # Get Android context
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                
                # Enable network on main thread
                NetworkOnMainThreadException = autoclass('android.os.NetworkOnMainThreadException')
                StrictMode = autoclass('android.os.StrictMode')
                StrictMode.setThreadPolicy(StrictMode.ThreadPolicy.Builder().permitAll().build())

            # WebSocket setup with custom socket options
            ws_opts = {
                'timeout': 10,
                'skip_utf8_validation': True,
                'enable_multithread': True,
                'sslopt': {"cert_reqs": ssl.CERT_NONE},
                'sockopt': [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)],
            }

            self.websocket = websocket.WebSocketApp(
                self.websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )

            def run_connection():
                try:
                    self.websocket.run_forever(**ws_opts)
                except Exception as e:
                    Logger.error(f'Thread: Error in connection thread: {str(e)}')
                    Logger.error(f'Thread: {traceback.format_exc()}')
                    Clock.schedule_once(lambda dt: setattr(self, 'received_text', f"Connection Error: {str(e)}"))

            if hasattr(self, '_ws_thread') and self._ws_thread:
                self._ws_thread.join(timeout=1)

            self._ws_thread = threading.Thread(target=run_connection)
            self._ws_thread.daemon = True
            self._ws_thread.start()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            Logger.error(f'App: {error_msg}')
            self.received_text = error_msg

    def on_stop(self):
        if self.websocket:
            self.websocket.close()

class WebSocketClientApp(App):
    def build(self):
        self.root = RootLayout()
        return self.root

    def on_start(self):
        self.dont_gc = AndroidPermissions(self.start_app)

    def start_app(self):
        self.dont_gc = None
        self.root.permissions_granted = True
        self.root.received_text = "Permissions granted. Ready to connect."
        self.root.update_permission_labels()


if __name__ == '__main__':
    WebSocketClientApp().run()