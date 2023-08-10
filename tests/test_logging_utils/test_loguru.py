"""TODO(dugab): automated testing

This is just a manual test helper for now.


"""
from __future__ import annotations

import json
import logging

import pytest
from loguru import logger as loguru_logger

from mm_logger.logger import initialize
from mm_logger.conf import LoggerConfiguration

# ruff: noqa: T201


def test_basic_info(capsys: pytest.CaptureFixture[str]) -> None:
    lc = LoggerConfiguration({"MM_LOGGER_CAPTURE_LOGURU": "OUI"})
    initialize(lc)
    loguru_logger.info("test info")
    captured = capsys.readouterr()
    errlines = captured.err.split("\n")
    errlines.remove("")
    assert len(errlines) == 1
    print(errlines[0])
    record = json.loads(errlines[0])
    assert record["message"] == "test info"


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
    raise RuntimeError("XXX")


def test_disallow_loguru_reconfig():
    config = LoggerConfiguration()
    initialize()
    assert config.disallow_loguru_reconfig
    assert config.capture_loguru

    assert hasattr(loguru_logger, "add_original")

    with pytest.raises(RuntimeError):
        loguru_logger.add(lambda x: print(x))

    from mm_logger.loguru_sink import _unblock_loguru_reconfiguration

    _unblock_loguru_reconfiguration()
    test = loguru_logger.add(lambda x: print(x))
    loguru_logger.remove(test)
