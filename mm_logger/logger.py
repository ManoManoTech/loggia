"""Main module for logging configuration, using standard logging."""
from __future__ import annotations

import logging
import logging.config
import sys
from typing import TYPE_CHECKING, Any, Final

from mm_logger.settings import ActiveMMLogsConfig, LoggerConfigurationError, MMLogsConfig, MMLogsConfigPartial
from mm_logger.utils.dictutils import deep_merge_log_config
from mm_logger.stdlib_formatters.json_formatter import CustomJsonFormatter, CustomJsonEncoder

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from inspect import Traceback
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
    level_name_lower = level_name.lower()
    logging.addLevelName(level_number, level_name_upper)

patch_to_add_level(5, "trace")
patch_to_add_level(25, "success")


def _get_json_formatter() -> dict[str, type[logging.Formatter] | Any]:
    attr_whitelist = {"name", "levelname", "pathname", "lineno", "funcName"}
    attrs = [x for x in CustomJsonFormatter.RESERVED_ATTRS if x not in attr_whitelist]
    return {
        "()": CustomJsonFormatter,
        "json_indent": None,
        "json_encoder": CustomJsonEncoder,
        "reserved_attrs": attrs,
        "timestamp": True,
    }


def configure_logging(custom_config: MMLogsConfig | MMLogsConfigPartial | None = None) -> MMLogsConfig:
    """Main function to configure logging.

    Args:
        custom_config (MMLogsConfig | None, optional): Your custom config. If None, a default config will be used.
    """
    mm_logger_config = _get_logger_config(custom_config)
    # Merge the custom stdlib logging config with the default
    if mm_logger_config.custom_stdlib_logging_dict_config is not None:
        mm_logger_config.stdlib_logging_dict_config = deep_merge_log_config(
            mm_logger_config.stdlib_logging_dict_config, mm_logger_config.custom_stdlib_logging_dict_config
        )

    ActiveMMLogsConfig.store(mm_logger_config)

    config = mm_logger_config.stdlib_logging_dict_config  # XXX deepcopy
    config["formatters"]["structured"] = _get_json_formatter()

    # Assert for type checking only
    assert "handlers" in config, "Missing 'handlers' key in stdlib_logging_dict_config"  # noqa: S101
    assert "loggers" in config, "Missing 'loggers' key in stdlib_logging_dict_config"  # noqa: S101
    assert "formatters" in config, "Missing 'formatters' key in stdlib_logging_dict_config"  # noqa: S101
    assert isinstance(config["handlers"], dict)  # noqa: S101
    assert isinstance(config["loggers"], dict)  # noqa: S101
    assert isinstance(config["formatters"], dict)  # noqa: S101

    config["handlers"]["default"]["formatter"] = mm_logger_config.log_formatter_name
    config["handlers"]["default"]["level"] = mm_logger_config.log_level
    config["loggers"][""]["level"] = mm_logger_config.log_level

    if mm_logger_config.set_excepthook:
        _set_excepthook(logging.getLogger())

    # XXX sys.unraisablehook
    # XXX threading.excepthook
    # XXX asyncio bullshit?
    # XXX audit subsystem bridge

    if mm_logger_config.capture_warnings:
        # XXX test
        logging.captureWarnings(capture=True)

    if mm_logger_config.capture_loguru:
        try:
            from mm_logger.loguru_sink import configure_loguru

            configure_loguru(mm_logger_config)
        except ImportError as exc:
            mm_logger_config._configuration_errors.append(
                LoggerConfigurationError(
                    msg="Failed to configure loguru! Is is installed?",
                    exc=exc,
                ),
            )

    logging.config.dictConfig(config)

    logger = logging.getLogger()
    if mm_logger_config.debug_show_config:
        logger.debug("Logging configured", config=mm_logger_config)

    if len(mm_logger_config._configuration_errors) > 0:
        logger.error("Logging configured with errors", errors=mm_logger_config._configuration_errors)

    return mm_logger_config


def _get_logger_config(custom_config: MMLogsConfig | MMLogsConfigPartial | None) -> MMLogsConfig:
    """Create a config if none is provided, or merge the default config (dataclass) with the custom one (Partial typed dict) into the final config (dataclass)."""
    if custom_config is None:
        logging_config = MMLogsConfig()
    elif isinstance(custom_config, dict):
        logging_config = MMLogsConfig(**custom_config)
    elif isinstance(custom_config, MMLogsConfig):
        logging_config = custom_config

    return logging_config


def _set_excepthook(logger: logging.Logger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook
