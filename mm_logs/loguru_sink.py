"""This modules provide a custom sink function for Loguru to pass log messages to Structlog.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use Structlog for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging or structlog instead.


"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn

import structlog
from loguru import logger as loguru_logger

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord

    from mm_logs.settings import MMLogsConfig


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
        _loguru_record=record,
        **record["extra"],
        **attributes,
    )


def configure_loguru(cfg: MMLogsConfig) -> None:
    """Configure Loguru to use our logger.

    Remove Loguru's default handler and pass all messages to Structlog.

    Args:
        cfg (MMLogsConfig): Your configuration.
    """
    loguru_logger.remove()
    loguru_logger.add(loguru_to_structlog_sink, level=cfg.log_level)

    if cfg.debug_disallow_loguru_reconfig:
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
