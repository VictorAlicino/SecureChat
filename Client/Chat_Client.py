import socket
import select
import sys
import pickle
from datetime import datetime


class ChatPayload:
    message_time = datetime.now()  # Time when the message was sent
    to_ip = None  # Receiver IP
    by = None  # Sender Name
    raw_byte = None  # Raw bytes payload
    format_name = None  # Raw Bytes format
    text_payload = None  # Text payload


class ChatClient:
    def __init__(self, ip_address: str, port: int):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect((ip_address, port))

    def loop(self):
        while True:
            msg = self._server.recv(4096)
            print(msg)
            temp = pickle.loads(msg)
            print(temp)
