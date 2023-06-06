"""Main module for logging configuration, using structlog."""
from __future__ import annotations

import logging
import logging.config
import sys
from collections.abc import Iterable
from types import TracebackType
from typing import TYPE_CHECKING, Any

import structlog
from structlog.typing import Processor

from mm_logs.settings import ActiveMMLoggerConfig, MMLoggerConfig, load_config
from mm_logs.structlog_utils.processors import (
    CustomCallsiteParameterAdder,
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    RemoveKeysProcessor,
    datadog_error_mapping_processor,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def patch_to_add_level(level_number: int, level_name: str) -> None:
    """Add a new level to structlog and the standard logger.
    Sanity check for existing levels is left as an exercise to the user.
    XXX(dugab): Some of these statements may be redundant.
    """
    # pylint: disable=protected-access
    # pyright: reportGeneralTypeIssues=false
    level_name_upper = level_name.upper()
    level_name_lower = level_name.lower()

    logging.addLevelName(level_number, level_name_upper)

    setattr(structlog._log_levels, level_name_upper, level_number)
    structlog._log_levels._NAME_TO_LEVEL[level_name_lower] = level_number

    structlog._log_levels._LEVEL_TO_NAME = {
        v: k for k, v in structlog._log_levels._NAME_TO_LEVEL.items() if k not in ("warn", "exception", "notset")
    }

    def new_level(self, msg, *args, **kw) -> Any:  # type: ignore[no-untyped-def]
        return self.log(level_number, msg, *args, **kw)

    setattr(structlog.stdlib._FixedFindCallerLogger, level_name_lower, new_level)
    setattr(structlog.stdlib.BoundLogger, level_name_lower, new_level)

    setattr(
        structlog._log_levels,
        f"BoundLoggerFilteringAt{level_name_upper}",
        structlog._log_levels._make_filtering_bound_logger(getattr(structlog._log_levels, level_name_upper)),
    )

    structlog._log_levels._LEVEL_TO_FILTERING_LOGGER[getattr(structlog._log_levels, level_name_upper)] = getattr(
        structlog._log_levels,
        f"BoundLoggerFilteringAt{level_name_upper}",
    )


patch_to_add_level(5, "trace")
patch_to_add_level(25, "success")


def make_formatter_structured(cfg: MMLoggerConfig | None = None) -> dict[str, Any]:
    json_indent = cfg.log_debug_json_indent if cfg else 0

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            datadog_error_mapping_processor,
            structlog.stdlib.add_logger_name,
            CustomCallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                ],
            ),
            EventAttributeMapper(
                {
                    structlog.processors.CallsiteParameter.THREAD_NAME.value: "logger.thread_name",
                    structlog.processors.CallsiteParameter.PATHNAME.value: "logger.path_name",
                    structlog.processors.CallsiteParameter.FUNC_NAME.value: "logger.method_name",
                    structlog.processors.CallsiteParameter.LINENO.value: "logger.lineno",
                    "logger": "logger.name",
                    "level": "status",
                },
            ),
            ManoManoDataDogAttributesProcessor(),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            # XXX Custom JSON Renderer (more performance?)
            structlog.processors.JSONRenderer(sort_keys=True, ensure_ascii=False, indent=json_indent),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


def make_formatter_colored(cfg: MMLoggerConfig | None = None) -> dict[str, Any]:
    # Import here to avoid structlog.dev import in production
    from mm_logs.structlog_utils.pretty_console_renderer import PrettyConsoleRenderer

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            # ISO local time
            structlog.processors.TimeStamper(fmt="%H:%M:%S.%f%z", utc=False, key="timestamp"),
            CustomCallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.PROCESS_NAME,
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.THREAD,
                ],
                additional_ignores=["mm_utils", "__main__", "loguru_sink", "loguru"],
            ),
            EventAttributeMapper(
                {
                    structlog.processors.CallsiteParameter.THREAD.value: "logger.thread_id",
                    structlog.processors.CallsiteParameter.THREAD_NAME.value: "logger.thread_name",
                    structlog.processors.CallsiteParameter.PATHNAME.value: "logger.path_name",
                    structlog.processors.CallsiteParameter.FUNC_NAME.value: "logger.method_name",
                    # structlog.processors.CallsiteParameter.LINENO.value: "logger.lineno",
                    structlog.processors.CallsiteParameter.PROCESS.value: "logger.process_id",
                    structlog.processors.CallsiteParameter.PROCESS_NAME.value: "logger.process_name",
                    "logger": "logger.name",
                },
            ),
            structlog.stdlib.add_logger_name,
            # XXX Remove process and thread name from the log message (or format it differently)
            structlog.stdlib.add_log_level_number,
            # XXX Make a version that supports custom log level
            # Make sure we remove the meta, and some of the standard keys
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            RemoveKeysProcessor(
                (
                    "logger.method_name",
                    "logger.path_name",
                    "logger.process_id",
                    "logger.process_name",
                    "logger.thread_id",
                    "logger.thread_name",
                )
            ),
            # RemoveKeysProcessor(("pathname", "process", "thread_name", "func_nameXX", "process_name", "thread")),
            PrettyConsoleRenderer(colors=True, event_key="message"),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


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
"""Processors to be used for logs coming from standard logging."""


