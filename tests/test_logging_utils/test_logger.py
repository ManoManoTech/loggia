import logging
import logging.config
import sys
from unittest import mock

import pytest

from mm_logger.conf import LoggerConfiguration as LC
from mm_logger.logger import (
    _set_excepthook,
    initialize,
    patch_to_add_level,
)


def test_configure_logging_custom():
    """Tests that the logger is correctly configured with custom settings."""
    logging_config = LC()
    logging_config.set_default_formatter("pretty")
    logging_config.set_general_level("DEBUG")
    initialize(logging_config)
    logger = logging.getLogger("test")
    assert logger.isEnabledFor(logging.DEBUG)


def test_configure_logging():
    with mock.patch.object(logging.config, "dictConfig") as mock_dict_config:
        initialize()
        assert mock_dict_config.called


def test_set_excepthook_on():
    logger = logging.getLogger("test_logger")
    previous_hook = sys.excepthook
    _set_excepthook(logger)
    assert logger is not None
    assert sys.excepthook is not previous_hook


def test_patch_to_add_level():
    level_number = 35
    level_name = "custom_level"
    patch_to_add_level(level_number, level_name)
    initialize()
    assert logging.getLevelName(level_number) == level_name.upper()

    logger = logging.getLogger("test")
    logger.log(level_number, "Testing")


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
