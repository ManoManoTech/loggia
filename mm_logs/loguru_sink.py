"""This modules provide a custom sink function for Loguru to pass log messages to Structlog.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use Structlog for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging or structlog instead.


"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog
from loguru import logger as loguru_logger

from mm_logs.settings import ActiveMMLoggerConfig, MMLoggerConfig

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord


# Custom sink function for Loguru to pass log messages to Structlog
def loguru_to_structlog_sink(message: LoguruMessage) -> None:
    """Custom sink function to adapt Loguru Record to Structlog EventDict."""
    record: LoguruRecord = message.record

    # XXX(dugab): should we cache the getLogger? use a wrapped logger?
    structlog_logger: structlog.stdlib.BoundLogger = structlog.getLogger(record["name"])

    # XXX test with loguru.log

    attributes: dict[str, Any] = {}

    if "msecs" in record:
        # Duration should be in ns
        # XXX(dugab): check key actualy exists somewhere?
        attributes["duration"] = record["msecs"] * 1000000  # type: ignore[typeddict-item] # pylance: disable[reportGeneralTypeIssues]

    # We want to pass stack,exc_info and exception to structlog
    if "exception" in record:
        attributes["exc_info"] = record["exception"].value if record["exception"] else None

    if "stack" in record:
        # XXX(dugab): check key actualy exists somewhere?
        attributes["stack"] = record["stack"]  # type: ignore[typeddict-item] # pylance: disable[reportGeneralTypeIssues]

    # if "module" in record:
    #     attributes["module"] = record["module"]
    if "line" in record:
        attributes["lineno"] = record["line"]
    if "function" in record:
        attributes["func_name"] = record["function"]

    # XXX What about exc_info?
    structlog_logger.log(
        level=record["level"].no,
        event=record["message"],
        **record["extra"],
        **attributes,
    )


def configure_loguru(cfg: MMLoggerConfig | None = None) -> None:
    # Remove Loguru's default handler and add the custom sink function
    # XXX Patch loguru.add to raise an error if the sink is changed!
    cfg = ActiveMMLoggerConfig.get() if cfg is None else cfg
    loguru_logger.remove()
    loguru_logger.add(loguru_to_structlog_sink, level=cfg.log_level)
