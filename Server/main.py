import socket
import os
from Chat import Chat

if __name__ == "__main__":
    print("Welcome to (unsecure) Chat Server by Alicino")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"The Server IP Address is: {local_ip}")
    print(f"The Hostname is: {hostname}")
    print(f"\nWould you like to setup the Chat on this IP Address ({local_ip})? [Y/N]")
    choice = input()
    available_ports = []
    if choice == "Y":
        print("Scanning available ports on this machine")
        progress = 0
        for port in range(100, 500):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)

            # returns an error indicator
            result = s.connect_ex((local_ip, port))
            if result == 0:
                available_ports.append(port)
            s.close()
            if port % 40:
                progress = progress + 10
                print(f"{port/100}%")
        print("Scanning completed")
        print(f"Available Ports: {available_ports}")
    server = Chat(local_ip, 5050)

