"""This modules provide a custom sink function for Loguru to pass log messages to Structlog.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use Structlog for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging or structlog instead.


"""
from __future__ import annotations

import logging
import traceback
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import structlog
from loguru import logger as loguru_logger
from loguru._recattrs import RecordException, RecordFile, RecordLevel, RecordProcess, RecordThread

from mm_utils.logging_utils.structlog_utils.log import ActiveConfig, configure_logging

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord


# Custom sink function for Loguru to pass log messages to Structlog
def loguru_to_structlog_sink(message: LoguruMessage) -> None:
    """We drop elapsed ( it's time from the start of the program, not the start of the request)

    Args:
        message (LoguruMessage): _description_
    """
    record: LoguruRecord = message.record

    # XXX(dugab): should we cache the getLogger? use a wrapped logger?
    structlog_logger: structlog.stdlib.BoundLogger = structlog.getLogger(record["name"])

    # XXX test with loguru.log

    attributes: dict[str, Any] = {}

    if "msecs" in record:
        # Duration should be in ns
        attributes["duration"] = record["msecs"] * 1000000

    # We want to pass stack,exc_info and exception to structlog
    if "exception" in record:
        attributes["exc_info"] = record["exception"].value if record["exception"] else None

    if "stack" in record:
        attributes["stack"] = record["stack"]

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


def configure_loguru() -> None:
    # Remove Loguru's default handler and add the custom sink function
    # XXX Patch loguru.add to raise an error if the sink is changed!
    cfg = ActiveConfig.get()
    loguru_logger.remove()
    loguru_logger.add(loguru_to_structlog_sink, level=cfg.log_level)
