"""TODO(dugab): automated testing

This is just a manual test helper for now.


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
from mm_utils.logging_utils.structlog_utils.loguru_sink import configure_loguru

if TYPE_CHECKING:
    from loguru import Message as LoguruMessage
    from loguru import Record as LoguruRecord


def setup() -> None:
    configure_logging()
    configure_loguru()


def launch() -> None:
    logger = logging.getLogger(__name__)

    # # Test standard logging
    # # logging.debug("Debug log from standard logging")

    # # # Test logging with Loguru
    # loguru_logger.debug("Debug log from Loguru", argument1="test", argument2="test2")
    # logger.debug("Debug log from std lib", extra=dict(argument1="test", argument2="test2"))
    # # loguru_logger.info("Info log from Loguru")
    # # loguru_logger.warning("Warning log from Loguru")
    # # loguru_logger.error("Error log from Loguru")
    # # loguru_logger.critical("Critical log from Loguru", argument1="test", argument2="test2")
    # # loguru_logger.trace("Trace log from Loguru")  # XXX Is ignored rn
    # # loguru_logger.log("CRITICAL", "Critical log from Loguru, using log method")
    # # loguru_logger.success("Success log from Loguru")
    # logger.debug("Debug log from standard logging")
    # loguru_logger.debug("Debug log from Loguru")

    # #  Test when raising
    # try:
    #     1 / 0
    # except Exception as e:
    #     loguru_logger.opt(exception=e).error("Error log from Loguru")
    # try:
    #     1 / 0
    # except Exception as e:
    #     logger.exception("Error log from standard logging")

    logger.log(logging.WARNING, "Warning log from standard logging, using log method")
    loguru_logger.log("WARNING", "Warning log from Loguru, using log method")


if __name__ == "__main__":
    setup()
    launch()