from __future__ import annotations

import logging
from typing import Literal, Any, TypeVar

from mm_logger.constants import PALETTES
from mm_logger.utils.colorsutils import ansi_end, ansi_fg

# pylint: disable=consider-using-f-string

T = TypeVar("T")
def _popattr(record: logging.LogRecord, attr: str, default: T) -> T:
    if not hasattr(record, attr):
        return default
    result = getattr(record, attr)
    delattr(record, attr)
    return result

std_log = logging.Logger._log
def patched_log(*args, **kwargs):
    if "stacklevel" in kwargs:
        kwargs["stacklevel"] += 1
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["_fmt_with_filename"] = True
    else:
        kwargs["stacklevel"] = 2
    std_log(*args, **kwargs)
logging.Logger._log = patched_log

class PrettyFormatter(logging.Formatter):
    """A custom formatter for logging that uses colors."""
    default_time_format = "%H:%M:%S"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._std_fields = set(logging.makeLogRecord({}).__dict__.keys())

    # pylint: disable=protected-access
    def _set_format(self, fmt: str, style: Literal["%"] | Literal["$"] | Literal["{"] = "%") -> None:
        self._style = logging._STYLES[style][0](fmt)  # type: ignore[operator]  # type: ignore[reportGeneralTypeIssues] # Mysticism 🤔
        self._fmt = self._style._fmt

    def format(self, record: logging.LogRecord) -> str:
        # Reference attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
        with_filename = _popattr(record, "_fmt_with_filename", False)
        palette = PALETTES.get(record.levelno, PALETTES[logging.DEBUG])

        pretty_extra = "\n  ".join(
            f"{ansi_fg(palette[2])}{k}{ansi_end()}={ansi_fg(palette[3])}{v}"
            for k, v in record.__dict__.items()
            if k not in self._std_fields
        )

        if pretty_extra:
            pretty_extra = f"\n  {pretty_extra}"

        if with_filename:
            fmt = (f"{ansi_fg(palette[0])}%(asctime)s "
                   f"{ansi_fg(palette[1])}%(levelname)-8s "
                   f"{ansi_fg(palette[2])}%(name)s "
                   f"{ansi_fg(palette[2])}%(filename)s:%(lineno)d "
                   f"{ansi_fg(palette[3])}%(message)s"
                   f"{pretty_extra}"
                   f"{ansi_end()}")
        else:
            fmt = (f"{ansi_fg(palette[0])}%(asctime)s "
                   f"{ansi_fg(palette[1])}%(levelname)-8s "
                   f"{ansi_fg(palette[2])}%(name)s:%(lineno)d "
                   f"{ansi_fg(palette[3])}%(message)s"
                   f"{pretty_extra}"
                   f"{ansi_end()}")

        self._set_format(fmt)
        return super().format(record)
