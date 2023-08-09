from socket import socket
from typing import Any

from pythonjsonlogger.jsonlogger import JsonEncoder


class CustomJsonEncoder(JsonEncoder):
    """Custom JSON encoder for xSGI server logs."""

    def encode(self, o: Any) -> str:
        if isinstance(o, socket):
            return super().encode({"socket": {"peer": o.getpeername()}})
        return super().encode(o)
