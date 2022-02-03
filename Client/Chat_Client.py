import socket
import select
import sys
import pickle
from datetime import datetime
from ChatPayload import ChatPayload


class ChatClient:
    def __init__(self, ip_address: str, port: int):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((ip_address, port))

    def loop(self):
        while True:
            received_bytes = self._server.recv(4096)
            received_object = pickle.loads(received_bytes)
            print(received_object.text_payload)
