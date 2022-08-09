import socket
import os
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from Server import Server

if __name__ == "__main__":
    console = Console()
    console.rule("[bold blue] Secure Chat Server")
    target_ip = None
    target_port = None

    # Get the host machine information
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname('localhost')
    console.print(f"[bold white] The Server IP Address is: {local_ip}")
    console.print(f"[bold white] The Server Hostname is: {hostname}")

    choice1 = Confirm.ask(f"Would you like to setup the Chat on this IP Address ({local_ip})?")
    if not choice1:
        target_ip = input("Type the IP Address you would like to run the application on: ")
    else:
        target_ip = local_ip

    target_port = int(input("Which Port the application will run on: "))

    # Create the server object
    server = Server(local_ip, target_port)
    server.accept_clients()

