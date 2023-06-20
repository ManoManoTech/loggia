"""Main module for logging configuration, using structlog."""
from __future__ import annotations

import logging
import logging.config
import sys
from typing import TYPE_CHECKING, Any, Final

import structlog

from mm_logs.settings import ActiveMMLogsConfig, MMLogsConfig, MMLogsConfigPartial
from mm_logs.structlog_utils.processors import (
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    RemoveKeysProcessor,
    datadog_error_mapping_processor,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from types import TracebackType

    from structlog.typing import Processor

DEFAULT_HANDLER: Final[str] = "default"


def patch_to_add_level(level_number: int, level_name: str) -> None:
    """Add a new level to structlog and the standard logger.

    Sanity check for existing levels is left as an exercise to the user.
    XXX(dugab): Some of these statements may be redundant.
    """
    # pylint: disable=protected-access
    # pyright: reportGeneralTypeIssues=false
    # ruff: noqa: SLF001
    level_name_upper = level_name.upper()
    level_name_lower = level_name.lower()

    logging.addLevelName(level_number, level_name_upper)

    setattr(structlog._log_levels, level_name_upper, level_number)
    structlog._log_levels._NAME_TO_LEVEL[level_name_lower] = level_number

    structlog._log_levels._LEVEL_TO_NAME = {
        v: k for k, v in structlog._log_levels._NAME_TO_LEVEL.items() if k not in ("warn", "exception", "notset")
    }

    def new_level(self, msg, *args, **kw) -> Any:  # type: ignore[no-untyped-def] # noqa: ANN
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


def make_formatter_structured(cfg: MMLogsConfig | None = None) -> dict[str, Any]:
    """Make a structlog formatter for structured logging."""
    json_indent = cfg.debug_json_indent if cfg else 0

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            datadog_error_mapping_processor,
            structlog.stdlib.add_logger_name,
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.PROCESS_NAME,
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.THREAD,
                ],
                additional_ignores=["mm_logs", "__main__", "loguru_sink", "loguru"],
            ),
            EventAttributeMapper(
                {
                    structlog.processors.CallsiteParameter.THREAD.value: "logger.thread_id",
                    structlog.processors.CallsiteParameter.THREAD_NAME.value: "logger.thread_name",
                    structlog.processors.CallsiteParameter.PATHNAME.value: "logger.path_name",
                    structlog.processors.CallsiteParameter.FUNC_NAME.value: "logger.method_name",
                    structlog.processors.CallsiteParameter.LINENO.value: "logger.lineno",
                    structlog.processors.CallsiteParameter.PROCESS.value: "logger.process_id",
                    structlog.processors.CallsiteParameter.PROCESS_NAME.value: "logger.process_name",
                    "logger": "logger.name",
                    "level": "status",
                },
            ),
            ManoManoDataDogAttributesProcessor(),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            RemoveKeysProcessor(("_loguru_record",)),
            # XXX Custom JSON Renderer (more performance?)
            structlog.processors.JSONRenderer(ensure_ascii=False, indent=json_indent, separators=(",", ":")),
        ],
        "foreign_pre_chain": std_pre_chain,
    }


def make_formatter_colored(_cfg: MMLogsConfig | None = None) -> dict[str, Any]:
    # Import here to avoid structlog.dev import in production
    from mm_logs.structlog_utils.pretty_console_renderer import PrettyConsoleRenderer

    return {
        "()": structlog.stdlib.ProcessorFormatter,
        "processors": [
            # extract_from_record_datadog,
            # ISO local time
            structlog.processors.TimeStamper(fmt="%H:%M:%S.%f%z", utc=False, key="timestamp"),
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.PROCESS_NAME,
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.THREAD,
                ],
                additional_ignores=["mm_logs", "__main__", "loguru_sink", "loguru"],
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
                ),
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


