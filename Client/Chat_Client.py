import socket
import pickle
import threading
import sys
import os
import ssl
from rich.console import Console
from datetime import datetime
from ChatPayload import ChatPayload
from tkinter import *
from tkinter import filedialog
import pathlib


def process_message_rcv(message: ChatPayload):
    if message.text_payload.startswith("You are now connected with "):
        return 1
    if message.text_payload.startswith("/file_transfer "):
        return 2
    else:
        return 0           
    
def parse_file(filename: str):
    with open(filename, "rb") as f:
        return f.read()

def file_recv(file, sender:str):
    with open(r"{sender}-{datetime.now()}{file.format_name}", "wb") as f:
        f.write(file.raw_bytes)


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
                received_bytes = self._server.recv(1073741824)
                received_object = pickle.loads(received_bytes)
                select = process_message_rcv(received_object)

                if select == 0:
                    print(f"[{received_object.message_time}] <<{received_object.username}>> "
                          f"{received_object.text_payload}")
                if select == 1:
                    self.console.rule(f"[bold green] Connected to "
                                      f"{received_object.text_payload[26:received_object.text_payload.find('@')]}")
                if select == 2:
                    try:
                        size = 1024 + int(received_object.text_payload[15:])
                        received_bytes = self._server.recv(size)
                        received_object = pickle.loads(received_bytes)
                        file_recv(received_object, received_object.by)
                        print(f"[{received_object.message_time}] <<{received_object.username}>> "
                              f"[bold white] File of type {received_object.format_name} received")
                    except Exception as e:
                        raise e
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
            # Send Files
            if msg.text_payload.startswith("/sendfile"):
                try:
                    directory = os.path.basename(msg.text_payload[10:])
                    if not os.path.isfile(directory):
                        raise Exception("File not found")
                    file_temp1 = parse_file(directory)
                    msg.text_payload = f"/file_transfer {len(file_temp1)}"
                    print(msg)
                    self._server.send(pickle.dumps(msg))
                    msg.raw_byte = file_temp1
                    msg.format_name = pathlib.Path(directory).suffix
                    self._server.send(pickle.dumps(msg))
                except Exception as e:
                    sys.stdout.write("\033[1A[\033[2K") # Clear the input line
                    self.console.print(f"Unvalid file path: [ {msg.text_payload[10:]} ]", style="bold red")
                    msg.raw_byte = None
                    msg.format_name = None
                    msg.text_payload = ""
                    continue
            if msg.text_payload.startswith("/exit"):
                self._server.send(pickle.dumps(msg))
                self._server.close()
                exit(1)
            msg.raw_byte = ""
            msg.format_name = ""
            sys.stdout.write("\033[1A[\033[2K") # Clear the input line
            # self.layout["footer"].update(GUI.input_section(msg.text_payload))
            self._server.send(pickle.dumps(msg))
            msg.text_payload = ""
