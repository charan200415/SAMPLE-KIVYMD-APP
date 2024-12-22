import asyncio
import socket
from threading import Thread
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from websockets import serve
from jnius import autoclass

class MainApp(App):
    def build(self):
        # Main UI layout
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Status label to display messages
        self.status_label = Label(text="WebSocket Server: Initializing...", size_hint=(1, 0.2))
        layout.add_widget(self.status_label)

        # Button to simulate interaction
        test_button = Button(text="Simulate Action", size_hint=(1, 0.2))
        test_button.bind(on_press=self.simulate_action)
        layout.add_widget(test_button)

        # Start WebSocket server in the background
        self.start_server()

        return layout

    def simulate_action(self, instance):
        """Simulate an action triggered from the UI."""
        self.status_label.text = "Simulated action triggered!"

    def start_server(self):
        """Start the WebSocket server in a separate thread."""
        def run_asyncio_loop():
            asyncio.run(self.websocket_server())

        thread = Thread(target=run_asyncio_loop, daemon=True)
        thread.start()

    async def websocket_server(self):
        """Asynchronous WebSocket server to handle AI commands."""
        async def handle_client(websocket, path):
            # Notify connection
            self.update_status("Client connected!")

            async for message in websocket:
                # Process incoming messages
                self.update_status(f"Received: {message}")
                if message == "CALL_FRIEND":
                    self.update_status("Action: Call friend!")
                elif message == "SEND_SMS":
                    self.update_status("Action: Send SMS!")
                else:
                    self.update_status(f"Unknown command: {message}")

        # Get the Wi-Fi IP address
        local_ip = self.get_wifi_ip()

        # Show the IP address in the UI
        self.update_status(f"Server IP: {local_ip}")

        # Start the WebSocket server
        server = await serve(handle_client, "0.0.0.0", 8765)
        self.update_status(f"WebSocket Server: Listening on {local_ip}:8765")
        await server.wait_closed()

    def get_wifi_ip(self):
        """Retrieve the device's local Wi-Fi IP address."""
        WifiInfo = autoclass("android.net.wifi.WifiInfo")
        WifiManager = autoclass("android.net.wifi.WifiManager")
        Context = autoclass("android.content.Context")

        # Get the application context
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        wifi_service = activity.getSystemService(Context.WIFI_SERVICE)
        wifi_manager = wifi_service.cast(WifiManager)
        connection_info = wifi_manager.getConnectionInfo()

        # Extract the IP address from the connection info
        ip_address = connection_info.getIpAddress()
        ip = socket.inet_ntoa(ip_address.to_bytes(4, "little"))
        return ip

    def update_status(self, message):
        """Update the status label safely from any thread."""
        self.status_label.text = message

if __name__ == "__main__":
    MainApp().run()
