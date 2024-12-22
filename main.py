import asyncio
import socket
from threading import Thread
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from websockets import serve
if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission
from kivy.utils import platform
from kivy.clock import Clock

def request_android_permissions(callback):
    """Request necessary permissions at runtime."""
    required_permissions = [
        Permission.INTERNET,
        Permission.ACCESS_NETWORK_STATE,
        Permission.ACCESS_WIFI_STATE,
    ]

    def callback_wrapper(permissions, results):
        if all(results):
            callback()
        else:
            print("Permissions not granted")

    # Check and request permissions if not already granted
    if platform == 'android':
        request_permissions(required_permissions, callback_wrapper)
    else:
        callback()

def get_wifi_ip():
    """Retrieve the device's local IP address."""
    try:
        # Use hostname as a fallback if Wi-Fi access is restricted
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        return f"Error retrieving IP: {str(e)}"

class MainApp(App):
    def build(self):
        # Main UI layout
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Status label to display messages
        self.status_label = Label(text="WebSocket Server: Initializing...", size_hint=(1, 0.2))
        layout.add_widget(self.status_label)

        # Button to simulate interaction
        test_button = Button(text="Simulate me Action", size_hint=(1, 0.2))
        test_button.bind(on_press=self.simulate_action)
        layout.add_widget(test_button)

        # Request permissions and start server
        request_android_permissions(self.start_server)

        return layout

    def simulate_action(self, instance):
        """Simulate an action triggered from the UI."""
        self.status_label.text = "Simulated actions triggered!"

    def start_server(self):
        """Start the WebSocket server in a separate thread."""
        def run_asyncio_loop():
            asyncio.run(self.websocket_server())

        thread = Thread(target=run_asyncio_loop, daemon=True)
        thread.start()

    async def websocket_server(self):
        """Asynchronous WebSocket server to handle AI commands."""
        try:
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

            # Get the Wi-Fi IP address or fallback
            local_ip = get_wifi_ip()

            # Show the IP address in the UI
            self.update_status(f"Server IP: {local_ip}")

            # Start the WebSocket server
            server = await serve(handle_client, "0.0.0.0", 8765)
            self.update_status(f"WebSocket Server: Listening on {local_ip}:8765")
            await server.wait_closed()
        except Exception as e:
            self.update_status(f"Error: {str(e)}")

    def update_status(self, message):
        """Update the status label safely from any thread."""
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', message))

if __name__ == "__main__":
    MainApp().run()
