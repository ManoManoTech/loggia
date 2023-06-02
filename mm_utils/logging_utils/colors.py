from __future__ import annotations

import logging
from typing import Final

COLORS: Final[dict[str, str]] = {
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

PALETTES: Final[dict[int, tuple[str, str, str, str]]] = {
    logging.NOTSET: ("Blue Gray", "Sky", "Stone Blue", "White Blue"),
    logging.DEBUG: ("Blue Gray", "Sky", "Stone Blue", "White Blue"),
    logging.INFO: ("Forest Green", "Lint", "Emerald Green", "Pale Lint"),
    logging.WARNING: ("Nude", "Tan", "Nude", "Sand Dollar"),
    logging.ERROR: ("Hot Pink", "Fuchsia", "Pink", "Red"),
    logging.CRITICAL: ("Hot Pink", "Fuchsia", "Pink", "Red"),
}


def html_to_triple_dec(html_code: str) -> list[int]:
    return [int(x, 16) for x in (html_code[1:3], html_code[3:5], html_code[5:8])]


def ansi_fg(name: str) -> str:
    html_code = COLORS[name]
    return "\x1b[38;2;{};{};{}m".format(*html_to_triple_dec(html_code))


def ansi_end() -> str:
    return "\x1b[0m"
