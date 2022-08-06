import socket
import pickle
import threading
import sys
import ssl
from rich.console import Console
from datetime import datetime
from ChatPayload import ChatPayload


def process_message_rcv(message: str):
    if message.startswith("You are now connected with "):
        return 1
    else:
        return 0


class ChatClient:
    def __init__(self, username: str, secure_connection=False):
        self.username = username  # Username of the user

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Server socket
        self.server_ip_addr = ""  # IP Address of the server
        self.server_port = 0  # Port of the server
        self.secure_connection = secure_connection  # Secure connection is required?
        self.context = None  # SSL Context
        self._connected_with = None  # Username of the connected user

        self.console = Console()
        # self.layout = GUI.chat_layout() # RIP cool design layout, I ran out of time to implement it

    def connect(self):
        # Secure connection is required
        if self.secure_connection:
            # TLS Setup
            # Creating the Context
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            self.context.verify_mode = ssl.CERT_REQUIRED
            self.console.log("[bold blue]<<TLS>>[white] --> [TLS Enabled]", style="bold white")

            # Loading the certificate
            self.context.load_verify_locations("../Certs/ServerCerts/cert.pem")
            self.console.log("[bold blue]<<TLS>>[white] --> [Verifying Certificates]", style="bold white")
            self.context.load_cert_chain("../Certs/ClientCerts/cert.pem", "../Certs/ClientCerts/key.pem")
            self.console.log("[bold blue]<<TLS>>[white] --> [Certificate Loaded]", style="bold white")

            # Creating a new socket
            self._server = self.context.wrap_socket(socket.socket(), server_side=False)
            self.console.log("[bold blue]<<TLS>>[white] --> [Creating Secure Connection]", style="bold green")

        # Connecting to the server
        self._server.connect((self.server_ip_addr, self.server_port))

        # Connected to the server
        self.console.rule(f"[bold blue] Connected to {self.server_ip_addr}")
        received_bytes = self._server.recv(2048)
        received_object = pickle.loads(received_bytes)
        self.console.log(f"<<{received_object.by}>> --> {received_object.get_message()}", style="bold white")

        msg = ChatPayload()
        msg.text_payload = "Thanks for connecting"
        msg.username = self.username
        msg.by = socket.gethostname()
        self._server.send(pickle.dumps(msg))

        # RIP Cool interface
        # self.layout["header"].update(GUI.Header())
        # self.layout["chat_body"].update(GUI.messages_panel_helper())
        # self.layout["side"].update(GUI.active_users_panel("None active users"))
        # self.layout["footer"].update(GUI.input_section("Write your message here..."))

        threading.Thread(target=self.recv_loop).start()  # Thread for receiving messages
        threading.Thread(target=self.send_loop).start()  # Thread for sending messages
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
