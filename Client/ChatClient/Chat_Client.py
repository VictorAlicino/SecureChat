import socket
import pickle
import threading
import sys
from rich.console import Console
from datetime import datetime
from rich.live import Live
from rich.prompt import Prompt, IntPrompt, Confirm
import keyboard
import GUI
from ChatPayload import ChatPayload


def process_message_rcv(message: str):
    if message.startswith("You are now connected with "):
        return 1
    else:
        return 0


class ChatClient:
    def __init__(self, username: str):
        self.username = username
        self._server = None
        self.server_ip_addr = ""
        self.server_port = 0
        self._connected_with = None

        self.console = Console()
        # self.layout = GUI.chat_layout()

    def connect(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((self.server_ip_addr, self.server_port))

        self.console.rule(f"[bold blue] Connected to {self.server_ip_addr}")
        received_bytes = self._server.recv(1024)
        received_object = pickle.loads(received_bytes)
        print(f"[{datetime.now()}] System <<{received_object.by}>> --> {received_object.get_message()}")

        msg = ChatPayload()
        msg.text_payload = "Ready to Transmit"
        msg.username = self.username
        msg.by = socket.gethostname()
        self._server.send(pickle.dumps(msg))

        # self.layout["header"].update(GUI.Header())
        # self.layout["chat_body"].update(GUI.messages_panel_helper())
        # self.layout["side"].update(GUI.active_users_panel("None active users"))
        # self.layout["footer"].update(GUI.input_section("Write your message here..."))

        gui_thread = threading.Thread(target=self.recv_loop).start()
        recv_thread = threading.Thread(target=self.send_loop).start()
        return self._server

    def recv_loop(self):
        while True:
            try:
                received_bytes = self._server.recv(1024)
                received_object = pickle.loads(received_bytes)
                select = process_message_rcv(received_object.text_payload)

                if select == 0:
                    print(f"[{received_object.message_time}] <<{received_object.username}>> "
                          f"{received_object.text_payload}")
                if select == 1:
                    self.console.rule(f"[bold green] Connected to "
                                      f"{received_object.text_payload[26:received_object.text_payload.find('@')]}")
            except OSError as e:
                print(f"[{datetime.now()}] {e}")
                print(f"[{datetime.now()}] Disconnected from Server")
                exit(1)
            except Exception as e:
                print(f"[{datetime.now()}] {e}")

    def send_loop(self):
        msg = ChatPayload()
        msg.text_payload = ""
        msg.username = self.username
        msg.by = socket.gethostname()
        while True:
            msg.text_payload += input()
            if msg.text_payload.startswith("/exit"):
                self._server.send(pickle.dumps(msg))
                self._server.close()
                exit(1)
            sys.stdout.write("\033[1A[\033[2K")
            # self.layout["footer"].update(GUI.input_section(msg.text_payload))
            self._server.send(pickle.dumps(msg))
            msg.text_payload = ""
