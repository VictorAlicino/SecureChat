import socket
import os
from Server import Server

if __name__ == "__main__":
    print("Welcome to secure Chat Server by Alicino")
    target_ip = None
    target_port = None

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"The Server IP Address is: {local_ip}")
    print(f"The Hostname is: {hostname}")

    print(f"\nWould you like to setup the Chat on this IP Address ({local_ip})? [Y/N]")
    choice1 = input()
    if choice1 == "N":
        target_ip = input("Type the IP Address you would like to run the application on: ")
    else:
        target_ip = local_ip

    target_port = int(input("Which Port the application will run on: "))

    server = Server(local_ip, target_port)
    server.loop()

