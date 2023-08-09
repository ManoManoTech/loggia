from typing import TYPE_CHECKING

import structlog
from hypercorn.config import Config
from hypercorn.logging import Logger

from mm_logs.constants import HYPERCORN_ATTRIBUTES_MAP, SAFE_HEADER_ATTRIBUTES

if TYPE_CHECKING:
    from collections.abc import Mapping

    from hypercorn.typing import ResponseSummary, WWWScope


class HypercornLogger(Logger):
    """Hypercorn logger that uses structlog.

    From https://gist.github.com/airhorns/c2d34b2c823541fc0b32e5c853aab7e7
    A stripped down version of https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py to provide structlog logging in gunicorn
    Modified from http://stevetarver.github.io/2017/05/10/python-falcon-logging.html.
    """

    def __init__(self, cfg: Config):  # pylint: disable=super-init-not-called
        self.error_logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("hypercorn.error")  # type: ignore[assignment]
        self.access_logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("hypercorn.access")  # type: ignore[assignment]
        self.cfg = cfg
        self.access_log_format = cfg.access_log_format.replace("%(t)s ", "").lstrip("- ")

    async def access(self, request: "WWWScope", response: "ResponseSummary", request_time: float) -> None:
        # XXX(dugab): Url vs URI?
        # XXX Check duration is in ns
        atoms: Mapping[str, float | int | str] = self.atoms(request, response, request_time)
        # Add all headers in the HEADER_ATTRIBUTES list to the log, or any header starting with x- or sec-
        # Keep in minds that headers are case insensitive, so we need to lowercase them
        # request["headers"] is a tuple of bytes
        # key: name.decode('latin1').lower()
        # Value: value.decode('latin1')
        headers: dict[str, str] = {}

        for key_b, value in request["headers"]:
            key = key_b.decode("latin1").lower()
            if key in SAFE_HEADER_ATTRIBUTES or key.startswith(("x-", "sec-")):
                headers["http.headers." + key] = value.decode("latin1")
        # Same for response headers in http.response_headers
        for key_b, value in response["headers"]:
            key = key_b.decode("latin1").lower()
            if key in SAFE_HEADER_ATTRIBUTES or key.startswith(("x-", "sec-")):
                headers["http.response_headers." + key] = value.decode("latin1")
        self.access_logger.info(
            self.access_log_format % atoms,  # noqa: G002
            **{HYPERCORN_ATTRIBUTES_MAP[k]: v for k, v in atoms.items() if k in HYPERCORN_ATTRIBUTES_MAP},
            **headers,
        )
