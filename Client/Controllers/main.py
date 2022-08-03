from Chat_Client import ChatClient
from Views.GUI import init

if __name__ == "__main__":
    root = init()
    ip_address = input("Digite o IP: ")
    port = int(input("Digite a Porta: "))
    conn = ChatClient(ip_address, port)
    conn.loop()
