import socket


class Chat:
    def __init__(self, ip_address: str, port: bytes):
        _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        _server.bind((ip_address, port))
        _server.listen(100)
        _list_of_clients = []
