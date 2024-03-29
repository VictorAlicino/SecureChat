import pickle
import socket
import threading
import time
import ssl
from rich.console import Console
from rich.table import Table
from datetime import datetime
from ChatPayload import ChatPayload
from User import User


# When I write this function, only God and I know what it does.
# Now, only God knows.
def timer():
    app_time = time.time()
    while True:
        new_time = time.time()
        if new_time - app_time > 120:
            print(f"[{datetime.now()}] Server On")
            app_time = new_time


# Transform the commands sent by the user into an integer for easy processing.
def process_received_message(msg: str):
    if msg.startswith("/"):
        if msg.startswith("/help"):
            return 1
        elif msg.startswith("/disconnect"):
            return 2
        elif msg.startswith("/users"):
            return 3
        elif msg.startswith("/connect"):
            return 4
        elif msg.startswith("/exit"):
            return 5
        elif msg.startswith("/file_transfer "):
            return 6
        else:
            return -1
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
        self.secure = True
        self.console = Console()

        # TLS Setup
        # Creating the Context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.console.log("[bold blue]<<TLS>>[white] --> [TLS Enabled]", style="bold white")
        self.context.load_verify_locations("../Certs/ClientCerts/cert.pem")
        self.context.load_cert_chain("../Certs/ServerCerts/cert.pem", "../Certs/ServerCerts/key.pem")
        self.console.log("[bold blue]<<TLS>>[white] --> [Certificate Loaded]", style="bold white")
        self.console.log("Server is Secured by TLS v1.2", style="bold green")
        self.context.keylog_filename = "keylog.txt"

        # Creating the Socket
        self.console.log(f"Starting Server on {self._ip_address}:{self._port}", style="blue")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        self._socket.bind(("0.0.0.0", port))

        # Start listening for connections
        self.console.log(f"Listening on port: {self._port}", style="blue")
        self._socket.listen(100)
        self.console.log(f"Server Started", style="green")

        # Creates a User for the Server broadcast messages
        server = User((None, self._ip_address), datetime.now())
        server.username = "Server"
        server.hostname = "Host"
        self._list_of_clients["Server"] = server

    # When a client connects, this function is called
    def accept_clients(self):
        while True:
            # Build a "new user"

            # Accept the connection
            connection = self._socket.accept()
            # TLS Encryption
            try:
                tls_connection = self.context.wrap_socket(connection[0], server_side=True)
            except Exception as e:
                self.console.log("Exception Detected:", style="bold red")
                self.console.print_exception(width=0)
                continue

            # Build a new User object
            new_user = User((tls_connection, connection[1]), datetime.now())
            new_user.tls_connection = tls_connection
            self.console.log(f"Connected with: {new_user.address[0]}: {new_user.address[1]}", style="bold white")

            # Building the server response message
            payload = ChatPayload()
            payload.by = "Server"
            payload.username = "Server"
            payload.text_payload = "[Ready to Broadcast]\nType /help for help"
            new_user.send(payload)

            # Waits for the client to send the username
            recv_payload = new_user.connection.recv(2048)
            recv_payload = pickle.loads(recv_payload)

            new_user.username = recv_payload.username
            new_user.hostname = recv_payload.by
            # Add the new client to the list of clients
            self.console.log(f"[bold blue]<<{recv_payload.by}>>[white] --> [{recv_payload.get_message()}]")
            self._list_of_clients[new_user.username] = new_user

            # Prints the User's Connection information
            user_data_table = Table(title=f"New User:{new_user.username}")
            user_data_table.add_column("Field", justify="left")
            user_data_table.add_column("Connection", justify="left")
            user_data_table.add_row("Username", new_user.username)
            user_data_table.add_row("Hostname", new_user.hostname)
            user_data_table.add_row("IP Address", new_user.address[0])
            user_data_table.add_row("Port", str(new_user.address[1]))
            user_data_table.add_row("Connected Since", new_user.connected_since())

            self.console.print(user_data_table)

            thread = threading.Thread(target=self._handle, args=(new_user,))
            thread.start()

    # Handles the client's messages
    def _handle(self, client: User):
        while True:
            try:
                recv_payload = client.connection.recv(1073741824)
                recv_payload = pickle.loads(recv_payload)
                if verbose_mode:
                    print(recv_payload) # Only for DEBUG purposes

                # Signed the payload with the origin client's username
                recv_payload.username = client.username
                message = recv_payload.get_message()

                # Check if the message is a command
                message_code = process_received_message(message)
                # Invalid command
                if message_code == -1:
                    payload = ChatPayload()
                    payload.by = "Server"
                    payload.username = "Server"
                    payload.text_payload = f"\"{message[1:]}\" is not a valid command"
                    client.send(payload)

                # List users command
                elif message_code == 3:
                    self._send_list_of_users(client)
                    self.console.log(f"Sending a list of users to {client.hostname}@{client.address[0]} "
                                     f"aka {client.username}",
                                     style="bold white")

                # Connect with another user command
                elif message_code == 4:
                    try:
                        user_to_connect_with = message.split(" ")[1] # Separate the username from the command
                        self.console.log(f"Connecting {client.hostname} aka {client.username} with "
                                         f"{user_to_connect_with}")
                        self._conn_with_user(client, user_to_connect_with)
                    except Exception as e:
                        raise e

                # Disconnect command
                elif message_code == 5:
                    self.console.log(f"{client.hostname} aka {client.username} disconnected", style="bold red")
                    del self._list_of_clients[client.username] # Remove the client from the list of clients
                    self._print_clients_connections()
                    break # End the thread

                # Client is sending an file
                elif message_code == 6:
                    self.console.log(f"[{recv_payload.username}] --> [{client.sending_msgs_to}]")
                    size = 1024 + int(recv_payload.text_payload[15:]) # Get the size of the file
                    
                    if verbose_mode:
                        print(recv_payload) # Only for DEBUG purposes

                    # Signed the payload with the origin client's username
                    recv_payload.username = client.username
                    message = recv_payload.get_message()
                    self._file_transfer(recv_payload, client, size)
                # Message is not a command
                else:
                    # If client is not connected to anyone, a warning is sent
                    if client.sending_msgs_to is not None:
                        # If the client is connected to the server, the message is sent to destination
                        if client.sending_msgs_to != "Server":
                            self.console.log(f"[{recv_payload.username}] --> [{client.sending_msgs_to}]")
                            try:
                                self._broadcast_to_dest(recv_payload, client)
                            except Exception as e:
                                raise e
                        # If the client is connected to the server the message is transmitted to all clients
                        else:
                            self.console.log(f"<<{recv_payload.username}>> {recv_payload.get_message()}",
                                             style="bold purple")
                            try:
                                self._broadcast(recv_payload)
                            except Exception as e:
                                raise e
                    # Sent warning, client is not connected to anyone
                    else:
                        payload = ChatPayload()
                        payload.by = "Server"
                        payload.username = "Server"
                        payload.text_payload = "[Error: You're not connect with anyone]\nType /users for see " \
                                               "active users"
                        client.send(payload)
            # Handling any exception as a true graduation student, not specifying any of them
            except Exception as e:
                self.console.log("Exception Detected:", style="bold red")
                self.console.print_exception()

                # Prints the User's Connection information
                user_data_table = Table(title=f"CONNECTION WITH {client.username} WAS FORCED TO BROKE",
                                        style="bold red")
                user_data_table.add_column("Field", justify="left")
                user_data_table.add_column("Connection", justify="left")
                user_data_table.add_row("Username", client.username)
                user_data_table.add_row("Hostname", client.hostname)
                user_data_table.add_row("IP Address", client.address[0])
                user_data_table.add_row("Port", str(client.address[1]))
                user_data_table.add_row("Connected Since", client.connected_since())

                self.console.print(user_data_table)
                del self._list_of_clients[client.username]
                # TODO: Disconnect client from server
                break

    # Broadcast a message to all clients
    def _broadcast(self, payload: ChatPayload):
        payload.username += " (Broadcast)" # Add to message that is a broadcast
        for client in self._list_of_clients:
            if client != "Server":
                try:
                    self._list_of_clients[client].send(payload)
                except Exception as e:
                    self.console.log("Exception Detected:", style="bold red")
                    self.console.print_exception()
                    continue

    # Broadcast a message to a specific client
    def _broadcast_to_dest(self, payload: ChatPayload, sender: User):
        try:
            self._list_of_clients[sender.sending_msgs_to].send(payload)
            sender.send(payload)
        except Exception as e:
            self.console.log("Exception Detected:", style="bold red")
            self.console.print_exception()

    # Send a list of users to the client
    def _send_list_of_users(self, clients: User):
        payload = ChatPayload()
        payload.by = "Server"
        payload.username = "Server"
        users_list = ""
        for clients_conn in self._list_of_clients:
            users_list += f"{clients_conn} @ {self._list_of_clients[clients_conn].hostname}\n"
        payload.text_payload = f"The following {len(self._list_of_clients)} user(s) are available: " \
                               f"(User Server broadcast to all)\n" \
                               f"{users_list}"
        clients.send(payload)

    # Connect a user to another
    def _conn_with_user(self, client: User, user_to_connect_with: str):
        payload = ChatPayload()
        payload.by = "Server"
        payload.username = "Server"
        try:
            user = self._list_of_clients[client.username]
            user.sending_msgs_to = user_to_connect_with
            self._list_of_clients.update({client.username: user})
            payload.text_payload = f"You are now connected with {user_to_connect_with} @ " \
                                   f"{self._list_of_clients[user_to_connect_with].hostname}"
            self._print_clients_connections()
            client.send(payload)
        except Exception as e:
            self.console.log("Exception Detected:", style="bold red")
            self.console.print_exception()
            payload.text_payload = f"{user_to_connect_with} is not available"
            client.send(payload)

    # Prints the list of clients and their connections
    def _print_clients_connections(self):
        print(f"[{datetime.now()}] Clients connections:")
        connections_table = Table(title="CONNECTIONS", style="bold white")
        connections_table.add_column("User", justify="left")
        connections_table.add_column("is connected to", justify="left")
        # Loop through the list of clients and print their connections
        for client in self._list_of_clients:
            a = self._list_of_clients[client]
            if a.sending_msgs_to is None:
                connections_table.add_row(f"{a.username}@{a.hostname}", "No one")
            else:
                b = self._list_of_clients[a.sending_msgs_to]
                connections_table.add_row(f"{a.username}@{a.hostname}", f"{b.username}@{b.hostname}")
        self.console.print(connections_table)

    # Client is sending a file
    def _file_transfer(self, payload: ChatPayload, client: User, size: int):
        # If client is not connected to anyone, a warning is sent
        if client.sending_msgs_to is not None:
            # If the client is not connected to the server, the message is sent to destination
            if client.sending_msgs_to != "Server":
                self.console.log(f"[{payload.username}] --> [{client.sending_msgs_to}]")
                try:
                    dest = self._list_of_clients[client.sending_msgs_to]
                    dest.send(payload)

                    temp2 = ChatPayload()
                    temp2.by = "Server"
                    temp2.username = "Server"
                    temp2.text_payload = f"File transfer to {client.sending_msgs_to} was successful"
                    client.send(temp2)
                except Exception as e:
                    temp2 = ChatPayload()
                    temp2.by = "Server"
                    temp2.username = "Server"
                    temp2.text_payload = f"File transfer to {client.sending_msgs_to} failed"
                    client.send(temp2)
            # If the client is connected to the server transfers are not allowed
            else:
                payload = ChatPayload()
                payload.by = "Server"
                payload.username = "Server"
                payload.text_payload = "[Error: You're not allowed to send files in broadcast mode]"
                client.send(payload)
        # Sent warning, client is not connected to anyone
        else:
            payload = ChatPayload()
            payload.by = "Server"
            payload.username = "Server"
            payload.text_payload = "[Error: You're not connect with anyone]\nType /users for see " \
                                   "active users"
            client.send(payload)

    # Destructor
    def __del__(self):
        try:
            print(f"[{datetime.now()}] Connection Closed")
            print(f"[{datetime.now()}] Server Closed")
        except Exception as e:
            print(f"[{datetime.now()}] Exception Detected:")
            self.console.print_exception()
