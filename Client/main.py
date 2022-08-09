from tkinter import simpledialog
from rich.console import Console
from Chat_Client import ChatClient
from rich.prompt import Prompt, IntPrompt, Confirm
from tkinter import *

if __name__ == "__main__":
    console = Console()
    console.rule("[bold blue] Chat Client")
    username = Prompt.ask("What is your username?")
    client = ChatClient(username)
    client.username = username
    console.rule("[bold blue] Server Information")
    client.server_ip_addr = Prompt.ask("What is the IP address of the server?")
    client.server_port = IntPrompt.ask("What is the port of the server?")
    tls_required = Confirm.ask(f"Do you wish to encrypt your connection?")
    client.secure_connection = tls_required
    conn = None
    while True:
        try:
            with console.status("Connecting to server, please wait", spinner='material', speed=0.5):
                conn = ChatClient.connect(client)
                break
        except FileNotFoundError as e:
            console.rule("[bold red] Error")
            console.log("Certificate keys are not found. Please make sure you have the correct keys.", style="bold red")
            user_retry = Confirm.ask(f"Do you want to retry?")
            if not user_retry:
                exit(1)
        except OSError as e:
            console.rule("[bold red] Error")
            console.print_exception(width=0)
            user_retry = Confirm.ask(f"Do you want to retry?")
            if not user_retry:
                exit(1)
