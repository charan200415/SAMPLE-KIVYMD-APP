from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

import threading
import websocket

class WebSocketClientApp(App):
    received_text = StringProperty("Waiting for messages...")
    websocket_url = StringProperty("ws://192.168.29.193:8000/ws")  # Default IP

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # IP Address input
        ip_layout = BoxLayout(orientation='horizontal')
        ip_layout.add_widget(Label(text="PC IP Address:"))
        self.ip_input = TextInput(text=self.websocket_url.split("//")[1].split(":")[0], multiline=False)
        ip_layout.add_widget(self.ip_input)
        layout.add_widget(ip_layout)

        # Connect Button
        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.start_websocket)
        layout.add_widget(self.connect_button)

        self.status_label = Label(text=self.received_text)
        layout.add_widget(self.status_label)
        return layout

    def start_websocket(self, instance):
        ip_address = self.ip_input.text
        self.websocket_url = f"ws://{ip_address}:8000/ws"

        self.ws = websocket.WebSocketApp(self.websocket_url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
