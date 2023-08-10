"""Main module for logging configuration, using standard logging."""
from __future__ import annotations
from collections.abc import Mapping

import logging
import logging.config
import sys
from typing import TYPE_CHECKING, Any

from mm_logger.stdlib_formatters.json_formatter import CustomJsonFormatter, CustomJsonEncoder
from mm_logger.conf import LoggerConfiguration


if TYPE_CHECKING:
    from types import TracebackType


def patch_to_add_level(level_number: int, level_name: str) -> None:
    """Add a new level to the standard logger.

    Sanity check for existing levels is left as an exercise to the user.
    XXX(dugab): Some of these statements may be redundant.
    """
    # pylint: disable=protected-access
    # pyright: reportGeneralTypeIssues=false
    # ruff: noqa: SLF001
    level_name_upper = level_name.upper()
    level_name.lower()
    logging.addLevelName(level_number, level_name_upper)


patch_to_add_level(5, "trace")
patch_to_add_level(25, "success")


def _build_json_formatter() -> dict[str, type[logging.Formatter] | Any]:
    attr_whitelist = {"name", "levelname", "pathname", "lineno", "funcName"}
    attrs = [x for x in CustomJsonFormatter.RESERVED_ATTRS if x not in attr_whitelist]
    return {
        "()": CustomJsonFormatter,
        "json_indent": None,
        "json_encoder": CustomJsonEncoder,
        "reserved_attrs": attrs,
        "timestamp": True,
    }


def prelogger_error(msg, exc=None):
    print(msg)
    if exc:
        print(exc)


def initialize(conf: LoggerConfiguration | Mapping | None = None) -> None:
    if conf is None:
        conf = LoggerConfiguration()
    if isinstance(conf, Mapping):
        conf = LoggerConfiguration(conf)
    if not isinstance(conf, LoggerConfiguration):
        raise TypeError("initialize() accepts LoggerConfiguration "
                        "instances or mappings (like a dict).")

    assert "formatters" in conf._dictconfig  # noqa: S101
    conf._dictconfig["formatters"]["structured"] = _build_json_formatter()

    if conf.set_excepthook:
        _set_excepthook(logging.getLogger())

    # XXX sys.unraisablehook
    # XXX threading.excepthook
    # XXX asyncio bullshit?
    # XXX audit subsystem bridge

    if conf.capture_warnings:
        # XXX test
        logging.captureWarnings(capture=True)

    if conf.capture_loguru:
        try:
            from mm_logger.loguru_sink import configure_loguru
            configure_loguru(conf)
        except ImportError as e:
            prelogger_error("Failed to configure loguru! Is is installed?", e)

    logging.config.dictConfig(conf._dictconfig)


def _set_excepthook(logger: logging.Logger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook
