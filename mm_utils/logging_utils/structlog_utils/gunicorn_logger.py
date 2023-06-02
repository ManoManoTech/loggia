import datetime
import os
from typing import Any, Literal

import structlog
from gunicorn.config import Config as GunicornConfig
from gunicorn.http.message import Request
from gunicorn.http.wsgi import Response


class GunicornLogger:
    """
    From https://gist.github.com/airhorns/c2d34b2c823541fc0b32e5c853aab7e7
    A stripped down version of https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py to provide structlog logging in gunicorn
    Modified from http://stevetarver.github.io/2017/05/10/python-falcon-logging.html
    """

    def __init__(self, cfg: GunicornConfig) -> None:
        self._error_logger: structlog.stdlib.BoundLogger = structlog.get_logger("gunicorn.error")
        self._access_logger: structlog.stdlib.BoundLogger = structlog.get_logger("gunicorn.access")
        self.cfg: GunicornConfig = cfg

    def __getattr__(self, name: str | Literal["critical", "error", "warning", "info", "debug", "exception", "log"]) -> Any:
        if name in ["critical", "error", "warning", "info", "debug", "exception", "log"]:
            return getattr(self._error_logger, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def access(self, resp: Response, req: Request, environ: dict[str, str], request_time: datetime.timedelta) -> None:
        status = resp.status

        # set_trace()
        if isinstance(status, str):
            status = status.split(None, 1)[0]

        duration_ns: float | int = request_time.total_seconds() * 1e9
        self._access_logger.info(
            "",
            duration=duration_ns,
            **{
                # "http.name": environ["REQUEST_METHOD"],
                "http.url": environ["RAW_URI"],
                "http.status_code": status,
                "http.method": environ["REQUEST_METHOD"],
                "http.referer": environ.get("HTTP_REFERER", ""),
                "http.request_id": environ.get("HTTP_X_REQUEST_ID", ""),
                "http.version": environ.get("SERVER_PROTOCOL", ""),
                "http.useragent": environ.get("HTTP_USER_AGENT", ""),
                "logger.pid": os.getpid(),
                "http.response_length": getattr(resp, "sent", None),
            },
            request_time_seconds="%d.%06d" % (request_time.seconds, request_time.microseconds),
        )

    def close_on_exec(self, *args: Any, **kwargs: Any) -> None:
        pass
