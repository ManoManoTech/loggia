from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize

if TYPE_CHECKING:
    import loguru

    from tests.conftest import ErrlinesCaptureFixture, JsonStderrCaptureFixture

# ruff: noqa: T201

loguru_module = pytest.importorskip("loguru")
loguru_logger: loguru.Logger = loguru_module.logger


def test_basic_info(capjson: JsonStderrCaptureFixture) -> None:
    lc = LoggerConfiguration(settings={"LOGGIA_CAPTURE_LOGURU": "OUI"})
    initialize(lc)
    loguru_logger.info("test info")
    assert len(capjson.records) == 1
    assert capjson.record
    assert capjson.record["message"] == "test info"


def test_basic_info_2(capjson: JsonStderrCaptureFixture) -> None:
    lc = LoggerConfiguration(settings={"LOGGIA_CAPTURE_LOGURU": "AUTO"})
    initialize(lc)
    loguru_logger.info("test info")
    assert len(capjson.records) == 1
    assert capjson.record
    assert capjson.record["message"] == "test info"


# XXX test that CAPTURE_LOGURU=FALSE does work


def test_extra_kv(capjson: JsonStderrCaptureFixture) -> None:
    lc = LoggerConfiguration(settings={"LOGGIA_CAPTURE_LOGURU": "OUI"})
    initialize(lc)
    loguru_logger.info("test info", coco=1, toto=False, xoxo="oui")
    assert len(capjson.records) == 1
    assert capjson.record
    assert capjson.record["message"] == "test info"
    assert capjson.record["coco"] == 1
    assert capjson.record["toto"] is False
    assert capjson.record["xoxo"] == "oui"


def test_bind(capjson: JsonStderrCaptureFixture) -> None:
    lc = LoggerConfiguration(settings={"LOGGIA_CAPTURE_LOGURU": "OUI"})
    initialize(lc)
    bound_loguru_logger = loguru_logger.bind(coco=1, toto=False, xoxo="oui")
    bound_loguru_logger.info("test info")
    assert len(capjson.records) == 1
    assert capjson.record
    assert capjson.record["message"] == "test info"
    assert capjson.record["coco"] == 1
    assert capjson.record["toto"] is False
    assert capjson.record["xoxo"] == "oui"


def test_extra_kv_pretty(caperrlines: ErrlinesCaptureFixture) -> None:
    lc = LoggerConfiguration(settings={"LOGGIA_CAPTURE_LOGURU": "OUI"}, presets="dev")
    initialize(lc)
    loguru_logger.info("test info", coco=1, toto=False, xoxo="oui")
    assert len(caperrlines.lines) == 4
    caperrlines.strip_ansi_codes()
    assert caperrlines.has_line_containing("coco=1")
    assert caperrlines.has_line_containing("toto=False")
    assert caperrlines.has_line_containing("xoxo=oui")  # XXX maybe a defect


def launch() -> None:
    logger = logging.getLogger(__name__)

    logger.log(logging.WARNING, "Warning log from standard logging, using log method")
    loguru_logger.log("WARNING", "Warning log from Loguru, using log method")
    raise RuntimeError("XXX")


def test_disallow_loguru_reconfig():
    config = LoggerConfiguration(presets=["dev"])
    assert config.disallow_loguru_reconfig
    assert config.capture_loguru
    initialize(config)

    assert hasattr(loguru_logger, "add_original")

    with pytest.raises(RuntimeError):
        loguru_logger.add(lambda x: print(x))

    from loggia._internal.loguru_stuff import _unblock_loguru_reconfiguration

    _unblock_loguru_reconfiguration()
    test = loguru_logger.add(lambda x: print(x))
    loguru_logger.remove(test)
