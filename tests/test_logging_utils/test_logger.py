import logging
import logging.config
import sys
from unittest import mock

import pytest

from mm_logger.logger import (
    _get_logger_config,
    _set_excepthook,
    configure_logging,
    patch_to_add_level,
)
from mm_logger.settings import MMLogsConfig, MMLogsConfigPartial


def test_configure_logging_custom():
    """Tests that the logger is correctly configured with custom settings."""
    logging_config = MMLogsConfig()
    logging_config.log_formatter_name = "structured"
    logging_config.log_level = logging.DEBUG
    configure_logging(logging_config)
    # assert isinstance(logger, structlog.stdlib.BoundLogger)
    # assert logger.isEnabledFor(logging.DEBUG)


# Prepare a custom config for testing
custom_config = MMLogsConfig(log_level=logging.DEBUG, log_formatter_name="structured")


def test_configure_logging():
    with mock.patch.object(logging.config, "dictConfig") as mock_dict_config:
        configure_logging(custom_config)
        assert mock_dict_config.called


def test_set_excepthook():
    logger = logging.getLogger("test_logger")
    _set_excepthook(logger)
    assert logger is not None
    assert sys.excepthook is not None


def test_patch_to_add_level():
    level_number = 35
    level_name = "custom_level"
    patch_to_add_level(level_number, level_name)
    configure_logging()
    assert logging.getLevelName(level_number) == level_name.upper()

    logger = logging.getLogger("test")
    logger.log(level_number, "Testing")


def test_get_logger_config_custom_dict():
    custom_config = MMLogsConfigPartial(log_level="DEBUG")
    assert isinstance(_get_logger_config(custom_config), MMLogsConfig)
    assert _get_logger_config(custom_config).log_level == logging.DEBUG


def test_get_logger_config_custom_config():
    custom_config = MMLogsConfig(log_level="DEBUG")
    assert isinstance(_get_logger_config(custom_config), MMLogsConfig)
    assert _get_logger_config(custom_config).log_level == logging.DEBUG


def test_get_logger_config_default():
    assert isinstance(_get_logger_config(None), MMLogsConfig)


@pytest.fixture()
def logger():
    return logging.get_logger()


# def test_check_duplicate_processors_no_duplicates():
#     logging.shutdown()
#     reload(logging)
#     logger_config = _get_logger_config(None)
#     logger_factory = structlog.PrintLoggerFactory()
#     processor = structlog.processors.JSONRenderer()

#     # Create a structlog logger with unique processors
#     structlog.configure(
#         processors=[structlog.stdlib.filter_by_level, structlog.stdlib.add_logger_name, processor],
#         logger_factory=logger_factory,
#         wrapper_class=structlog.stdlib.BoundLogger,
#         context_class=dict,
#         cache_logger_on_first_use=True,
#     )
#     assert check_duplicate_processors(logging.getLogger()) == False
#     # Verify that the check_duplicate_processors function doesn't raise an exception

#     try:
#         check_duplicate_processors(logging.getLogger()) == False
#     except Exception as e:
#         pytest.fail(f"Unexpected Exception {e}")


# def test_check_duplicate_processors_with_duplicates():
#     logging.shutdown()
#     reload(logging)
#     logger_config = _get_logger_config(None)
#     logger_factory = structlog.PrintLoggerFactory()
#     processor = structlog.processors.JSONRenderer()

#     # Create a structlog logger with duplicate processors
#     structlog.configure(
#         processors=[structlog.stdlib.filter_by_level, structlog.stdlib.add_logger_name, processor, processor],
#         logger_factory=logger_factory,
#         wrapper_class=structlog.stdlib.BoundLogger,
#         context_class=dict,
#         cache_logger_on_first_use=True,
#     )

#     assert check_duplicate_processors(logging.getLogger()) == True
