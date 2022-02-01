import socket

if __name__ == "__main__":
    print("Welcome to (unsecure) Chat Server by Alicino")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"The Server IP Address is: {local_ip}")
    print(f"The Hostname is: {hostname}")
    
