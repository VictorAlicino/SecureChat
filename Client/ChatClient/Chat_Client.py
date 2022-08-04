import socket
import pickle
import threading
import sys
import time
import rich
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from datetime import datetime
import GUI
from ChatPayload import ChatPayload


class ChatClient:
    def __init__(self, username: str):
        console = Console()
        self.username = username
        self._server = None
        self.server_ip_addr = ""
        self.server_port = 0

    def connect(self):
        print(f"[{datetime.now()}] Connecting to {self.server_ip_addr}:{self.server_port}")
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((self.server_ip_addr, self.server_port))

        received_bytes = self._server.recv(1024)
        received_object = pickle.loads(received_bytes)
        print(f"[{datetime.now()}] System <<{received_object.by}>> --> {received_object.get_message()}")

        msg = ChatPayload()
        msg.text_payload = "Ready to Transmit"
        msg.username = self.username
        msg.by = socket.gethostname()
        self._server.send(pickle.dumps(msg))

        gui_thread = threading.Thread(target=self.recv_loop).start()
        recv_thread = threading.Thread(target=self.send_loop()).start()
        return self._server

    def recv_loop(self):
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
        while True:
            msg = ChatPayload()
            msg.text_payload = input()
            msg.username = self.username
            msg.by = socket.gethostname()
            self._server.send(pickle.dumps(msg))
