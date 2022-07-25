import pickle
import socket
import time
from datetime import datetime
from ChatPayload import ChatPayload
from User import User
import select
import sys
from _thread import *


def timer():
    app_time = time.time()
    while True:
        new_time = time.time()
        if new_time - app_time > 120:
            print(f"[{datetime.now()}] Server On")
            app_time = new_time


class Server:
    def __init__(self, ip_address: str, port: int):
        # Setting variables
        self._ip_address = ip_address
        self._port = port
        self._list_of_clients = []
        self._connection = None

        print(f"[{datetime.now()}] Starting Server on {self._ip_address}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(f"[{datetime.now()}] Binding IP and Port")
        self._socket.bind((ip_address, port))

        print(f"[{datetime.now()}] Listening on port: {self._port}")
        self._socket.listen(100)
        print(f"[{datetime.now()}] Server Started")

    # Broadcast a message to all clients
    def _broadcast(self, message, connection):
        for clients in list(self._list_of_clients.values()):
            try:
                clients.send(message)
            except Exception as e:
                print(f"[{datetime.now()}] Exception Detected: {e}")
                clients.close()
                # if the link is broken, we remove the client
                self._remove(clients)

    def _receive(self):
        while True:
            # Build a "new user"
            new_user = User(self._socket.accept(), datetime.now())
            print(f"[{datetime.now()}] Connected with: {new_user.address}")

            payload = ChatPayload()
            payload.by = "Server"
            payload.text_payload = "Digite seu nome:"
            payload = new_user.send(payload)

            rec_payload = new_user.connection.recv(2048)
            rec_payload = pickle.loads(rec_payload)

            new_user.nickname = rec_payload.get_message()
            self._list_of_clients.append(new_user)

            print(f"[{datetime.now()}] A new user has joined the server:\n"
                  f"User:\t{new_user.nickname}\n"
                  f"IP Address:\t{new_user.address}\n"
                  f"Joined at:\t{new_user.connected_since()}")

    def _client_thread(self, connection, addr):
        # sends a message to the client whose user object is conn
        msg = ChatPayload()
        msg.text_payload = "Bem Vindo ao Chat"
        msg.by = "Server"
        connection.send(pickle.dumps(msg))

        while True:
            try:
                message = connection.recv(2048)
                if message:

                    """prints the message and address of the
                    user who just sent the message on the server
                    terminal"""
                    print("<" + addr[0] + "> " + message)

                    # Calls broadcast function to send message to all
                    message_to_send = "<" + addr[0] + "> " + message
                    self._broadcast(message_to_send, connection)

                else:
                    """message may have no content if the connection
                    is broken, in this case we remove the connection"""
                    self._remove(connection)
            except Exception as e:
                print(f"[{datetime.now()}] Exception Detected: {e}")
                continue

    """The following function simply removes the object
    from the list that was created at the beginning of
    the program

    def _remove(self, connection):
        if connection in self._list_of_clients:
            self._list_of_clients.remove(connection)
            """

    def loop(self):
        print(f"[{datetime.now()}] Server On")
        start_new_thread(timer, ())
        while True:
            """Accepts a connection request and stores two parameters,
                conn which is a socket object for that user, and addr
                which contains the IP address of the client that just
                connected"""
            self._connection, address = self._socket.accept()

            """Maintains a list of clients for ease of broadcasting
            a message to all available people in the chatroom"""
            self._list_of_clients.append(self._connection)

            # prints the address of the user that just connected
            print(f"[{datetime.now()}] {address[0]} connection has been established")

            # creates and individual thread for every user
            # that connects
            start_new_thread(self._client_thread, (self._connection, address))

    def __del__(self):
        self._connection.close()
        print(f"[{datetime.now()}] Connection Closed")
        self._socket.close()
        print(f"[{datetime.now()}] Server Closed")
