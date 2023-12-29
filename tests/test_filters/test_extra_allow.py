from __future__ import annotations

import logging
import logging.config
from typing import TYPE_CHECKING

from loggia.conf import LoggerConfiguration
from loggia.filters.extra_allow import ExtraAllow
from loggia.logger import initialize

if TYPE_CHECKING:
    from tests.conftest import JsonStderrCaptureFixture


def test_basic_logger_filtering(capjson: JsonStderrCaptureFixture):
    logging_config = LoggerConfiguration()
    logging_config.add_log_filter("test", ExtraAllow(allow_list=["toto"]))
    initialize(logging_config)
    logger = logging.getLogger("test")
    logger.info("test", extra={"toto": "oui", "tata": "non"})
    assert "toto" in capjson.record
    assert "tata" not in capjson.record


def test_propagated_logger_filtering(capjson: JsonStderrCaptureFixture):
    logging_config = LoggerConfiguration()
    logging_config.add_default_handler_filter(ExtraAllow(allow_list=["toto"]))
    initialize(logging_config)
    logger = logging.getLogger("test")
    logger.info("test", extra={"toto": "oui", "tata": "non"})
    assert "toto" in capjson.record
    assert "tata" not in capjson.record
