import socket
import pickle
import threading
import Views.GUI
from Controllers.ChatPayload import ChatPayload


class ChatClient:
    def __init__(self, username: str):
        self.username = username
        self._server = None
        self.server_ip_addr = ""
        self.server_port = 0

    def connect(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((self.server_ip_addr, self.server_port))
        gui_thread = threading.Thread(target=self.recv_loop).start()
        recv_thread = threading.Thread(target=self.send_loop()).start()
        return self._server

    def recv_loop(self):
        while True:
            received_bytes = self._server.recv(1024)
            received_object = pickle.loads(received_bytes)
            print(f"[{received_object.message_time}] <<{received_object.by}>> {received_object.text_payload}")

    def send_loop(self):
        while True:
            msg = ChatPayload()
            msg.text_payload = input()
            msg.username = self.username
            msg.by = socket.gethostname()
            self._server.send(pickle.dumps(msg))
            print(f"sent: {msg.text_payload}")

