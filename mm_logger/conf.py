from copy import deepcopy
from json import JSONEncoder
from typing import TYPE_CHECKING

from mm_logger.constants import BASE_DICTCONFIG
import mm_logger._internal.env_parsers as ep
from mm_logger._internal.conf import from_env, apply_env, is_truthy_string

if TYPE_CHECKING:
    import logging.config


class LoggerConfiguration:
    """Environment-aware configuration container for loggia."""
    _dictconfig: "logging.config._DictConfigArgs"
    set_excepthook: bool = False
    capture_warnings: bool = False
    capture_loguru: bool = True
    disallow_loguru_reconfig: bool = True

    def __init__(self, overrides: dict[str, str] | None = None):
        self.reset_dictconfig()
        apply_env(self)

        if overrides:
            apply_env(self, overrides)

    def reset_dictconfig(self) -> None:
        self._dictconfig = deepcopy(BASE_DICTCONFIG)

    @from_env("MM_LOGGER_LEVEL")
    def set_general_level(self, level: int|str) -> None:
        assert "loggers" in self._dictconfig  # noqa: S101
        self._dictconfig["loggers"][""]["level"] = level

    # MM_LOGGER_FORCE_LEVEL=numba:INFO,numpy:TRACE,...
    @from_env("MM_LOGGER_FORCE_LEVEL", parser=ep.comma_colon)
    def set_logger_level(self, logger_name: str, level: int|str) -> None:
        assert "loggers" in self._dictconfig  # noqa: S101
        if logger_name not in self._dictconfig["loggers"]:
            self._dictconfig["loggers"][logger_name] = dict(
                handlers=["default"],
                propagate=True,
            )
        self._dictconfig["loggers"][logger_name]["level"] = level

    # MM_LOGGER_EXTRA_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @from_env("MM_LOGGER_EXTRA_FILTERS", parser=ep.comma_colon)
    def add_log_filter(self, logger_name: str, filter: str) -> None:
        raise NotImplementedError()

    # MM_LOGGER_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @from_env("MM_LOGGER_DISABLED_FILTERS", parser=ep.comma_colon)
    def remove_log_filter(self, logger_name: str, filter: str) -> None:
        raise NotImplementedError()

    # MM_LOGGER_DEV_FORMATTER=prettyformatter|simpleformatter
    @from_env("MM_LOGGER_FORMATTER")
    def set_default_formatter(self, formatter: str) -> None:
        assert "handlers" in self._dictconfig  # noqa: S101
        self._dictconfig["handlers"]["default"]["formatter"] = formatter

    # MM_LOGGER_PALETTE=dark256|classic16
    @from_env("MM_LOGGER_PRETTY_PALETTE")
    def set_pretty_formatter_palette(self, palette: str) -> None:
        raise NotImplementedError()

    # MM_LOGGER_JSON_ENCODER=xxx
    @from_env("MM_LOGGER_JSON_ENCODER")
    def set_json_encoder(self, encoder: type[JSONEncoder]|str) -> None:
        raise NotImplementedError()

    @from_env("MM_LOGGER_CAPTURE_LOGURU")
    def set_loguru_capture(self, enabled: str) -> None:
        self.capture_loguru = is_truthy_string(enabled)

    @from_env("MM_LOGGER_DISALLOW_LOGURU_RECONFIG")
    def set_loguru_reconfiguration_block(self, enabled: str) -> None:
        self.disallow_loguru_reconfig = is_truthy_string(enabled)


__all__ = ["LoggerConfiguration"]
