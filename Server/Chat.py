import socket
import select
import sys
import _thread


class Chat:
    def __init__(self, ip_address: str, port: int):
        self._list_of_clients = []
        self._connection = None
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._server.bind((ip_address, port))
        self._server.listen(100)

    """Using the below function, we broadcast the message to all
    clients who's object is not the same as the one sending
    the message """

    def _broadcast(self, message, connection):
        for clients in self._list_of_clients:
            if clients != connection:
                try:
                    clients.send(message)
                except:
                    clients.close()

                    # if the link is broken, we remove the client
                    self._remove(clients)

    def _client_thread(self, connection, addr):
        # sends a message to the client whose user object is conn
        connection.send("Welcome to this chatroom!")

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

            except:
                continue

    """The following function simply removes the object
    from the list that was created at the beginning of
    the program"""

    def _remove(self, connection):
        if connection in self._list_of_clients:
            self._list_of_clients.remove(connection)
