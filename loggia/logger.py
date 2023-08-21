"""Main module for logging configuration, using standard logging."""
from __future__ import annotations

import logging
import logging.config
from os import getenv
import sys
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from loggia.conf import LoggerConfiguration
from loggia._internal.bootstrap_logger import BootstrapLogger

if TYPE_CHECKING:
    from types import TracebackType


def _patch_to_add_level(level_number: int, level_name: str) -> None:
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


def initialize(conf: LoggerConfiguration | Mapping | None = None,
               presets: str | list[str] | None = None) -> None:
    """Initialize the logging system."""
    if conf is None:
        conf = LoggerConfiguration(presets=presets)
    if isinstance(conf, Mapping):
        conf = LoggerConfiguration(conf, presets=presets)
    if not isinstance(conf, LoggerConfiguration):
        raise TypeError("initialize() accepts LoggerConfiguration "
                        "instances or mappings (like a dict).")

    if conf.setup_excepthook:
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
            from loggia.loguru_sink import configure_loguru
            configure_loguru(conf)
            _patch_to_add_level(5, "trace")
            _patch_to_add_level(25, "success")
        except ImportError as e:
            BootstrapLogger.error("Failed to configure loguru! Is is installed?", e)

    logging.config.dictConfig(conf._dictconfig)


def _set_excepthook(logger: logging.Logger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook
