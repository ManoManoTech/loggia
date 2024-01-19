"""Internal loguru stuff.

We expect importing code to import-guard against loguru.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, NoReturn, cast

from loguru import logger as loguru_logger

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord
    from loguru import RecordException


# Custom sink function for Loguru to pass log messages to Structlog
def _loguru_to_std_sink(message: LoguruMessage) -> None:
    """Custom sink function to adapt Loguru Record to Structlog EventDict."""
    record: LoguruRecord = message.record

    # XXX(dugab): should we cache the getLogger? use a wrapped logger?
    logger = logging.getLogger(record["name"])

    # XXX test with loguru.log

    ct = record["time"].timestamp()
    attributes: dict[str, Any] = {
        "created": ct,
        "msecs": int((ct - int(ct)) * 1000) + 0.0,  # see gh-89047
        "name": record["name"],
        "levelname": record["level"].name,
        "levelno": record["level"].no,
        "pathname": record["file"].path,
        "filename": record["file"].name,
        "module": record["module"],
        "msg": record["message"],
        "lineno": record["line"],
        "funcName": record["function"],
        "thread": record["thread"].id,
        "threadName": record["thread"].name,
        "process": record["process"].id,
        "processName": record["process"].name,
    }

    if "msecs" in record:
        # Duration should be in ns
        # XXX(dugab): check key actualy exists somewhere?
        attributes["duration"] = record["msecs"] * 1000000  # type: ignore[typeddict-item] # pylance: disable[reportGeneralTypeIssues]

    # We want to pass stack,exc_info and exception
    if record["exception"]:
        record_exception: RecordException = record["exception"]
        if exc_value := record_exception.value:
            exc_type = type(exc_value) if not record_exception.type else record_exception.type
            exc_info: logging._ExcInfoType = (exc_type, exc_value, record_exception.traceback)
            attributes["exc_info"] = exc_info

    if "stack" in record:
        # XXX(dugab): check key actualy exists somewhere?
        attributes["stack"] = record["stack"]  # type: ignore[typeddict-item] # pylance: disable[reportGeneralTypeIssues]

    loguru_extra = cast(dict[str, Any], record.pop("extra", {}))  # type: ignore[misc]
    record_dict = loguru_extra | attributes

    log_record = logging.makeLogRecord(record_dict)
    logger.handle(log_record)


# ruff: noqa: B010
def _block_loguru_reconfiguration() -> None:
    def raise_error(*_: Any, **__: Any) -> NoReturn:
        raise RuntimeError("Loguru was reconfigured!")

    # Move the original functions to a new name
    setattr(loguru_logger, "add_original", loguru_logger.add)
    setattr(loguru_logger, "remove_original", loguru_logger.remove)
    setattr(loguru_logger, "patch_original", loguru_logger.patch)
    setattr(loguru_logger, "configure_original", loguru_logger.configure)

    # Replace the original functions with the blocking ones
    setattr(loguru_logger, "add", raise_error)
    setattr(loguru_logger, "remove", raise_error)
    setattr(loguru_logger, "patch", raise_error)
    setattr(loguru_logger, "configure", raise_error)


def _unblock_loguru_reconfiguration() -> None:
    """For testing purposes only, needed for teardown."""
    if hasattr(loguru_logger, "add_original"):
        setattr(loguru_logger, "add", loguru_logger.add_original)
    if hasattr(loguru_logger, "remove_original"):
        setattr(loguru_logger, "remove", loguru_logger.remove_original)
    if hasattr(loguru_logger, "patch_original"):
        setattr(loguru_logger, "patch", loguru_logger.patch_original)
    if hasattr(loguru_logger, "configure_original"):
        setattr(loguru_logger, "configure", loguru_logger.configure_original)
