import pickle
import socket
import threading
import time
from datetime import datetime
from ChatPayload import ChatPayload
from User import User
from _thread import *


class TextColors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END_C = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def timer():
    app_time = time.time()
    while True:
        new_time = time.time()
        if new_time - app_time > 120:
            print(f"[{datetime.now()}] Server On")
            app_time = new_time


def process_received_message(msg: str):
    if msg.startswith("/help "):
        return 1
    if msg.startswith("/disconnect "):
        return 2
    if msg.startswith("/users "):
        return 3
    if msg.startswith("/connectwith "):
        return 4
    else:
        return 0


verbose_mode = False


class Server:
    def __init__(self, ip_address: str, port: int):
        # Setting variables
        self._ip_address = ip_address
        self._port = port
        self._list_of_clients = {}
        self._connection = None

        print(f"{TextColors.OK_CYAN}[{datetime.now()}] Starting Server on {self._ip_address}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"{TextColors.END_C}[{datetime.now()}] Binding IP and Port")
        self._socket.bind((ip_address, port))

        print(f"{TextColors.OK_CYAN}[{datetime.now()}] Listening on port: {self._port}")
        self._socket.listen(100)
        print(f"{TextColors.END_C}[{datetime.now()}] Server Started")

    def receive(self):
        while True:
            # Build a "new user"
            connection = self._socket.accept()
            new_user = User(connection, datetime.now())
            print(f"[{datetime.now()}] Connected with: {new_user.address[0]}:{new_user.address[1]}")

            payload = ChatPayload()
            payload.by = "Server"
            payload.username = "Server"
            payload.text_payload = "[Ready to Broadcast]\nType /help for help"
            payload = new_user.send(payload)

            recv_payload = new_user.connection.recv(2048)
            recv_payload = pickle.loads(recv_payload)

            new_user.username = recv_payload.username
            new_user.hostname = recv_payload.by
            self._list_of_clients[new_user.username] = new_user

            print(f"[{datetime.now()}] A new user has joined the server:\n"
                  f"User:       {new_user.username}\n"
                  f"IP Address: {new_user.address[0]}\n"
                  f"Joined at:  {new_user.connected_since()}")
            print(f"[{datetime.now()}] System <<{recv_payload.by}>> --> [{recv_payload.get_message()}]")

            thread = threading.Thread(target=self._handle, args=(new_user,))
            thread.start()

    def _handle(self, client: User):
        while True:
            try:
                recv_payload = client.connection.recv(2048)
                recv_payload = pickle.loads(recv_payload)
                if verbose_mode:
                    print(recv_payload)

                recv_payload.username = client.username
                message = recv_payload.get_message()

                if process_received_message(message) == 3:
                    self._send_list_of_users(client)
                    print(f"[{datetime.now()}] Sending list of users to {client.hostname}@{client.address[0]} "
                          f"aka {client.username}")
                if process_received_message(message) == 4:
                    user_to_connect_with = message.split(" ")[1]
                    self._conn_with_user(client, user_to_connect_with)
                    print(f"[{datetime.now()}] Connecting {client.hostname} with user_to_connect_with"
                          f"aka {client.username}")
                else:
                    print(f"[{datetime.now()}] User {recv_payload.username} says: {recv_payload.get_message()}")

                #self._broadcast(recv_payload)
            except Exception as e:
                print(f"{TextColors.WARNING}[{datetime.now()}] Exception Detected: {e}")
                print(f"[{datetime.now()}] A user has disconnected:\n"
                      f"User:            {client.username}\n"
                      f"IP Address:      {client.address[0]}\n"
                      f"Joined at:       {client.connected_since()}\n"
                      f"Disconnected at: {datetime.now()}"
                      f"{TextColors.END_C}")
                # TODO: Disconnect client from server
                break

    # Broadcast a message to all clients
    def _broadcast(self, payload: ChatPayload):
        for client in self._list_of_clients:
            try:
                client.send(payload)
            except Exception as e:
                print(f"[{datetime.now()}] Exception Detected: {e}")
                continue

    def _send_list_of_users(self, clients: User):
        payload = ChatPayload()
        payload.by = "Server"
        payload.username = "Server"
        users_list = ""
        for clients_conn in self._list_of_clients:
            users_list += f"{clients_conn} @ {self._list_of_clients[clients_conn].hostname}\n"
        payload.text_payload = f"{len(self._list_of_clients)} user(s) available:\n{users_list}"
        clients.send(payload)

    def _conn_with_user(self, client: User, user_to_connect_with: str):
        payload = ChatPayload()
        payload.by = "Server"
        payload.username = "Server"
        try:
            self._list_of_clients[user_to_connect_with].sending_to = str
            payload.text_payload = f"Chatting with {user_to_connect_with}"
            client.send(payload)
        except Exception as e:
            print(f"[{datetime.now()}] Exception Detected: {e}")
            payload.text_payload = f"{user_to_connect_with} is not available"
            client.send(payload)

    def __del__(self):
        try:
            self._connection.close()
            print(f"[{datetime.now()}] Connection Closed")
            self._socket.close()
            print(f"[{datetime.now()}] Server Closed")
        except Exception as e:
            print(f"[{datetime.now()}] Exception Detected: {e}")
