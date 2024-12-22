from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import threading
import websocket
import json

class WebSocketClientApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ws = None
        self.received_text = "Waiting for messages..."
        self.status_label = None
        self.ip_input = None
        self.connect_button = None
        self.websocket_url = "ws://192.168.29.193:8000/ws" # Default IP

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # IP Address input
        ip_layout = BoxLayout(orientation='horizontal')
        ip_layout.add_widget(Label(text="PC IP Address:"))
        self.ip_input = TextInput(text=self.websocket_url.split("//")[1].split(":")[0], multiline=False) # Set default value as current IP address
        ip_layout.add_widget(self.ip_input)
        layout.add_widget(ip_layout)


        # Connect Button
        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.start_websocket) # Connect to server when clicked
        layout.add_widget(self.connect_button)

        self.status_label = Label(text=self.received_text)
        layout.add_widget(self.status_label)
        return layout


    def start_websocket(self, instance): # Pass instance so the on_press knows what widget was pressed
        ip_address = self.ip_input.text
        self.websocket_url = f"ws://{ip_address}:8000/ws" #Update url
        if self.ws and self.ws.sock:
            self.ws.close() #Close connection to connect again

        self.ws = websocket.WebSocketApp(self.websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close)
      
        threading.Thread(target=self.ws.run_forever).start() # Run the connection in its own thread

    def on_open(self, ws):
      print("WebSocket connection established")
      self.received_text = "Connected to Server"
      Clock.schedule_once(self.update_label, 0)

    def on_message(self, ws, message):
      print(f"Received message: {message}")
      self.received_text = message
      Clock.schedule_once(self.update_label, 0)

    def on_error(self, ws, error):
      print(f"WebSocket Error: {error}")
      self.received_text = f"Error: {error}"
      Clock.schedule_once(self.update_label, 0)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        self.received_text = "Connection Closed"
        Clock.schedule_once(self.update_label, 0)

    def update_label(self, dt):
      self.status_label.text = self.received_text


if __name__ == '__main__':
    WebSocketClientApp().run()
