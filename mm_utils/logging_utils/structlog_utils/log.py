import enum
import logging
import logging.config
import os
import sys
import timeit
import traceback
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from logging import Logger, LogRecord
from types import TracebackType
from typing import Any, ClassVar, Collection, Dict, Iterable, Literal, Optional, Union

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.typing import EventDict, Processor

from mm_utils.logging_utils.structlog_utils.processors import (
    CustomCallsiteParameterAdder,
    DataDogTraceInjectionProcessor,
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    RemoveKeysProcessor,
    add_log_level_number,
    datadog_add_log_level,
    datadog_add_logger_name,
    datadog_error_mapping_processor,
    extract_from_record_datadog,
)


def make_formatter_structured():
    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            datadog_error_mapping_processor,
            datadog_error_mapping_processor,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_logger_name,
            CustomCallsiteParameterAdder(
                [
                    CallsiteParameter.PATHNAME,
                    CallsiteParameter.FUNC_NAME,
                    CallsiteParameter.LINENO,
                    CallsiteParameter.THREAD_NAME,
                ],
                custom_attribute_names={
                    CallsiteParameter.THREAD_NAME: "logger.thread_name",
                    CallsiteParameter.PATHNAME: "logger.path_name",
                    CallsiteParameter.FUNC_NAME: "logger.method_name",
                    CallsiteParameter.LINENO: "logger.lineno",
                    # "logger": "logger.name",
                    # "level": "status",
                },
            ),
            EventAttributeMapper(
                {
                    CallsiteParameter.THREAD_NAME.value: "logger.thread_name",
                    CallsiteParameter.PATHNAME.value: "logger.path_name",
                    CallsiteParameter.FUNC_NAME.value: "logger.method_name",
                    CallsiteParameter.LINENO.value: "logger.lineno",
                    "logger": "logger.name",
                    "level": "status",
                }
            ),
            ManoManoDataDogAttributesProcessor(),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            # XXX Custom JSON Renderer (more performance?)
            structlog.processors.JSONRenderer(sort_keys=True, ensure_ascii=False, indent=2),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


def make_formatter_colored():
    # Import here to avoid structlog.dev import in production
    from mm_utils.logging_utils.structlog_utils.pretty_console_renderer import PrettyConsoleRenderer

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            structlog.processors.TimeStamper(fmt="iso", utc=False, key="timestamp"),
            CustomCallsiteParameterAdder(
                [
                    CallsiteParameter.LINENO,
                    CallsiteParameter.THREAD_NAME,
                    CallsiteParameter.PROCESS,
                    #  CallsiteParameter.PATHNAME
                ],
                additional_ignores=["mm_utils", "__main__"],
            ),
            structlog.stdlib.add_logger_name,
            # XXX Remove process and thread name from the log message (or format it differently)
            add_log_level_number,
            # XXX Make a version that supports custom log level
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            PrettyConsoleRenderer(colors=True, event_key="message"),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


"""Processors to be used for logs coming from standard logging."""
std_pre_chain: Iterable[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.PositionalArgumentsFormatter(),
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    structlog.stdlib.ExtraAdder(),  # XXX RESERVED ATTRIBUTES
    structlog.processors.add_log_level,
    structlog.processors.EventRenamer("message"),
]

"""Processors to be used for logs coming from structlog."""
struct_pre_chain: Iterable[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.add_log_level,
    structlog.processors.EventRenamer("message"),
    # Keep this last!
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]


class LoggingConfig:
    ignore_duplicate_processors: bool = False
    excepthook: bool = True

    def __init__(self, *args, **kwargs):
        self.log_level: int = get_log_level_number_from_env()
        self.formatter_name = get_main_formatter_name()
        self.config: "logging.config._DictConfigArgs" | None = None

    def set_log_level(self, level: int, *args, **kwargs):
        self.log_level = level

    def set_formatter(self, formatter_name: str, *args, **kwargs):
        self.formatter_name = formatter_name

    def set_config(self, config: "logging.config._DictConfigArgs", *args, **kwargs):
        self.config = config


def get_main_formatter_name() -> Literal["colored", "structured"]:
    return "colored" if os.getenv("ENV", "").upper() == "DEV" else "structured"


def get_log_level_number_from_env(log_level_env: str = "LOG_LEVEL") -> int:
    """Get the log level number from the environment variable LOG_LEVEL, which may be a string or an int.
    If LOG_LEVEL is not set, return "DEBUG" if ENV is "DEV", otherwise return "INFO".
    Supports custom log levels, e.g. "TRACE", using getLevelName"""
    log_level = os.getenv(log_level_env)
    if log_level is None:
        return logging.DEBUG if os.getenv("ENV", "").upper() == "DEV" else logging.INFO
    try:
        return int(log_level)
    except ValueError:
        # Not an int, must be a string
        val = logging.getLevelName(log_level.upper())
        if isinstance(val, int):
            return val

        return logging.DEBUG if os.getenv("ENV", "").upper() == "DEV" else logging.INFO


def configure_logging(logging_config: Optional[LoggingConfig] = None):
    if logging_config is None:
        logging_config = LoggingConfig()

    default_config: "logging.config._DictConfigArgs" = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "colored",
            }
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": True,
            },
            "gunicorn.access": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            },
            "gunicorn.error": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            },
            "gunicorn.errors": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            },
            "hypercorn.error": {
                "handlers": ["default"],
                "propagate": False,
            },
            "hypercorn.access": {"handlers": ["default"], "propagate": False},
        },
    }

    if logging_config.formatter_name == "structured":
        default_config["formatters"]["structured"] = make_formatter_structured()
    elif logging_config.formatter_name == "colored":
        default_config["formatters"]["colored"] = make_formatter_colored()
    if logging_config.config:
        config: "logging.config._DictConfigArgs" = {**default_config, **logging_config.config}  # type: ignore[misc]
    else:
        config = default_config

    config["handlers"]["default"]["formatter"] = logging_config.formatter_name
    config["handlers"]["default"]["level"] = logging_config.log_level
    config["loggers"][""]["level"] = logging_config.log_level

    logging.config.dictConfig(config)
    # FilterBoundLogger only supports basic log levels, so we need to find the closest one.
    # XXX Make sure we have a filter for the exact number
    # XXX Make a custom filterable?
    closet_smaller_log_level = _get_closest_smaller_log_level(logging_config.log_level)

    structlog.configure(
        processors=struct_pre_chain,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(closet_smaller_log_level),
        # wrapper_class=structlog._log_levels.(logging_config.log_level),
        cache_logger_on_first_use=True,
    )

    if not logging_config.ignore_duplicate_processors:
        # logging.getLogger().info("Duplicate processors are not ignored")
        check_no_duplicate_processors(logging.getLogger())

    if logging_config.excepthook:
        set_excepthook(structlog.stdlib.get_logger())
    logger = structlog.stdlib.get_logger()
    logger.info("Logging configured", config=config)


def set_formatter(formatter_name: str):
    logger = logging.getLogger()
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter(formatter_name))


def set_excepthook(logger: logging.Logger | structlog.stdlib.BoundLogger):
    def excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None):
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = excepthook


@contextmanager
def temporary_log_config(temp_config: LoggingConfig):
    original_config = LoggingConfig()
    original_config.set_config(logging.getLogger().getEffectiveLevel())
    original_config.set_formatter(logging.getLogger().handlers[0].formatter._fmt)

    configure_logging(temp_config)
    try:
        yield
    finally:
        configure_logging(original_config)


def check_no_duplicate_processors(logger: logging.Logger):
    """Check if a there are duplicates processors in each ProcessorFormatter.
    Also check in the pre_chain of the formatter.

    Beware: it only checks active formatters (i.e. formatters attached to a StreamHandler)
    """
    handlers = logger.handlers
    for handler in handlers:
        if not isinstance(handler, logging.StreamHandler):
            continue
        formatter = handler.formatter
        if not isinstance(formatter, structlog.stdlib.ProcessorFormatter):
            continue
        # print("Formatter", formatter)
        fmt_processors = formatter.processors
        pre_chain_processors = formatter.foreign_pre_chain or []
        # We can't add sequences with +
        processors: Sequence[Processor] = tuple(pre_chain_processors) + tuple(fmt_processors)
        # Not all processors have a __name__ attribute. In that case, use __class__.__name__
        processor_names = [p.__name__ if hasattr(p, "__name__") else p.__class__.__name__ for p in processors]
        duplicates = set([x for x in processor_names if processor_names.count(x) > 1])
        if not duplicates:
            continue
        print("Duplicate processors in ProcessorFormatter", duplicates, processor_names)
        logger.warning(
            "Duplicate processors in ProcessorFormatter",
            extra=dict(
                duplicates=duplicates,
                processors=processor_names,
            ),
        )


def _get_closest_smaller_log_level(log_level: int) -> int:
    """From an arbitrary log level (not only the default one), get the closest smaller or equal log level.

    Eg. if log_level is 30, it will return 30 (WARNING)
        if log_level is 5, it will return 0 (NOTSET)
        if log_level is 42, it will return 40 (ERROR)
        if log_level is 143, it will return 50 (CRITICAL)
    """
    closest_smaller_log_level = 0
    for level in [0, 10, 20, 30, 40, 50]:
        if level > log_level:
            break
        closest_smaller_log_level = level
    return closest_smaller_log_level


if __name__ == "__main__":
    # Configure the logger with default settings
    configure_logging()

    raise ValueError("This is a test")
