"""Constants for the loggia package."""
import logging.config
import re
from typing import Final

FORMAT_FIELDS = ["asctime", "levelname", "name", "lineno", "message", "filename"]
"""Fields use in the formatter"""

SAFE_HEADER_ATTRIBUTES: Final[list[str]] = [
    "accept",
    "accept-encoding",
    "accept-language",
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "cache-control",
    "connection",
    "content-length",
    "content-encoding",
    "content-length",
    "content-type",
    "content-language",
    "content-range",
    "content-disposition",
    "cookie",
    "etag",
    "pragma",
]
"""Headers that can be safely logged."""

HYPERCORN_ATTRIBUTES_MAP: Final[dict[str, str]] = {
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
"""Map of hypercorn log format characters to standard logging attributes."""


GUNICORN_HYPERCORN_KEY_RE: Final[re.Pattern[str]] = re.compile("{([^}]+)}")
"""Regex to match gunicorn log format keys."""


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
"""A dictionary of color names and their HTML color codes."""

PALETTES: Final[dict[int, tuple[str, str, str, str]]] = {
    logging.NOTSET: ("Blue Gray", "Sky", "Stone Blue", "White Blue"),
    5: ("Pink", "Pink White", "Pink", "Ivory"),  # Trace level
    logging.DEBUG: ("Blue Gray", "Sky", "Stone Blue", "White Blue"),
    logging.INFO: ("Forest Green", "Lint", "Emerald Green", "Pale Lint"),
    25: ("Forest Green", "Lint", "Emerald Green", "Pale Lint"),  # Success level
    logging.WARNING: ("Nude", "Tan", "Nude", "Sand Dollar"),
    logging.ERROR: ("Hot Pink", "Fuchsia", "Pink", "Red"),
    logging.CRITICAL: ("Hot Pink", "Fuchsia", "Pink", "Red"),
}
"""A dictionary of log levels and their color palettes."""


BASE_DICTCONFIG: Final["logging.config._DictConfigArgs"] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "propagate": True,
            "level": "INFO",
        },
    },
}
"""The base dictconfig for loggia.

See [standard logging.config.dictConfig][logging.config.dictConfig] for details about this.

NB: We do not encourage you to modify the base dictconfig, but it is the ultimate escape hatch,
where anything standard logging can do, you can do too. Remember anything put inside that dict
has the lowest precedence over any kind of configuration in Loggia.
"""


TRUTHY_STRINGS = {"Y", "YES", "JA", "OUI", "1", "TRUE", "ENABLED", "ACTIVATED", "ARMED"}


FALSY_STRINGS = {"N", "NO", "NEIN", "NON", "0", "FALSE", "DISABLED", "DEACTIVATED", "DISARMED", "BY CHTULU, NO!"}
