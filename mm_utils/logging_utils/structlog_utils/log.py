"""Main module for logging configuration, using structlog."""

import logging
import logging.config
import os
import sys
from collections.abc import Iterable
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal

from structlog import configure, contextvars, make_filtering_bound_logger, stdlib
from structlog.processors import CallsiteParameter, EventRenamer, JSONRenderer, StackInfoRenderer, TimeStamper, add_log_level
from structlog.typing import Processor

from mm_utils.logging_utils.structlog_utils.processors import (
    CustomCallsiteParameterAdder,
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    add_log_level_number,
    datadog_error_mapping_processor,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def make_formatter_structured() -> dict[str, Any]:
    return {
        "()": stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            TimeStamper(fmt="iso", utc=True, key="timestamp"),
            datadog_error_mapping_processor,
            stdlib.add_logger_name,
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
                },
            ),
            ManoManoDataDogAttributesProcessor(),
            stdlib.ProcessorFormatter.remove_processors_meta,
            # XXX Custom JSON Renderer (more performance?)
            JSONRenderer(sort_keys=True, ensure_ascii=False, indent=2),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


def make_formatter_colored() -> dict[str, Any]:
    # Import here to avoid structlog.dev import in production
    from mm_utils.logging_utils.structlog_utils.pretty_console_renderer import PrettyConsoleRenderer

    return {
        "()": stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            # ISO local time
            TimeStamper(fmt="%H:%M:%S.%f%z", utc=False, key="timestamp"),
            CustomCallsiteParameterAdder(
                [
                    CallsiteParameter.LINENO,
                    # CallsiteParameter.THREAD_NAME,
                    # CallsiteParameter.PROCESS,
                    #  CallsiteParameter.PATHNAME
                ],
                additional_ignores=["mm_utils", "__main__"],
            ),
            stdlib.add_logger_name,
            # XXX Remove process and thread name from the log message (or format it differently)
            add_log_level_number,
            # XXX Make a version that supports custom log level
            stdlib.ProcessorFormatter.remove_processors_meta,
            PrettyConsoleRenderer(colors=True, event_key="message"),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


std_pre_chain: Iterable[Processor] = [
    contextvars.merge_contextvars,
    stdlib.PositionalArgumentsFormatter(),
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    stdlib.ExtraAdder(),  # XXX RESERVED ATTRIBUTES
    add_log_level,
    EventRenamer("message"),
]
"""Processors to be used for logs coming from standard logging."""


struct_pre_chain: Iterable[Processor] = [
    contextvars.merge_contextvars,
    stdlib.PositionalArgumentsFormatter(),
    StackInfoRenderer(),
    add_log_level,
    EventRenamer("message"),
    # Keep this last!
    stdlib.ProcessorFormatter.wrap_for_formatter,
]
"""Processors to be used for logs coming from structlog."""


class LoggingConfig:
    """ "
    Base class for our custom logging configuration.
    XXX More extensible, maybe dataclass or pydantic?
    """

    ignore_duplicate_processors: bool = False
    excepthook: bool = True
    config: "logging.config._DictConfigArgs" | None
    formatter_name: str
    log_level: int

    def __init__(
        self,
        log_level: int | None = None,
        formatter_name: str | None = None,
        std_logger_config: "logging.config._DictConfigArgs" | None = None,
    ) -> None:
        self.log_level: int = get_log_level_number_from_env() if log_level is None else log_level
        self.formatter_name: str = get_main_formatter_name() if formatter_name is None else formatter_name
        self.config: "logging.config._DictConfigArgs" | None = None if std_logger_config is None else std_logger_config

    def set_log_level(self, level: int, *_: Any, **__: Any) -> None:
        self.log_level = level

    def set_formatter(self, formatter_name: str, *_: Any, **__: Any) -> None:
        self.formatter_name = formatter_name

    def set_config(self, config: "logging.config._DictConfigArgs", *_: Any, **__: Any) -> None:
        self.config = config


def get_main_formatter_name() -> Literal["colored", "structured"]:
    """Get the main formatter name from the environment variable ENV."""
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


def configure_logging(logging_config: LoggingConfig | None = None, print_config_debug: bool = False) -> None:
    """Main function to configure logging.

    Args:
        logging_config (LoggingConfig | None, optional): Your custom config. If None, a default config will be used.
        print_config_debug (bool, optional): Log the config. Defaults to False.
    """
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
            },
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

    configure(
        processors=struct_pre_chain,
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=make_filtering_bound_logger(closet_smaller_log_level),
        # wrapper_class=structlog._log_levels.(logging_config.log_level),
        cache_logger_on_first_use=True,
    )

    if not logging_config.ignore_duplicate_processors:
        # logging.getLogger().info("Duplicate processors are not ignored")
        check_duplicate_processors(logging.getLogger())

    if logging_config.excepthook:
        set_excepthook(stdlib.get_logger())

    if print_config_debug:
        logger = stdlib.get_logger()
        logger.debug("Logging configured", config=config)


def set_formatter(formatter_name: str) -> None:
    logger = logging.getLogger()
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter(formatter_name))


def set_excepthook(logger: logging.Logger | stdlib.BoundLogger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = excepthook


# @contextmanager
# def temporary_log_config(temp_config: LoggingConfig):
#     original_config = LoggingConfig()
#     original_config.set_config(logging.getLogger().getEffectiveLevel())
#     original_config.set_formatter(logging.getLogger().handlers[0].formatter._fmt)

#     configure_logging(temp_config)
#     try:
#         yield
#     finally:
#         configure_logging(original_config)


def check_duplicate_processors(logger: logging.Logger) -> None:
    """Check if a there are duplicates processors in each ProcessorFormatter.
    Also check in the pre_chain of the formatter.

    Beware: it only checks active formatters (i.e. formatters attached to a StreamHandler)
    """
    handlers = logger.handlers
    for handler in handlers:
        if not isinstance(handler, logging.StreamHandler):
            continue
        formatter = handler.formatter
        if not isinstance(formatter, stdlib.ProcessorFormatter):
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
            extra={
                "duplicates": duplicates,
                "processors": processor_names,
            },
        )


def _get_closest_smaller_log_level(log_level: int) -> int:
    """From an arbitrary log level value (not only the default one), get the closest smaller or equal [default log level value](https://docs.python.org/3/library/logging.html#logging-levels).


    Examples:

    - if log_level is 30, it will return 30 (WARNING)
    - if log_level is 5, it will return 0 (NOTSET)
    - if log_level is 42, it will return 40 (ERROR)
    - if log_level is 143, it will return 50 (CRITICAL)
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
    stdlib.get_logger("test").warning("hello from structlog", foo="bar")
    logging.getLogger("test").warning("hello from logging", extra={"foo": "bar"})

    stdlib.get_logger("test").error("error from structlog", foo="bar")
    logging.getLogger("test").error("error from logging", extra={"foo": "bar"})
    try:
        raise ValueError("test")
    except ValueError:
        stdlib.get_logger("test").exception("exception from structlog", foo="bar")
        logging.getLogger("test").exception("exception from logging", extra={"foo": "bar"})

    raise ValueError("Unhandled exception")
