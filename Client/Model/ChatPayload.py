from datetime import datetime


class ChatPayload:
    def __int__(self, by: str, to: str, message: str):
        self.by = by
        self.to_ip = to
        self.text_payload = message

    message_time = None  # Time when the message was sent, please use "datetime.now().strftime("%d/%m/%Y %H:%M:%S")"
    to_ip = None  # Receiver IP
    by = None  # Sender Name
    raw_byte = None  # Raw bytes payload
    format_name = None  # Raw Bytes format
    text_payload = None  # Text payload

    @classmethod
    def send_bytes(cls, by: str, to: str, bytes_to_send: bytes):
        cls.by = by
        cls.to_ip = to
        cls.text_payload = bytes_to_send

    def get_message(self):
        return str(self.text_payload)
