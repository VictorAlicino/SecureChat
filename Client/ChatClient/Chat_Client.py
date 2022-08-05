import socket
import pickle
import threading
from rich.console import Console
from datetime import datetime
from rich.live import Live
import keyboard
import GUI
from ChatPayload import ChatPayload


class ChatClient:
    def __init__(self, username: str):
        self.username = username
        self._server = None
        self.server_ip_addr = ""
        self.server_port = 0
        self._connected_with = "No one"

        self.console = Console()
        self.layout = GUI.chat_layout()

    def connect(self):
        print(f"[{datetime.now()}] Connecting to {self.server_ip_addr}:{self.server_port}")
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((self.server_ip_addr, self.server_port))

        received_bytes = self._server.recv(1024)
        received_object = pickle.loads(received_bytes)

        msg = ChatPayload()
        msg.text_payload = "Ready to Transmit"
        msg.username = self.username
        msg.by = socket.gethostname()
        self._server.send(pickle.dumps(msg))

        self.layout["header"].update(GUI.Header())
        self.layout["chat_body"].update(GUI.messages_panel(f"[{datetime.now()}] System <<{received_object.by}>> --> "
                                                           f"{received_object.get_message()}",
                                                           self._connected_with))
        self.layout["side"].update(GUI.active_users_panel("None active users"))
        self.layout["footer"].update(GUI.input_section("Write your message here..."))

        gui_thread = threading.Thread(target=self.recv_loop).start()
        recv_thread = threading.Thread(target=self.send_loop).start()
        return self._server

    def recv_loop(self):
        with Live(self.layout, screen=True, redirect_stderr=False) as live:
            while True:
                try:
                    received_bytes = self._server.recv(1024)
                    received_object = pickle.loads(received_bytes)
                    print(f"[{received_object.message_time}] <<{received_object.username}>> "
                          f"{received_object.text_payload}")
                except OSError as e:
                    print(f"[{datetime.now()}] {e}")
                    print(f"[{datetime.now()}] Disconnected from Server")
                    exit(1)
                except Exception as e:
                    print(f"[{datetime.now()}] {e}")

    def send_loop(self):
        msg = ChatPayload()
        msg.by = socket.gethostname()
        msg.text_payload = ""
        msg.username = self.username
        while True:
            key = keyboard.read_key()
            msg.text_payload += key
            self.layout["footer"].update(GUI.input_section(msg.text_payload))
            if key == "enter":
                self._server.send(pickle.dumps(msg))
                msg.text_payload = ""
                continue
            if key == "backspace":
                msg.text_payload = msg.text_payload[:-1]
                continue
