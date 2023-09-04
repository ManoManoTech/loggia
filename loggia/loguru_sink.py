"""This modules provide a custom sink function for Loguru to pass log messages to standard logging.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use standard logging for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging.


"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loggia.conf import LoggerConfiguration


def configure_loguru(cfg: LoggerConfiguration) -> None:
    """Configure Loguru to use our logger.

    Remove Loguru's default handler and pass all messages to Structlog.
    Caller is responsible to check for ModuleNotFound error in case loguru
    is not available.

    Args:
        cfg (LoggerConfiguration): Your configuration.
    """
    from loguru import logger as loguru_logger

    from loggia._internal.loguru_stuff import _block_loguru_reconfiguration, _loguru_to_std_sink

    loguru_logger.remove()
    loguru_logger.add(_loguru_to_std_sink, level=cfg.log_level)  # XXX NODEPLOY get defaut log level

    if cfg.disallow_loguru_reconfig:
        _block_loguru_reconfiguration()
