import kivy
kivy.require('2.1.0')  # Replace with your Kivy version if different
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import threading
import websocket
import json

class WebSocketClientApp(App):
    received_text = StringProperty("Waiting for messages...")
    websocket_url = StringProperty("ws://192.168.29.193:8000")  # Default IP (no /ws)
    ws = None

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

    def start_websocket(self, instance):
        ip_address = self.ip_input.text
        self.websocket_url = f"ws://{ip_address}:8000"  # Update URL (no /ws if server expects it at the root)
        self.received_text = "Connecting..."

        if self.ws:  # Check if a WebSocket connection exists
            self.ws.close()  # Close existing connection before creating a new one

        def on_open(ws):
            print("WebSocket connection established")
            self.received_text = "Connected!"
            ws.send(json.dumps({"type":"connect","message":"Client Connected"}))

        def on_message(ws, message):
            print(f"Received message: {message}")
            try:
                data = json.loads(message)
                if data["type"] == "message":
                    self.received_text = data["message"]
            except json.JSONDecodeError:
                self.received_text = message

        def on_error(ws, error):
            print(f"WebSocket Error: {error}")
            self.received_text = f"Error: {error}"

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")
            self.received_text = "Connection Closed"
            self.ws=None # set ws to None when the connection is closed

        self.ws = websocket.WebSocketApp(self.websocket_url,
                                         on_open=on_open,
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close)

        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True # Allow the main thread to exit even if the websocket thread is running
        thread.start()

if __name__ == '__main__':
    WebSocketClientApp().run()
