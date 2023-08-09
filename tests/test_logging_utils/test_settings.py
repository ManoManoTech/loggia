import logging
import os

import pytest

from mm_logger.constants import DEFAULT_STDLIB_DICT_CONFIG
from mm_logger.settings import MMLogsConfig, _log_level_converter, _true_if_debug


# Define some test cases for the _log_level_converter function
@pytest.mark.parametrize(
    ("log_level", "expected"),
    [
        (30, 30),  # if log_level is 30 or 'WARNING', it will return 30 (WARNING)
        (4, 0),  # if log_level is 4 or 'DEBUG', it will return 0 (NOTSET)
        (42, 40),  # if log_level is 42 or 'ERROR', it will return 40 (ERROR)
        (143, 50),  # if log_level is 143 or 'CRITICAL', it will return 50 (CRITICAL)
        ("warning", 30),  # it should be case-insensitive
        ("error", 40),
        ("critical", 50),
        ("debug", 10),
    ],
)
def test_log_level_converter(log_level, expected):
    result = _log_level_converter(log_level)
    assert result == expected


def test_log_level_converter_invalid_input():
    with pytest.raises(ValueError, match="Invalid log level"):
        _log_level_converter("invalid_level")


def test_true_if_debug():
    mm_logger_config = MMLogsConfig()
    mm_logger_config.debug = True
    assert _true_if_debug(mm_logger_config) is True
    mm_logger_config.debug = False
    assert _true_if_debug(mm_logger_config) is False


@pytest.mark.parametrize(
    ("log_level", "env"),
    [
        (logging.INFO, "production"),
        (logging.DEBUG, "dev"),
    ],
)
def test_MMLogsConfig_default_values(log_level, env):
    os.environ["LOG_LEVEL"] = str(log_level)
    os.environ["ENV"] = env
    mm_logger_config = MMLogsConfig()

    assert mm_logger_config.log_level == log_level
    assert mm_logger_config.env == env.lower()
    assert mm_logger_config.set_excepthook is True
    assert mm_logger_config.capture_warnings is True
    assert mm_logger_config.debug is False
    assert mm_logger_config.debug_show_config is False
    assert mm_logger_config.debug_json_indent is None if env != "dev" else 2
    assert mm_logger_config.debug_check_duplicate_processors is False
    assert mm_logger_config.debug_disallow_loguru_reconfig is False
    assert mm_logger_config.debug_show_extra_args is False
    assert mm_logger_config.custom_stdlib_logging_dict_config is None
    assert mm_logger_config.stdlib_logging_dict_config == DEFAULT_STDLIB_DICT_CONFIG
    assert mm_logger_config.extra_log_formatters is None
    assert mm_logger_config._configuration_errors == []


def test_MMLogsConfig_set_invalid_attr():
    mm_logger_config = MMLogsConfig()

    # set inexisting attr should raise
    with pytest.raises(AttributeError):
        mm_logger_config.invalid_attr = "invalid"

    # even though we attempted to set invalid attr, it should not exist
    with pytest.raises(AttributeError):
        _ = mm_logger_config.invalid_attr


def test_MMLogsConfig_set_invalid_type():
    config = MMLogsConfig()

    # Setting invalid should fail silently, and put the default value
    json_indent = config.debug_json_indent
    config.debug_json_indent = "invalid"

    assert config.debug_json_indent == json_indent
    assert len(config._configuration_errors) == 1
    assert config._configuration_errors[0].field_name == "debug_json_indent"
