from __future__ import annotations

import logging

COLORS = {
    "Forest Green": "#086e3f",
    "Emerald Green": "#58ad72",
    "Lint": "#4bd676",
    "Pale Lint": "#75e097",
    "Fuchsia": "#fb4570",
    "Hot Pink": "#fb6b90",
    "Pink": "#fb8da0",
    "Pink White": "#efebe0",
    "Red": "#ed4040",
    "Ivory": "#f1ece4",
    "Nude": "#c3b090",
    "Sand Dollar": "#de943a",
    "Tan": "#92794f",
    "Blue Gray": "#8da7c4",
    "Sky": "#ace1fc",
    "Stone Blue": "#8da7c4",
    "White Blue": "#e5ddfc",
}

PALETTES = {
    logging.DEBUG: ["Blue Gray", "Sky", "Stone Blue", "White Blue"],
    logging.INFO: ["Forest Green", "Lint", "Emerald Green", "Pale Lint"],
    logging.WARN: ["Nude", "Tan", "Nude", "Sand Dollar"],
    logging.ERROR: ["Hot Pink", "Fuchsia", "Pink", "Red"],
    logging.CRITICAL: ["Hot Pink", "Fuchsia", "Pink", "Red"],
}
# pylint: disable=consider-using-f-string


def html_to_triple_dec(html_code):
    return list(map(lambda x: int(x, 16), (html_code[1:3], html_code[3:5], html_code[5:8])))


def ansi_fg(name: str) -> str:
    html_code = COLORS[name]
    return "\x1b[38;2;{};{};{}m".format(*html_to_triple_dec(html_code))


def ansi_end() -> str:
    return "\x1b[0m"


class PrettyFormatter(logging.Formatter):
    # pylint: disable=protected-access
    def _set_format(self, fmt, style="%"):
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
            f"{ansi_end()}"
        )
        return super().format(record)
