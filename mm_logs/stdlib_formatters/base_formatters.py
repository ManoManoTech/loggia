from socket import socket
from typing import Any

from pythonjsonlogger.jsonlogger import JsonEncoder


class CustomJsonEncoder(JsonEncoder):
    def encode(self, o: Any) -> str:
        if isinstance(o, socket):
            return super().encode({"socket": {"peer": o.getpeername()}})
        return super().encode(o)
