from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from hypercorn.logging import Logger

from loggia.constants import HYPERCORN_ATTRIBUTES_MAP, SAFE_HEADER_ATTRIBUTES

if TYPE_CHECKING:
    from collections.abc import Mapping

    from hypercorn.config import Config
    from hypercorn.typing import ResponseSummary, WWWScope


class HypercornLogger(Logger):
    """Hypercorn logger that uses standard logging..

    From https://gist.github.com/airhorns/c2d34b2c823541fc0b32e5c853aab7e7
    A stripped down version of https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py to provide structlog logging in gunicorn
    Modified from https://stevetarver.github.io/2017/05/10/python-falcon-logging.html.
    """

    error_logger: logging.Logger
    access_logger: logging.Logger

    def __init__(self, cfg: Config):  # pylint: disable=super-init-not-called
        self.error_logger = logging.getLogger("hypercorn.error")
        self.access_logger = logging.getLogger("hypercorn.access")
        self.cfg = cfg
        self.access_log_format = cfg.access_log_format.replace("%(t)s ", "").lstrip("- ")

    async def access(self, request: WWWScope, response: ResponseSummary | None, request_time: float) -> None:
        # XXX(dugab): Url vs URI?
        # XXX Check duration is in ns
        atoms: Mapping[str, float | int | str] = self.atoms(request, response, request_time)
        # Add all headers in the HEADER_ATTRIBUTES list to the log, or any header starting with x- or sec-
        # Keep in minds that headers are case insensitive, so we need to lowercase them
        # request["headers"] is a tuple of bytes
        headers: dict[str, str] = {}

        for key_b, value in request["headers"]:
            key = key_b.decode("latin1").lower()
            if key in SAFE_HEADER_ATTRIBUTES or key.startswith(("x-", "sec-")):
                headers["http.headers." + key] = value.decode("latin1")

        # Same for response headers in http.response_headers
        if response is not None:
            for key_b, value in response["headers"]:
                key = key_b.decode("latin1").lower()
                if key in SAFE_HEADER_ATTRIBUTES or key.startswith(("x-", "sec-")):
                    headers["http.response_headers." + key] = value.decode("latin1")
        self.access_logger.info(  # pylint: disable=logging-not-lazy
            self.access_log_format % atoms,  # noqa: G002
            extra={HYPERCORN_ATTRIBUTES_MAP[k]: v for k, v in atoms.items() if k in HYPERCORN_ATTRIBUTES_MAP} | headers,  # type: ignore[operator]
        )
