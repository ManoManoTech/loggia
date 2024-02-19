from __future__ import annotations

import logging
import logging.config
from typing import TYPE_CHECKING

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize

if TYPE_CHECKING:
    from tests.conftest import JsonStderrCaptureFixture


def test_child_high_root_low(capjson: JsonStderrCaptureFixture):
    conf = LoggerConfiguration()
    conf.set_general_level("INFO")
    conf.set_logger_level("test", "warn")
    initialize(conf)

    logger = logging.getLogger("test")
    logger.warning("should go through")
    logger.info("should not go through")

    assert len(capjson.records) == 1


def test_child_high_root_low_lower(capjson: JsonStderrCaptureFixture):
    conf = LoggerConfiguration()
    conf.set_general_level("info")
    conf.set_logger_level("test", "warn")
    initialize(conf)

    logger = logging.getLogger("test")
    logger.warning("should go through")
    logger.info("should not go through")

    assert len(capjson.records) == 1


def test_child_high_root_low_int(capjson: JsonStderrCaptureFixture):
    conf = LoggerConfiguration()
    conf.set_general_level(logging.INFO)
    conf.set_logger_level("test", logging.WARNING)
    initialize(conf)

    logger = logging.getLogger("test")
    logger.warning("should go through")
    logger.info("should not go through")

    assert len(capjson.records) == 1


def test_child_low_root_high(capjson: JsonStderrCaptureFixture):
    conf = LoggerConfiguration()
    conf.set_general_level("ERROR")
    conf.set_logger_level("test", "INFO")
    initialize(conf)

    logger = logging.getLogger("test")
    logger.error("should go through")
    logger.warning("should go through")
    logger.info("should go through")

    assert len(capjson.records) == 3
