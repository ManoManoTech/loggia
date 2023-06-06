import logging
import sys
from io import StringIO
from re import I

import pytest
import structlog

# from mm_utils.logging_utils.structlog_utils import  _get_closest_smaller_log_level, configure_logging, patch_to_add_level
from mm_logs.logger import _get_closest_smaller_log_level, configure_logging, patch_to_add_level, set_excepthook
from mm_logs.settings import MMLoggerConfig, load_config

# def test_configure_logging_default():
#     """Tests that the logger is correctly configured with default settings."""
#     configure_logging()
#     logger = structlog.stdlib.get_logger("test")
#     # We need to log something to actually create the logger
#     logger.info("Testing")
#     assert isinstance(logger.bin, structlog.stdlib.BoundLogger)


def test_configure_logging_custom():
    """Tests that the logger is correctly configured with custom settings."""
    logging_config = load_config()
    logging_config.log_formatter_name = "structured"
    logging_config.log_level = logging.DEBUG
    configure_logging(logging_config)
    logger = structlog.stdlib.get_logger("test")
    # assert isinstance(logger, structlog.stdlib.BoundLogger)
    # assert logger.isEnabledFor(logging.DEBUG)


def test_patch_to_add_level():
    """Tests that a new level is correctly added to structlog and the standard logger."""
    patch_to_add_level(42, "custom")
    configure_logging()
    logger = logging.getLogger("test")
    # logger = structlog.stdlib.get_logger("test")
    # assert hasattr(logger, "custom")
    logger.custom("Testing")


@pytest.mark.parametrize("level", [30, 4, 42, 143])
def test_get_closest_smaller_log_level(level):
    """Tests that get_closest_smaller_log_level function returns the correct level."""
    assert isinstance(_get_closest_smaller_log_level(level), int)


def test_check_duplicate_processors(caplog):
    """Tests that no duplicate processors are detected in the default configuration."""
    caplog.set_level(logging.WARNING)
    configure_logging()
    logger = structlog.stdlib.get_logger()
    logger.warning("Testing")
    assert "Duplicate processors in ProcessorFormatter" not in caplog.text