def configure_logging(custom_config: MMLogsConfig | MMLogsConfigPartial | None = None) -> MMLogsConfig:
    """Main function to configure logging.

    Args:
        custom_config (MMLogsConfig | None, optional): Your custom config. If None, a default config will be used.
    """
    logging_config = _get_logger_config(custom_config)
    ActiveMMLogsConfig.store(logging_config)

    stdb_lib_config = logging_config.stdlib_logging_dict_config

    # Assert for type checking only
    assert "handlers" in stdb_lib_config, "Missing 'handlers' key in stdlib_logging_dict_config"  # noqa: S101
    assert "loggers" in stdb_lib_config, "Missing 'loggers' key in stdlib_logging_dict_config"  # noqa: S101
    assert "formatters" in stdb_lib_config, "Missing 'formatters' key in stdlib_logging_dict_config"  # noqa: S101
    assert isinstance(stdb_lib_config["handlers"], dict)  # noqa: S101
    assert isinstance(stdb_lib_config["loggers"], dict)  # noqa: S101
    assert isinstance(stdb_lib_config["formatters"], dict)  # noqa: S101

    stdb_lib_config["handlers"][DEFAULT_HANDLER]["formatter"] = logging_config.log_formatter_name
    stdb_lib_config["handlers"][DEFAULT_HANDLER]["level"] = logging_config.log_level
    stdb_lib_config["loggers"][""]["level"] = logging_config.log_level
    if logging_config.log_formatter_name == "structured":
        stdb_lib_config["formatters"]["structured"] = make_formatter_structured(logging_config)
    elif logging_config.log_formatter_name == "colored":
        stdb_lib_config["formatters"]["colored"] = make_formatter_colored()

    logging.config.dictConfig(stdb_lib_config)

    structlog.configure(
        processors=struct_pre_chain,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging_config.log_level),
        cache_logger_on_first_use=False,
    )

    if logging_config.debug_check_duplicate_processors:
        check_duplicate_processors(logging.getLogger())

    if logging_config.set_excepthook:
        # set_excepthook(logging.getLogger())
        set_excepthook(structlog.stdlib.get_logger())

    if logging_config.capture_warnings:
        logging.captureWarnings(capture=True)

    if logging_config.debug_show_config:
        logger = structlog.stdlib.get_logger()
        logger.debug("Logging configured", config=logging_config)

    if len(logging_config._configuration_errors) > 0:
        logger = structlog.stdlib.get_logger()
        logger.error("Logging configured with errors", errors=logging_config._configuration_errors)

    return MMLogsConfig


def _get_logger_config(custom_config: MMLogsConfig | MMLogsConfigPartial | None) -> MMLogsConfig:
    """Create a config if none is provided, or merge the default config (dataclass) with the custom one (Partial typed dict) into the final config (dataclass)."""
    if custom_config is None:
        logging_config = MMLogsConfig()
    elif isinstance(custom_config, dict):
        logging_config = MMLogsConfig(**custom_config)
    elif isinstance(custom_config, MMLogsConfig):
        logging_config = custom_config

    return logging_config


def set_excepthook(logger: logging.Logger | structlog.stdlib.BoundLogger) -> None:
    """Set the excepthook to log unhandled exceptions with the given logger.

    Args:
        logger (logging.Logger | stdlib.BoundLogger): The logger to use to log unhandled exceptions
    """

    def _excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None) -> None:
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = _excepthook


def check_duplicate_processors(logger: logging.Logger) -> bool:
    """Check if a there are duplicates processors in each ProcessorFormatter.

    Also check in the pre_chain of the formatter.
    Beware: it only checks active formatters (i.e. formatters attached to a StreamHandler)
    """
    handlers = logger.handlers
    errored: bool = False
    for handler in handlers:
        if not isinstance(handler, logging.StreamHandler):
            continue
        formatter = handler.formatter
        if not isinstance(formatter, structlog.stdlib.ProcessorFormatter):
            continue

        fmt_processors = formatter.processors
        pre_chain_processors = formatter.foreign_pre_chain or []
        # We can't add sequences with +
        processors: Sequence[Processor] = tuple(pre_chain_processors) + tuple(fmt_processors)
        # Not all processors have a __name__ attribute. In that case, use __class__.__name__
        processor_names = [p.__name__ if hasattr(p, "__name__") else p.__class__.__name__ for p in processors]
        duplicates = {x for x in processor_names if processor_names.count(x) > 1}
        if not duplicates:
            continue
        errored = True
        print("Duplicate processors in ProcessorFormatter", duplicates, processor_names)  # noqa: T201
        logger.warning(
            "Duplicate processors in ProcessorFormatter",
            extra={
                "duplicates": duplicates,
                "processors": processor_names,
            },
        )
        # XXX(dugab) Should add a configuration error
    return errored
