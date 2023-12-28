from __future__ import annotations

import logging
from typing import Any, Literal

from loggia.constants import FORMAT_FIELDS, PALETTES
from loggia.utils.colorsutils import ansi_end, ansi_fg
from loggia.utils.logrecordutils import extra_fields, popattr

# pylint: disable=consider-using-f-string

std_log = logging.Logger._log


def patched_log(*args: tuple[Any, ...], **kwargs: Any) -> Any:
    if "stacklevel" in kwargs:
        kwargs["stacklevel"] += 1
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["_fmt_with_filename"] = True
    else:
        kwargs["stacklevel"] = 2
    return std_log(*args, **kwargs)  # type: ignore[arg-type]


logging.Logger._log = patched_log  # type: ignore[method-assign]


class PrettyFormatter(logging.Formatter):
    """A custom formatter for logging that uses colors."""

    default_time_format = "%H:%M:%S"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    # pylint: disable=protected-access
    def _set_format(self, fmt: str, style: Literal["%", "$", "{"] = "%") -> None:
        self._style = logging._STYLES[style][0](fmt)  # type: ignore[operator]  # type: ignore[reportGeneralTypeIssues] # Mysticism 🤔
        self._fmt = self._style._fmt

    def format(self, record: logging.LogRecord) -> str:
        # Reference attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
        with_filename = popattr(record, "_fmt_with_filename", default=False)
        palette = PALETTES.get(record.levelno, PALETTES[logging.DEBUG])

        pretty_extra = "\n  ".join(
            f"{ansi_fg(palette[2])}{k}{ansi_end()}={ansi_fg(palette[3])}{v}" for k, v in extra_fields(record, FORMAT_FIELDS)
        )

        if pretty_extra:
            # Sanitize extra so that they are not formatted by percent formatter
            pretty_extra = f"\n  {pretty_extra}".replace("%", "%%")

        if with_filename:
            fmt = (
                f"{ansi_fg(palette[0])}%(asctime)s "
                f"{ansi_fg(palette[1])}%(levelname)-8s "
                f"{ansi_fg(palette[2])}%(name)s "
                f"{ansi_fg(palette[2])}%(filename)s:%(lineno)d "
                f"{ansi_fg(palette[3])}%(message)s"
                f"{pretty_extra}"
                f"{ansi_end()}"
            )
        else:
            fmt = (
                f"{ansi_fg(palette[0])}%(asctime)s "
                f"{ansi_fg(palette[1])}%(levelname)-8s "
                f"{ansi_fg(palette[2])}%(name)s:%(lineno)d "
                f"{ansi_fg(palette[3])}%(message)s"
                f"{pretty_extra}"
                f"{ansi_end()}"
            )

        self._set_format(fmt)
        return super().format(record)
