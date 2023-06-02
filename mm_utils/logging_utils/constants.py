import re
from typing import Final

SAFE_HEADER_ATTRIBUTES: Final[list[str]] = [
    "accept",
    "accept-encoding",
    "accept-language",
    "access-control-allow-origin",
    "cache-control",
    "connection",
    "content_length",
    "content-encoding",
    "content-length",
    "content-type",
    "cookie",
    "etag",
    "pragma",
]
"""Headers that can be safely logged."""

HYPERCORN_ATTRIBUTES_MAP: Final[dict[str, str]] = {
    "s": "http.status_code",
    "m": "http.method",
    "f": "http.referer",
    "a": "http.useragent",
    "H": "http.version",
    "S": "http.url_details.scheme",
    "q": "http.url_details.queryString",
    "U": "http.url_details.path",
    "D": "duration",
}
"""Map of hypercorn log format characters to structlog attributes."""


GUNICORN_HYPERCORN_KEY_RE: Final[re.Pattern[str]] = re.compile("{([^}]+)}")
"""Regex to match gunicorn log format keys."""
