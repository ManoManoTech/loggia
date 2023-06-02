from __future__ import annotations

import logging
from typing import Literal

from mm_utils.logging_utils.constants import PALETTES
from mm_utils.utils.colorsutils import ansi_end, ansi_fg

# pylint: disable=consider-using-f-string


class PrettyFormatter(logging.Formatter):
    # pylint: disable=protected-access
    def _set_format(self, fmt: str, style: Literal["%"] | Literal["$"] | Literal["{"] = "%") -> None:
        self._style = logging._STYLES[style][0](fmt)  # type: ignore  # Mysticism 🤔
        self._fmt = self._style._fmt

    def format(self, record: logging.LogRecord) -> str:
        # Reference attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
        palette = PALETTES.get(record.levelno, PALETTES[logging.DEBUG])
        self._set_format(
            f"{ansi_fg(palette[0])}%(asctime)s "
            f"{ansi_fg(palette[1])}%(levelname)-8s "
            f"{ansi_fg(palette[2])}%(name)s:%(lineno)d "
            f"{ansi_fg(palette[3])}%(message)s"
            f"{ansi_end()}",
        )
        return super().format(record)
