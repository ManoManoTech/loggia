# From radiologist-python

from radiologist.collector.util.hypercornlog import AccessLogFilter, CustomJsonEncoder, CustomJsonFormatter
from radiologist.collector.util.logging import loguru_production_mode

# Hypercorn config
# https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#configuration-options

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
formatter = {"()": CustomJsonFormatter}
formatter.update(
    dict(
        json_indent=None,
        json_encoder=CustomJsonEncoder,
        reserved_attrs=attrs,
        timestamp=True,
    )
)  # type: ignore
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

loguru_production_mode()