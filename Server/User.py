import pickle
from datetime import datetime
from ChatPayload import ChatPayload


class User:
    def __init__(self, connection: tuple, connection_time: datetime):
        self.hostname = None
        self.sending_msgs_to = None
        self.connection, self.address = connection
        self.username = None
        self._connected_since = connection_time

        # Check if it's a IPV4 or IPV6 connection
        if len(self.address) > 2:
            self.is_ipv6 = True
        else:
            self.is_ipv6 = False

    def send(self, payload: ChatPayload) -> ChatPayload:
        temp_payload = payload

        if temp_payload.to_ip is None:
            temp_payload.to_ip = self.address

        temp_payload.message_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        try:
            self.connection.send(pickle.dumps(temp_payload))
        except Exception as e:
            raise e

        return temp_payload

    def connected_since(self) -> str:
        return self._connected_since.strftime("%d/%m/%Y %H:%M:%S")

