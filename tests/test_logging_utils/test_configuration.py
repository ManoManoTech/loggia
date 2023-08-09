import logging
import logging.config
import os
from copy import deepcopy
from unittest.mock import patch

import pytest

from mm_logs.constants import DEFAULT_STDLIB_DICT_CONFIG, SETTINGS_PREFIX
from mm_logs.settings import ActiveMMLogsConfig, MMLogsConfig, _convert, _log_level_converter
from mm_logs.utils.dictutils import deep_merge_log_config

# Let's first define the setup and teardown for the tests


@pytest.fixture(autouse=True)  # 'autouse' ensures the fixture is automatically used for all tests
def _env_setup_teardown():
    """Reset the environment variables before and after each test in this file."""
    original_environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture()
def _setup_and_teardown():
    os.environ["LOG_LEVEL"] = "WARNING"

    yield
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]


def test_log_level_converter():
    assert _log_level_converter("INFO") == logging.INFO
    assert _log_level_converter(logging.INFO) == logging.INFO
    with pytest.raises(ValueError, match="Invalid log level"):
        _log_level_converter("UNKNOWN")


@pytest.mark.usefixtures("_setup_and_teardown")
def test_mmloggerconfig_default_values():
    config = MMLogsConfig()
    assert config.log_level == logging.INFO
    assert config.env == "production"
    assert config.log_formatter_name == "structured"
    assert config.set_excepthook is True
    assert config.capture_warnings is True
    assert config.debug is False
    assert config.debug_show_config is False


def test_convert():
    assert _convert("100", int) == 100
    assert _convert("false", bool) is False
    with pytest.raises(ValueError, match="Cannot convert"):
        _convert("value", None)


@pytest.mark.usefixtures("_setup_and_teardown")
def test_active_mmloggerconfig_store_and_get():
    config = MMLogsConfig()
    ActiveMMLogsConfig.store(config)
    active_config = ActiveMMLogsConfig.get()
    assert active_config == config


def test_MMLogsConfig_keeps_args_over_env():
    # Using 'patch.dict' to temporarily set environment variables
    with patch.dict("os.environ", {f"{SETTINGS_PREFIX}ENV": "env", f"{SETTINGS_PREFIX}LEVEL": "50"}):
        config = MMLogsConfig(env="test", log_level=30)

    assert config.env == "test"
    assert config.log_level == 30


def test_MMLogsConfig_keeps_args_over_env_multiple():
    # Test with multiple different configs to ensure consistency
    test_cases = [
        {"env": "test", "log_level": 10},
        {"env": "prod", "log_level": 40},
        {"env": "dev", "log_level": 20},
    ]

    for test_case in test_cases:
        with patch.dict("os.environ", {f"{SETTINGS_PREFIX}ENV": "env", f"{SETTINGS_PREFIX}LOG_LEVEL": "50"}):
            config = MMLogsConfig(env=test_case["env"], log_level=test_case["log_level"])

        assert config.env == test_case["env"]
        assert config.log_level == test_case["log_level"]


def test_MMLogsConfig_uses_env_when_no_args():
    # Ensure that environment variables are still used when no arguments are passed
    os.environ[f"{SETTINGS_PREFIX}ENV"] = "env"
    os.environ[f"{SETTINGS_PREFIX}LOG_LEVEL"] = "50"
    config = MMLogsConfig()

    assert config.env == "env"
    assert config.log_level == 50


def test_MMLogsConfig_invalid_log_level_fallback():
    # Invalid 'log_level' value
    with patch.dict("os.environ", {f"{SETTINGS_PREFIX}LOG_LEVEL": "invalid_level"}):
        config = MMLogsConfig()
    # It should fallback to the default value, which is INFO (20) for 'production' env
    assert config.log_level == 20
    # And there should be a LoggerConfigurationError in _configuration_errors
    # Print in purple each error in its own line
    assert len(config._configuration_errors) == 1
    assert config._configuration_errors[0].field_name == "log_level"
    error = config._configuration_errors[0]
    assert error.field_name == "log_level"
    assert error.original_value == "invalid_level"
    assert error.set_to_value == 20
    assert isinstance(error.exc, ValueError)


def test_MMLogsConfig_env_precedence_python_config():
    # Set environment variables
    with patch.dict("os.environ", {"MM_LOGS_ENV": "mm_logger_env", "ENV": "env"}):
        # Create MMLogsConfig with 'env' configured in Python
        config = MMLogsConfig(env="python_env")
    # 'env' configured in Python should take precedence
    assert config.env == "python_env"


def test_MMLogsConfig_env_precedence_mm_logger_env():
    # Set environment variables
    with patch.dict("os.environ", {"MM_LOGS_ENV": "mm_logger_env", "ENV": "env"}):
        # Create MMLogsConfig without 'env' configured in Python
        config = MMLogsConfig()
    # 'MM_LOGS_ENV' should take precedence over 'ENV'
    assert config.env == "mm_logger_env"


def test_MMLogsConfig_env_precedence_env():
    # Set 'ENV' environment variable
    with patch.dict("os.environ", {"ENV": "env"}):
        # Create MMLogsConfig without 'env' configured in Python and 'MM_LOGS_ENV' not set
        config = MMLogsConfig()
    # 'ENV' should be used as 'env' value
    assert config.env == "env"


def test_MMLogsConfig_merge_stdlib_dict_config():
    custom_stdlib_dict_config: logging.config._DictConfigArgs = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }

    expected_merged_config = deepcopy(DEFAULT_STDLIB_DICT_CONFIG)
    expected_merged_config = deep_merge_log_config(expected_merged_config, custom_stdlib_dict_config)

    config = MMLogsConfig(custom_stdlib_logging_dict_config=custom_stdlib_dict_config)
    assert config.stdlib_logging_dict_config == expected_merged_config
    assert "console" in config.stdlib_logging_dict_config["handlers"]
    assert "default" in config.stdlib_logging_dict_config["handlers"]


def test_can_access_all_properties():
    config = MMLogsConfig()
    assert config.log_level
    assert config.env
    assert config.log_formatter_name
    assert config.custom_stdlib_logging_dict_config is None or isinstance(config.custom_stdlib_logging_dict_config, dict)
    assert config.set_excepthook
