from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from types import TracebackType

UTC = timezone.utc


class BootstrapLoggerError(RuntimeError):
    pass


class BootstrapLogger:
    """BootstrapLogger for use before standard logging is setup.

    It basically captures all log calls properly - logs are properly written
    after logging is setup. (vaporware, presently clobbering stdout like a maniac)
    """

    deferred = False
    raise_on_log = False
    buf: list[_BootstrapLoggerEntry]

    def __init__(self) -> None:
        self.buf = []

    def warn(self, msg: str, exc: Exception | None = None) -> None:
        self.log("warn", msg, exc)

    def error(self, msg: str, exc: Exception | None = None) -> None:
        self.log("error", msg, exc)

    def log(self, level: str, msg: str, exc: Exception | None = None) -> None:
        levelno = logging._nameToLevel.get(level.upper(), logging.INFO)
        e = _BootstrapLoggerEntry(datetime.now(tz=UTC), levelno, msg, exc)

        if self.raise_on_log:
            raise BootstrapLoggerError(str(e))

        if not self.deferred:
            print(e)  # noqa: T201
        else:
            self.buf.append(e)

    def buf_to_logger(self, logger: logging.Logger) -> None:
        for e in self.buf:
            # XXX mess with logrecords to properly deal with the timestamp
            logger.log(e.level, e.msg, exc_info=e.exc_info)


class _BootstrapLoggerEntry(NamedTuple):
    ts: datetime
    level: int
    msg: str
    exc: Exception | None

    def __str__(self) -> str:
        lines = [f"[{self.levelstr}] {self.msg}"]
        if self.exc:
            lines.extend(traceback.format_exception(type(self.exc), self.exc, self.exc.__traceback__))
        return "\n".join(lines)

    @property
    def levelstr(self) -> str:
        return logging._levelToName.get(self.level, "???")

    @property
    def exc_info(self) -> None | tuple[type[Exception], Exception, TracebackType | None]:
        if self.exc:
            return (type(self.exc), self.exc, self.exc.__traceback__)
        return None


bootstrap_logger = BootstrapLogger()
