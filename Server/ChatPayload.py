from datetime import datetime


class ChatPayload:
    message_time = datetime.now()  # Time when the message was sent
    to_ip = None  # Receiver IP
    by = None  # Sender Name
    raw_byte = None  # Raw bytes payload
    format_name = None  # Raw Bytes format
    text_payload = None  # Text payload

    def __int__(self, by: str, to: str, message: str):
        self.by = by
        self.to_ip = to
        self.text_payload = message

    @classmethod
    def send_bytes(cls, by: str, to: str, bytes_to_send: bytes):
        cls.by = by
        cls.to_ip = to
        cls.text_payload = bytes_to_send

    def get_message(self):
        return str(self.text_payload)
