from tkinter import simpledialog
from Model.Chat_Client import ChatClient
import Views.GUI
from Views.GUI import *

if __name__ == "__main__":
    GUI = Views.GUI.UserInterface("Chat Server")
    username = simpledialog.askstring("Username", "What is your username?")
    client = ChatClient(username)
    client.username = username
    client.server_ip_addr = simpledialog.askstring("IP Address", "What is the IP Address of the Server?")
    client.server_port = int(simpledialog.askstring("Port", "What is the Port of the Server?"))
    conn = None
    while True:
        try:
            conn = ChatClient.connect(client)
            break
        except OSError as e:
            user_retry = messagebox.askretrycancel(f"Error connecting to {client.server_ip_addr}", f"{e}")
            if not user_retry:
                exit(1)
    messagebox.showinfo("Connected", "You are now connected to the Server")
    ChatClient.loop(client)