struct_pre_chain: Iterable[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.add_log_level,
    structlog.processors.EventRenamer("message"),
    # Keep this last!
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]
"""Processors to be used for logs coming from structlog."""


def configure_logging(logging_config: MMLoggerConfig | None = None) -> None:
    """Main function to configure logging.

    Args:
        logging_config (MMLoggerConfig | None, optional): Your custom config. If None, a default config will be used.
    """
    if logging_config is None:
        logging_config = load_config()

    ActiveMMLoggerConfig.store(logging_config)

    default_config: logging.config._DictConfigArgs = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "propagate": True,
            },
            "gunicorn.access": {
                "handlers": ["default"],
                "propagate": False,
            },
            "gunicorn.error": {
                "handlers": ["default"],
                "propagate": False,
            },
            "gunicorn.errors": {
                "handlers": ["default"],
                "propagate": False,
            },
            "hypercorn.error": {
                "handlers": ["default"],
                "propagate": False,
            },
            "hypercorn.access": {"handlers": ["default"], "propagate": False},
        },
    }

    if logging_config.log_formatter_name == "structured":
        default_config["formatters"]["structured"] = make_formatter_structured(logging_config)
    elif logging_config.log_formatter_name == "colored":
        default_config["formatters"]["colored"] = make_formatter_colored()
    if logging_config.custom_standard_logging_dict_config:
        config: logging.config._DictConfigArgs = {**default_config, **logging_config.config}  # type: ignore[misc]
    else:
        config = default_config

    config["handlers"]["default"]["formatter"] = logging_config.log_formatter_name
    config["handlers"]["default"]["level"] = logging_config.log_level
    config["loggers"][""]["level"] = logging_config.log_level

    logging.config.dictConfig(config)

    # FilterBoundLogger only supports existing log levels, so we need to find the closest one.
    closest_smaller_log_level = _get_closest_smaller_log_level(logging_config.log_level)

    structlog.configure(
        processors=struct_pre_chain,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(closest_smaller_log_level),
        cache_logger_on_first_use=False,
    )

    if logging_config.log_debug_check_duplicate_processors:
        check_duplicate_processors(logging.getLogger())

    if logging_config.set_excepthook:
        # set_excepthook(logging.getLogger())
        set_excepthook(structlog.stdlib.get_logger())

    if logging_config.capture_warnings:
        logging.captureWarnings(True)

    if logging_config.log_debug_show_config:
        logger = structlog.stdlib.get_logger()
        logger.debug("Logging configured", config=config)


def set_excepthook(logger: logging.Logger | structlog.stdlib.BoundLogger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook


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
        if not isinstance(formatter, structlog.stdlib.ProcessorFormatter):
            continue
        # print("Formatter", formatter)
        fmt_processors = formatter.processors
        pre_chain_processors = formatter.foreign_pre_chain or []
        # We can't add sequences with +
        processors: Sequence[Processor] = tuple(pre_chain_processors) + tuple(fmt_processors)
        # Not all processors have a __name__ attribute. In that case, use __class__.__name__
        processor_names = [p.__name__ if hasattr(p, "__name__") else p.__class__.__name__ for p in processors]
        duplicates = {x for x in processor_names if processor_names.count(x) > 1}
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
    - if log_level is 4, it will return 0 (NOTSET)
    - if log_level is 42, it will return 40 (ERROR)
    - if log_level is 143, it will return 50 (CRITICAL)
    """
    reversedMap = {v: k for k, v in logging.getLevelNamesMapping().items()}
    while log_level not in reversedMap:
        log_level -= 1
    return log_level


if __name__ == "__main__":
    # Configure the logger with default settings
    configure_logging()
    structlog.stdlib.get_logger("test").warning("hello from structlog", foo="bar")
    logging.getLogger("test").warning("hello from logging", extra={"foo": "bar"})

    structlog.stdlib.get_logger("test").error("error from structlog", foo="bar")
    logging.getLogger("test").error("error from logging", extra={"foo": "bar"})
    try:
        raise ValueError("test")
    except ValueError:
        structlog.stdlib.get_logger("test").exception("exception from structlog", foo="bar")
        logging.getLogger("test").exception("exception from logging", extra={"foo": "bar"})

    raise ValueError("Unhandled exception")
