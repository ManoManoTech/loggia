"""Main module for logging configuration, using standard logging."""
from __future__ import annotations

import logging
import logging.config
import sys
import threading
from collections.abc import Mapping
from typing import TYPE_CHECKING

from loggia._internal.bootstrap_logger import bootstrap_logger
from loggia.conf import FlexibleFlag, LoggerConfiguration

if TYPE_CHECKING:
    from types import TracebackType


def _patch_to_add_level(level_number: int, level_name: str) -> None:
    """Add a new level to the standard logger.

    Sanity check for existing levels is left as an exercise to the user.
    XXX(dugab): Some of these statements may be redundant.
    """
    # pylint: disable=protected-access
    # ruff: noqa: SLF001
    level_name_upper = level_name.upper()
    logging.addLevelName(level_number, level_name_upper)


def _bootstrap_config(
    conf: LoggerConfiguration | dict[str, str] | None = None,
    presets: str | list[str] | None = None,
) -> LoggerConfiguration:
    if conf is None:
        conf = LoggerConfiguration(presets=presets)
    if isinstance(conf, Mapping):
        conf = LoggerConfiguration(settings=dict(conf), presets=presets)
    if not isinstance(conf, LoggerConfiguration):
        raise TypeError("initialize() accepts LoggerConfiguration instances or mappings (like a dict).")
    return conf


def initialize(conf: LoggerConfiguration | dict[str, str] | None = None, presets: str | list[str] | None = None) -> None:
    """Initialize the logging system."""
    conf = _bootstrap_config(conf, presets)

    if conf.setup_excepthook:
        _set_excepthook(logging.getLogger())

    if conf.setup_unraisablehook:
        _set_unraisablehook(logging.getLogger())

    if conf.setup_threading_excepthook:
        _set_threading_excepthook(logging.getLogger())

    # XXX asyncio bullshit?
    # XXX audit subsystem bridge

    if conf.capture_warnings:
        # XXX test
        logging.captureWarnings(capture=True)

    if conf.capture_loguru in (FlexibleFlag.AUTO, FlexibleFlag.ENABLED):
        try:
            from loggia.loguru_sink import configure_loguru

            _patch_to_add_level(5, "TRACE")
            _patch_to_add_level(25, "SUCCESS")
            configure_loguru(conf)
        except ModuleNotFoundError as e:
            if conf.capture_loguru == FlexibleFlag.ENABLED:
                bootstrap_logger.error("Failed to configure loguru! Is is installed?", e)

    # XXX Check that logger levels exists
    # BIM BAM BADABEEM BADABOOM, LOGGIA MAGICA!
    logging.config.dictConfig(conf._dictconfig)


def _set_excepthook(logger: logging.Logger) -> None:
    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook


def _set_unraisablehook(logger: logging.Logger) -> None:
    def _unraisablehook(unraisable: sys.UnraisableHookArgs) -> None:
        msg = f"Unraisable exception: {unraisable.err_msg}" if unraisable.err_msg else "Unraisable exception"
        # XXX we don't know how to test for exc_value=None
        logger.critical(msg, exc_info=(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback))  # type:ignore[arg-type]

    sys.unraisablehook = _unraisablehook


def _set_threading_excepthook(logger: logging.Logger) -> None:
    def _excepthook(args: threading.ExceptHookArgs) -> None:
        msg = f"Unhandled exception in thread: {args.exc_type}"
        # XXX we don't know how to test for exc_value=None
        logger.critical(msg, exc_info={args.exc_type, args.exc_value, args.exc_traceback})  # type:ignore[arg-type]

    threading.excepthook = _excepthook
