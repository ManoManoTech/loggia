from __future__ import annotations

import logging
from typing import Any, Literal

from mm_logger.constants import PALETTES
from mm_logger.utils.colorsutils import ansi_end, ansi_fg

# pylint: disable=consider-using-f-string


class PrettyFormatter(logging.Formatter):
    """A custom formatter for logging that uses colors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._std_fields = set(logging.makeLogRecord({}).__dict__.keys())

    # pylint: disable=protected-access
    def _set_format(self, fmt: str, style: Literal["%"] | Literal["$"] | Literal["{"] = "%") -> None:
        self._style = logging._STYLES[style][0](fmt)  # type: ignore[operator]  # type: ignore[reportGeneralTypeIssues] # Mysticism 🤔
        self._fmt = self._style._fmt

    def format(self, record: logging.LogRecord) -> str:
        # Reference attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
        palette = PALETTES.get(record.levelno, PALETTES[logging.DEBUG])

        pretty_extra = "\n  ".join(
            f"{ansi_fg(palette[2])}{k}{ansi_end()}={ansi_fg(palette[3])}{v}"
            for k, v in record.__dict__.items()
            if k not in self._std_fields
        )

        if pretty_extra:
            pretty_extra = f"\n  {pretty_extra}"

        self._set_format(
            f"{ansi_fg(palette[0])}%(asctime)s "
            f"{ansi_fg(palette[1])}%(levelname)-8s "
            f"{ansi_fg(palette[2])}%(name)s:%(lineno)d "
            f"{ansi_fg(palette[3])}%(message)s"
            f"{pretty_extra}"
            f"{ansi_end()}",
        )
        return super().format(record)
