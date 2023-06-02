from typing import Mapping

import structlog
from hypercorn.config import Config
from hypercorn.logging import Logger
from hypercorn.typing import ResponseSummary, WWWScope

# print("TEST")
from mm_utils.logging_utils.structlog_utils import log

log.configure_logging()
HEADER_ATTRIBUTES = [
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
HYPERCORN_MAP = {
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


class HypercornLogger(Logger):
    """
    From https://gist.github.com/airhorns/c2d34b2c823541fc0b32e5c853aab7e7
    A stripped down version of https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py to provide structlog logging in gunicorn
    Modified from http://stevetarver.github.io/2017/05/10/python-falcon-logging.html
    """

    def __init__(self, cfg: Config):
        # print("O")
        self.error_logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("hypercorn.error")
        self.access_logger: structlog.stdlib.BoundLogger = structlog.stdlib.get_logger("hypercorn.access")
        self.cfg = cfg
        self.access_log_format = cfg.access_log_format

    # def exception(self, msg, *args, **kwargs) -> None:
    #     self._error_logger.exception(msg, *args, **kwargs)

    # def log(self, lvl, msg, *args, **kwargs) -> None:
    #     self._error_logger.log(lvl, msg, *args, **kwargs)
    # def access(self, request: WWWScope, response: ResponseSummary, request_time: float) -> Coroutine[Any, Any, None]:
    #     return await super().access(request, response, request_time)

    async def access(self, request: "WWWScope", response: "ResponseSummary", request_time: float) -> None:
        # XXX Url vs URI?
        # XXX Check duration is in ns
        atoms: Mapping[str, float | int | str] = self.atoms(request, response, request_time)
        # Add all headers in the HEADER_ATTRIBUTES list to the log, or any header starting with x- or sec-
        # Keep in minds that headers are case insensitive, so we need to lowercase them
        # request["headers"] is a tuple of bytes
        # key: name.decode('latin1').lower()
        # Value: value.decode('latin1')
        headers = {}
        # Convert microseconds to nanoseconds
        atoms["D"] = atoms["D"] * 1e3
        for key_b, value in request["headers"]:
            key = key_b.decode("latin1").lower()
            if key in HEADER_ATTRIBUTES or key.startswith("x-") or key.startswith("sec-"):
                headers["http.headers." + key] = value.decode("latin1")
        # Same for response headers in http.response_headers
        for key_b, value in response["headers"]:
            key = key_b.decode("latin1").lower()
            if key in HEADER_ATTRIBUTES or key.startswith("x-") or key.startswith("sec-"):
                headers["http.response_headers." + key] = value.decode("latin1")

        # atoms["http.url_details"] = request["url_details"]
        self.access_logger.info("access", **{HYPERCORN_MAP[k]: v for k, v in atoms.items() if k in HYPERCORN_MAP}, **headers)

    # from ipdb import set_trace

    # set_trace()
    # if isinstance(status, str):
    #     status = status.split(None, 1)[0]

    # duration_ns: float | int = request_time.total_seconds() * 1e9
    # self._access_logger.info(
    #     "",
    #     duration=duration_ns,
    #     **{
    #         # "http.name": environ["REQUEST_METHOD"],
    #         "http.url": environ["RAW_URI"],
    #         "http.status_code": status,
    #         "http.method": environ["REQUEST_METHOD"],
    #         "http.referer": environ.get("HTTP_REFERER", ""),
    #         "http.request_id": environ.get("HTTP_X_REQUEST_ID", ""),
    #         "http.version": environ.get("SERVER_PROTOCOL", ""),
    #         "http.useragent": environ.get("HTTP_USER_AGENT", ""),
    #         "logger.pid": os.getpid(),
    #         "http.response_length": getattr(resp, "sent", None),
    #     },
    #     request_time_seconds="%d.%06d" % (request_time.seconds, request_time.microseconds),
    # )
