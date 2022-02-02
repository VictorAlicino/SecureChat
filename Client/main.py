from Chat_Client import ChatClient

if __name__ == "__main__":
    ip_address = input("Digite o IP: ")
    port = int(input("Digite a Porta: "))
    conn = ChatClient(ip_address, port)
    conn.loop()
