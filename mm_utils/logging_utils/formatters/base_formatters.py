import re
from socket import socket
from typing import Any, TypeVar

from pythonjsonlogger.jsonlogger import JsonEncoder


GUNICORN_KEY_RE = re.compile("{([^}]+)}")
T = TypeVar("T")
K = TypeVar("K")


class CustomJsonEncoder(JsonEncoder):
    def encode(self, o: Any) -> str:
        if isinstance(o, socket):
            return super().encode(dict(socket=dict(peer=o.getpeername())))
        return super().encode(o)
