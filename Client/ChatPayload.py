from datetime import datetime


class ChatPayload:
    def __int__(self, by: str, to: str, message: str):
        self.by = by
        self.to_ip = to
        self.text_payload = message

    username = None # Sender Username
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

    def __str__(self):
        return f"Payload -----------\n" \
               f"\tSender:          {self.by}\n" \
               f"\tReceiver:        {self.to_ip}\n" \
               f"\tSender Username: {self.username}\n" \
               f"\tTime:            {self.message_time}\n" \
               f"\tMessage:         {self.text_payload}\n\n" \
               f"\tFormat Name:     {self.format_name}\n" \
               f"\tRaw Bytes:       {self.raw_byte}\n" \
               f"Payload -----------"
