import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.support import install_twisted_reactor
from kivy.clock import Clock
import asyncio
import websockets
import threading
import traceback
import logging
from kivy.logger import Logger

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class WebSocketClientApp(App):
    received_text = StringProperty("Waiting for messages...")
    websocket_url = StringProperty("ws://192.168.29.193:8765")  # Updated port to match server
    websocket = None
    loop = None

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
            # Ensure the app has all required permissions
            if kivy.platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.INTERNET,
                    Permission.ACCESS_NETWORK_STATE,
                    Permission.ACCESS_WIFI_STATE
                ])
        except Exception as e:
            Logger.error(f'App: Error during startup: {str(e)}')
            Logger.error(f'App: {traceback.format_exc()}')

    async def receive_messages(self, websocket):
        while True:
            try:
                message = await websocket.recv()
                Clock.schedule_once(lambda dt: setattr(self, 'received_text', f"Received: {message}"))
            except websockets.ConnectionClosed:
                Clock.schedule_once(lambda dt: setattr(self, 'received_text', "Connection Closed"))
                break
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self, 'received_text', f"Error: {str(e)}"))
                break

    async def connect_websocket(self):
        try:
            Logger.info(f'WebSocket: Attempting to connect to {self.websocket_url}')
            self.websocket = await websockets.connect(
                self.websocket_url,
                ping_interval=None,  # Disable ping to avoid some connection issues
                close_timeout=1000
            )
            Clock.schedule_once(lambda dt: setattr(self, 'received_text', "Connected!"))
            await self.websocket.send("Hello, Server!")
            await self.receive_messages(self.websocket)
        except Exception as e:
            error_msg = f"Connection Error: {str(e)}\n{traceback.format_exc()}"
            Logger.error(f'WebSocket: {error_msg}')
            Clock.schedule_once(lambda dt: setattr(self, 'received_text', error_msg))

    def start_websocket(self, instance):
        try:
            ip_address = self.ip_input.text
            self.websocket_url = f"ws://{ip_address}:8765"
            self.received_text = "Connecting..."

            if not self.loop:
                self.loop = asyncio.new_event_loop()

            def run_connection():
                try:
                    asyncio.set_event_loop(self.loop)
                    self.loop.run_until_complete(self.connect_websocket())
                except Exception as e:
                    Logger.error(f'Thread: Error in connection thread: {str(e)}')
                    Logger.error(f'Thread: {traceback.format_exc()}')

            thread = threading.Thread(target=run_connection)
            thread.daemon = True
            thread.start()
        except Exception as e:
            Logger.error(f'App: Error starting websocket: {str(e)}')
            Logger.error(f'App: {traceback.format_exc()}')

    def on_pause(self):
        """Called when the application is paused."""
        Logger.info('App: Application paused')
        return True

    def on_resume(self):
        """Called when the application is resumed."""
        Logger.info('App: Application resumed')
        return True

    def on_stop(self):
        if self.websocket:
            self.loop.run_until_complete(self.websocket.close())
        if self.loop:
            self.loop.close()

if __name__ == '__main__':
    WebSocketClientApp().run()
