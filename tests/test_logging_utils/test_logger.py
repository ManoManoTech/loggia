import logging
import logging.config
import os
from unittest import mock

from loggia.conf import LoggerConfiguration as LC
from loggia.logger import _patch_to_add_level, initialize


def test_configure_logging_custom():
    """Tests that the logger is correctly configured with custom settings."""
    logging_config = LC(presets="dev")
    logging_config.set_general_level("DEBUG")
    initialize(logging_config)
    logger = logging.getLogger("test")
    assert logger.isEnabledFor(logging.DEBUG)


def test_configure_logging():
    with mock.patch.object(logging.config, "dictConfig") as mock_dict_config:
        initialize()
        assert mock_dict_config.called


def test_patch_to_add_level():
    level_number = 35
    level_name = "custom_level"
    _patch_to_add_level(level_number, level_name)
    initialize()
    assert logging.getLevelName(level_number) == level_name.upper()

    logger = logging.getLogger("test")
    logger.log(level_number, "Testing")


def test_preset_precedence_with_env() -> None:
    """Tests that the preset choosen in constructor is overridden by the env var."""
    os.environ["LOGGIA_PRESETS"] = "prod"
    logging_config = LC(presets="dev")
    assert logging_config.preset_bank.preset_preferences == {"prod"}


def test_logger_level_lowercase_debug() -> None:
    """Test that lowercase level names are correctly handled."""
    os.environ["LOGGIA_LEVEL"] = "debug"
    logging_config = LC()
    initialize(logging_config)
    logger = logging.getLogger("test")
    assert logger.isEnabledFor(10)


def test_logger_level_lowercase_custom() -> None:
    """Test that lowercase level names are correctly handled."""
    os.environ["LOGGIA_LEVEL"] = "5"
    logging_config = LC()
    logging_config.set_loguru_capture(enabled=True)
    initialize(logging_config)

    logger = logging.getLogger("test")
    assert logger.isEnabledFor(5)
