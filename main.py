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
import websocket  # Using websocket-client instead of websockets
import socket
import ssl
from kivy.utils import platform

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class WebSocketClientApp(App):
    received_text = StringProperty("Waiting for messages...")
    websocket_url = StringProperty("ws://192.168.29.193:8765")
    websocket = None

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # IP Address input
        ip_layout = BoxLayout(orientation='horizontal')
        ip_layout.add_widget(Label(text="Server IP Address:"))
        self.ip_input = TextInput(text=self.websocket_url.split("//")[1].split(":")[0], multiline=False)
        ip_layout.add_widget(self.ip_input)
        layout.add_widget(ip_layout)

        # Connect Button
        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.start_websocket)
        layout.add_widget(self.connect_button)

        self.status_label = Label(text=self.received_text)
        self.bind(received_text=self.status_label.setter('text')) # bind the label's text to the property
        layout.add_widget(self.status_label)
        return layout

    def on_start(self):
        """Called when the application starts."""
        try:
            Logger.info('App: Application starting...')
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.INTERNET,
                    Permission.ACCESS_NETWORK_STATE,
                    Permission.ACCESS_WIFI_STATE,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
                # Initialize socket for Android
                socket.setdefaulttimeout(10)
        except Exception as e:
            Logger.error(f'App: Error during startup: {str(e)}')
            Logger.error(f'App: {traceback.format_exc()}')

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

    def start_websocket(self, instance):
        try:
            ip_address = self.ip_input.text
            self.websocket_url = f"ws://{ip_address}:8765"
            self.received_text = "Connecting..."

            # Set socket options
            websocket.setdefaulttimeout(10)
            if platform == 'android':
                # Force IPv4
                socket.setdefaulttimeout(10)
                socket.socket = socket.socket(socket.AF_INET)

            # Enable debug
            websocket.enableTrace(True)
            
            # Create WebSocket with options
            self.websocket = websocket.WebSocketApp(
                self.websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )

            def run_connection():
                try:
                    # Set socket options for WebSocket
                    opts = {
                        'skip_utf8_validation': True,
                        'enable_multithread': True,
                        'timeout': 10,
                        'ssl_version': ssl.PROTOCOL_TLSv1_2,
                        'sslopt': {"cert_reqs": ssl.CERT_NONE},
                    }
                    
                    self.websocket.run_forever(**opts)
                except Exception as e:
                    Logger.error(f'Thread: Error in connection thread: {str(e)}')
                    Logger.error(f'Thread: {traceback.format_exc()}')

            # Stop existing thread if any
            if hasattr(self, '_ws_thread') and self._ws_thread:
                try:
                    self._ws_thread.join(timeout=1)
                except:
                    pass

            self._ws_thread = threading.Thread(target=run_connection)
            self._ws_thread.daemon = True
            self._ws_thread.start()

        except Exception as e:
            Logger.error(f'App: Error starting websocket: {str(e)}')
            Logger.error(f'App: {traceback.format_exc()}')

    def on_stop(self):
        if self.websocket:
            self.websocket.close()

if __name__ == '__main__':
    WebSocketClientApp().run()
