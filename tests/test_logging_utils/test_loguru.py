"""TODO(dugab): automated testing

This is just a manual test helper for now.


"""
from __future__ import annotations

import logging

import pytest
from loguru import logger as loguru_logger

from mm_logs.logger import configure_logging
from mm_logs.settings import MMLogsConfig

# ruff: noqa: T201


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


def test_disallow_loguru_reconfig():
    config = MMLogsConfig(debug_disallow_loguru_reconfig=True, capture_loguru=True)
    configure_logging(config)
    assert config.debug_disallow_loguru_reconfig
    assert config.capture_loguru

    assert hasattr(loguru_logger, "add_original")

    with pytest.raises(RuntimeError):
        loguru_logger.add(lambda x: print(x))

    from mm_logs.loguru_sink import _unblock_loguru_reconfiguration

    _unblock_loguru_reconfiguration()
    test = loguru_logger.add(lambda x: print(x))
    loguru_logger.remove(test)
