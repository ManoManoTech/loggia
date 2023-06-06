from __future__ import annotations

import dataclasses
import logging
import logging.config
import os
from collections.abc import Callable
from typing import Any, Final, Literal, TypedDict

from mm_logs.constants import SETTINGS_PREFIX

EnvType = Literal["dev", "production"] | str


PREFIX: Final[str] = SETTINGS_PREFIX


class _ConfigDict(TypedDict, total=False):
    """Temporary type for the config dict. This is not the final type, but helps for strictly typechecking the config class."""

    env: EnvType
    log_level: int
    set_excepthook: bool
    log_formatter_name: str
    log_debug: bool
    log_debug_show_config: bool
    log_debug_show_extra_args: bool
    log_debug_json_indent: int | None
    log_debug_check_duplicate_processors: bool
    log_debug_raise_on_loguru_reconfiguration: bool
    capture_warnings: bool


@dataclasses.dataclass
class MMLoggerConfig:
    """The configuration for the logger. Get the default configuration with [`load_config`][mm_logs.settings.load_config].


    This is a dataclass, so you can use `dataclasses.asdict` to get a dictionary from it.

    """

    env: EnvType
    log_level: int
    "The log level value to use. Use the helper to get it from a string."

    set_excepthook: bool
    "Should our logger set the `sys.excepthook`? This is useful for logging uncaught exceptions."

    capture_warnings: bool
    "Should our logger capture warbnings from the `warnings` module?"

    log_formatter_name: str
    'Which log formatter to use. Available by default are "structured" and "colored". You can also select the name of a custom formatter, which you can add to `extra_log_formatters`.'

    log_debug: bool
    "Turn on all MM Logger debug options. This is a shortcut to turn on all the debug options below."

    log_debug_show_config: bool
    "Log the logging configuration at the end of `configure_logging()`, as DEBUG."

    log_debug_json_indent: int | None
    "Indent JSON logs. Should only be used for debugging, as newlines won't work properly in DataDog."

    log_debug_check_duplicate_processors: bool
    "Run a sanity check of the structlog configuration to make sure no processors are duplicated, in each chain."

    log_debug_raise_on_loguru_reconfiguration: bool
    "Unused."

    log_debug_show_extra_args: bool
    "Unused."

    extra_log_formatters: dict[str, dict[str, Any] | Callable[..., dict[str, Any]]] | None = None
    "If you want to add extra log formatters, you can add them here."

    custom_standard_logging_dict_config: logging.config._DictConfigArgs | None = None
    "If you want to add extra standard logging configuration, you can add them here. It will be merged with the default configuration, and passed to `logging.config.dictConfig`."

    @staticmethod
    def from_dict(config_dict: _ConfigDict) -> MMLoggerConfig:
        return MMLoggerConfig(**config_dict)


def _get_env_bool(var_name: str, default: str | bool | None) -> bool:
    value = os.getenv(PREFIX + var_name)
    if value is None:
        if isinstance(default, bool):
            return default
        elif isinstance(default, str):
            return default.lower() in ["true", "1", "yes"]
        elif default is None:
            return False
    else:
        return value.lower() in ["true", "1", "yes"]


def load_config() -> MMLoggerConfig:
    """Returns the default configuration for the logger, based on environment variables."""
    # Lowercase for ENV
    env: EnvType = os.getenv(PREFIX + "ENV", os.getenv("ENV", "production")).lower()
    log_debug: bool = bool(os.getenv(PREFIX + "LOG_DEBUG", "False").lower() in ["true", "1", "yes"])

    def get_bool_config_log_debug(var_name: str, default: str | None = None) -> bool:
        if default is None:
            default = str(log_debug).lower()
        return _get_env_bool(PREFIX + var_name, default)

    # Now use the above function to get the other configurations
    config_dict: _ConfigDict = {
        "env": env,
        "set_excepthook": get_bool_config_log_debug("SET_EXCEPTHOOK", "True"),
        "capture_warnings": get_bool_config_log_debug("CAPTURE_WARNINGS", "True"),
        "log_level": get_log_level_number_from_env(PREFIX + "LOG_LEVEL", env),
        "log_formatter_name": "colored" if env == "dev" else "structured",
        "log_debug": log_debug,
        "log_debug_show_config": get_bool_config_log_debug("LOG_DEBUG_SHOW_CONFIG"),
        "log_debug_show_extra_args": get_bool_config_log_debug("LOG_DEBUG_SHOW_EXTRA_ARGS"),
        "log_debug_json_indent": int(os.getenv(PREFIX + "LOG_DEBUG_JSON_INDENT", 2 if log_debug else 0)),
        "log_debug_raise_on_loguru_reconfiguration": get_bool_config_log_debug("LOG_DEBUG_RAISE_ON_LOGURU_RECONFIGURATION"),
        "log_debug_check_duplicate_processors": get_bool_config_log_debug("LOG_DEBUG_CHECK_DUPLICATE_PROCESSORS"),
    }

    return MMLoggerConfig.from_dict(config_dict)


if __name__ == "__main__":
    config = load_config()
    print(config)


# class MMLoggerConfig:
#     """ "
#     Base class for our custom logging configuration.
#     """

#     ignore_duplicate_processors: bool = False
#     excepthook: bool = True
#     config: "logging.config._DictConfigArgs" | None
#     formatter_name: str
#     log_level: int

#     def __init__(
#         self,
#         log_level: int | None = None,
#         formatter_name: str | None = None,
#         std_logger_config: "logging.config._DictConfigArgs" | None = None,
#     ) -> None:
#         self.log_level: int = get_log_level_number_from_env() if log_level is None else log_level
#         self.formatter_name: str = get_main_formatter_name() if formatter_name is None else formatter_name
#         self.config: "logging.config._DictConfigArgs" | None = None if std_logger_config is None else std_logger_config

#     def set_config(self, config: "logging.config._DictConfigArgs", *_: Any, **__: Any) -> None:
#         self.config = config


def get_log_level_number_from_env(log_level_env: str, env: str) -> int:
    """Get the log level number from the specified environment variable, which may be a string or an int.
    If the environment variable is not set, return "DEBUG" if ENV is "DEV", otherwise return "INFO".
    Should support custom log levels, e.g. "TRACE", using getLevelName"""
    log_level = os.getenv(log_level_env)

    def get_default_log_level() -> int:
        return logging.DEBUG if env == "dev" else logging.INFO

    if log_level is None:
        return get_default_log_level()
    try:
        return int(log_level)
    except ValueError:
        # Not an int, must be a string
        val = logging.getLevelName(log_level.upper())
        if isinstance(val, int):
            return val

        return get_default_log_level()


class ActiveMMLoggerConfig:
    """A class to store the active configuration, so that it can be accessed from anywhere."""

    _cfg: MMLoggerConfig | None = None

    @classmethod
    def store(cls, cfg: MMLoggerConfig) -> None:
        cls._cfg = cfg

    @classmethod
    def get(cls) -> MMLoggerConfig:
        if cls._cfg is None:
            raise RuntimeError("No active config")
        return cls._cfg
