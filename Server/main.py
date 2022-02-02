import socket
import os
from Chat import Chat

if __name__ == "__main__":
    print("Welcome to (unsecure) Chat Server by Alicino")
    target_ip = None
    target_port = None
    available_ports = []

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

    print("Would you like to run the scanner to find available ports? [Y/N]")
    choice2 = input()
    if choice2 == "Y":
        print("Scanning available ports on this machine")
        print("This may take some time, go make a coffee...")
        progress = 0
        for port in range(100, 500):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)

            # returns an error indicator
            result = s.connect_ex((target_ip, port))
            if result == 0:
                available_ports.append(port)
            s.close()
        print("Scanning completed")
        print(f"Available Ports: {available_ports}")

    target_port = int(input("Which Port the application will run on: "))

    server = Chat(local_ip, target_port)
    server.loop()

