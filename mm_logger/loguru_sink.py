"""This modules provide a custom sink function for Loguru to pass log messages to Structlog.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use Structlog for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging or structlog instead.


"""
from __future__ import annotations

from logging import getLogger, makeLogRecord
from typing import TYPE_CHECKING, Any, NoReturn, cast

from loguru import logger as loguru_logger

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord

    from mm_logger.conf import LoggerConfiguration


# Custom sink function for Loguru to pass log messages to Structlog
def _loguru_to_std_sink(message: LoguruMessage) -> None:
    """Custom sink function to adapt Loguru Record to Structlog EventDict."""
    record: LoguruRecord = message.record

    # XXX(dugab): should we cache the getLogger? use a wrapped logger?
    logger = getLogger(record["name"])

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
        attributes["exc_info"] = record["exception"].value

    if "stack" in record:
        # XXX(dugab): check key actualy exists somewhere?
        attributes["stack"] = record["stack"]  # type: ignore[typeddict-item] # pylance: disable[reportGeneralTypeIssues]

    # if "module" in record:
    #     attributes

    loguru_extra = cast(dict[str, Any], record.pop("extra", {}))
    record_dict = loguru_extra | attributes

    # exc_info = extra.pop("exc_info", None)
    # XXX there are more forbidden keys to extra, see logging/__init__.py:1606

    log_record = makeLogRecord(record_dict)
    logger.handle(log_record)


def configure_loguru(cfg: LoggerConfiguration) -> None:
    """Configure Loguru to use our logger.

    Remove Loguru's default handler and pass all messages to Structlog.

    Args:
        cfg (MMLogsConfig): Your configuration.
    """
    loguru_logger.remove()
    loguru_logger.add(_loguru_to_std_sink, level="INFO")  # XXX NODEPLOY get defaut log level

    if cfg.disallow_loguru_reconfig:
        _block_loguru_reconfiguration()


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
