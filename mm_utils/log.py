import enum
import logging.config
import os
import sys
import timeit
import traceback
from logging import Logger, LogRecord
from types import TracebackType
from typing import Any, ClassVar, Collection, Dict, Iterable, Union

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.typing import EventDict, Processor

from mm_utils.logging_utils.structlog_utils.pretty_console_renderer import PrettyConsoleRenderer
from mm_utils.logging_utils.structlog_utils.processors import (
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    RemoveKeysProcessor,
    datadog_add_log_level,
    datadog_add_logger_name,
    datadog_error_mapping_processor,
    extract_from_record_datadog,
)

ExcInfo = tuple[type[BaseException], BaseException, None | TracebackType]
CONSOLE = True if os.getenv("ENV", "").upper() == "DEV" else False


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


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            # "colored": {
            #     "()": structlog.stdlib.ProcessorFormatter,
            #     "processors": [
            #         # extract_from_record_datadog,
            #         structlog.processors.TimeStamper(fmt="iso", utc=False, key="timestamp"),
            #         CallsiteParameterAdder(
            #             [
            #                 CallsiteParameter.LINENO,
            #                 CallsiteParameter.THREAD_NAME,
            #                 CallsiteParameter.PROCESS,
            #                 CallsiteParameter.PATHNAME,
            #                 CallsiteParameter.FUNC_NAME,
            #                 CallsiteParameter.FILENAME,
            #             ]
            #         ),
            #         structlog.stdlib.add_logger_name,
            #         # XXX Remove process and thread name from the log message (or format it differently)
            #         structlog.stdlib.add_log_level_number,
            #         structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            #         PrettyConsoleRenderer(colors=True, event_key="message"),
            #     ],
            #     "foreign_pre_chain": std_pre_chain,
            # },
            # "structured": {
            #     "()": structlog.stdlib.ProcessorFormatter,
            #     "processors": [
            #         # extract_from_record_datadog,
            #         structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            #         datadog_error_mapping_processor,
            #         structlog.stdlib.add_logger_name,
            #         CallsiteParameterAdder(
            #             [
            #                 CallsiteParameter.PATHNAME,
            #                 CallsiteParameter.FUNC_NAME,
            #                 CallsiteParameter.LINENO,
            #                 CallsiteParameter.THREAD_NAME,
            #             ]
            #         ),
            #         EventAttributeMapper(
            #             {
            #                 CallsiteParameter.THREAD_NAME.value: "logger.thread_name",
            #                 CallsiteParameter.PATHNAME.value: "logger.path_name",
            #                 CallsiteParameter.FUNC_NAME.value: "logger.method_name",
            #                 CallsiteParameter.LINENO.value: "logger.lineno",
            #                 "logger": "logger.name",
            #                 "level": "status",
            #             }
            #         ),
            #         ManoManoDataDogAttributesProcessor(),
            #         structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            #         # XXX Custom JSON Renderer (more performance?)
            #         structlog.processors.JSONRenderer(sort_keys=True, ensure_ascii=False, indent=2),
            #     ],
            #     "foreign_pre_chain": std_pre_chain,
            # },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "colored",
                # "formatter": "structured",
                # XXX Change logger dynamically
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
            # "hypercorn.errors": {
            #     "handlers": ["default"],
            #     "level": "DEBUG",
            #     "propagate": False,
            # },
            "hypercorn.error": {
                "handlers": ["default"],
                "propagate": True,
            },
            "hypercorn.access": {"handlers": ["default"], "propagate": True},
        },
    }
)
structlog.configure(
    processors=struct_pre_chain,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.INFO if os.environ.get("ENV", "DEV") != "DEV" else logging.DEBUG
    ),  # XXX Use LOG_LEVEL env var
    # wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.stdlib.get_logger()


def excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None):
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = excepthook


logging.info("Logging initialized")
if __name__ == "__main__":
    structlog.stdlib.get_logger("test").warning("hello from structlog", foo="bar")
    logging.getLogger("test").warning("hello from logging", extra={"foo": "bar"})

    # structlog.stdlib.get_logger("test").error("error from structlog", foo="bar")
    # logging.getLogger("test").error("error from logging", extra={"foo": "bar"})
    try:
        raise ValueError("test")
    except ValueError:
        pass
    structlog.stdlib.get_logger("test").error("exception from structlog", foo="bar")
    logging.getLogger("test").error("exception from logging", extra={"foo": "bar"})
