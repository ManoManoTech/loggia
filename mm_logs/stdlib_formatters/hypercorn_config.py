"""From radiologist-python


Hypercorn config sample

https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#configuration-options
"""
# pylint: disable=invalid-name
from typing import Any

from mm_logs.stdlib_formatters.base_formatters import CustomJsonEncoder
from mm_logs.stdlib_formatters.hypercorn_json_formatter import AccessLogFilter, CustomJsonFormatter

bind = ["0.0.0.0:3000"]
keep_alive_timeout = 300
workers = 4
# Loguru prod
# loguru_production_mode()

# Access and error log https://pgjones.gitlab.io/hypercorn/how_to_guides/logging.html
loglevel = "INFO"
# config.logger_class = XXX

attr_whitelist = {"name", "levelname", "pathname", "lineno", "funcName"}
attrs = [x for x in CustomJsonFormatter.RESERVED_ATTRS if x not in attr_whitelist]
formatter: dict[str, type[CustomJsonFormatter] | Any] = {"()": CustomJsonFormatter}
formatter.update(
    {
        "json_indent": None,
        "json_encoder": CustomJsonEncoder,
        "reserved_attrs": attrs,
        "timestamp": True,
    },
)
base_level = loglevel
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "dynamicfmt": formatter,
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "dynamicfmt"},
    },
    "loggers": {
        "radiologist": {"handlers": ["console"], "level": base_level, "propagate": False},
        "ezsre": {"handlers": ["console"], "level": base_level, "propagate": False},
        "botocore": {"handlers": ["console"], "level": base_level, "propagate": False},
        "hypercorn.error": {
            "handlers": ["console"],
            "propagate": False,
        },
        "hypercorn.access": {"handlers": ["console"], "filters": ["accessfilter"], "propagate": False},
        "ddtrace": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
    "filters": {"accessfilter": {"()": AccessLogFilter}},
    "root": {
        "handlers": ["console"],
        "level": base_level,
        "propagate": False,
    },
}

accesslog = "-"
errorlog = "-"