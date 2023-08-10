from copy import deepcopy
from json import JSONEncoder
from typing import TYPE_CHECKING

import loggia._internal.env_parsers as ep
from loggia._internal.conf import apply_env, from_env, is_truthy_string
from loggia.constants import BASE_DICTCONFIG

if TYPE_CHECKING:
    import logging.config


class LoggerConfiguration:
    """Environment-aware configuration container for loggia."""

    _dictconfig: "logging.config._DictConfigArgs"
    setup_excepthook: bool = False
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

    @from_env("LOGGIA_LEVEL")
    def set_general_level(self, level: int | str) -> None:
        """Set the general, or default, log level."""
        assert "loggers" in self._dictconfig  # noqa: S101
        self._dictconfig["loggers"][""]["level"] = level

    # LOGGIA_FORCE_LEVEL=numba:INFO,numpy:TRACE,...
    @from_env("LOGGIA_FORCE_LEVEL", parser=ep.comma_colon)
    def set_logger_level(self, logger_name: str, level: int | str) -> None:
        """Set a specific log level for a specific logger.

        This allows you to fine tune verbosity according to your needs.
        """
        assert "loggers" in self._dictconfig  # noqa: S101
        if logger_name not in self._dictconfig["loggers"]:
            self._dictconfig["loggers"][logger_name] = dict(
                handlers=["default"],
                propagate=True,
            )
        self._dictconfig["loggers"][logger_name]["level"] = level

    # LOGGIA_EXTRA_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @from_env("LOGGIA_EXTRA_FILTERS", parser=ep.comma_colon)
    def add_log_filter(self, logger_name: str, filter: str) -> None:
        raise NotImplementedError

    # LOGGIA_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @from_env("LOGGIA_DISABLED_FILTERS", parser=ep.comma_colon)
    def remove_log_filter(self, logger_name: str, filter: str) -> None:
        raise NotImplementedError

    # LOGGIA_DEV_FORMATTER=prettyformatter|simpleformatter
    @from_env("LOGGIA_FORMATTER")
    def set_default_formatter(self, formatter: str) -> None:
        """Sets the default formatter."""
        # XXX formatter registry
        # XXX formatter FQN
        # XXX throw if formatter doesn't exist
        assert "handlers" in self._dictconfig  # noqa: S101
        self._dictconfig["handlers"]["default"]["formatter"] = formatter

    # LOGGIA_PALETTE=dark256|classic16
    @from_env("LOGGIA_PRETTY_PALETTE")
    def set_pretty_formatter_palette(self, palette: str) -> None:
        raise NotImplementedError

    # LOGGIA_JSON_ENCODER=xxx
    @from_env("LOGGIA_JSON_ENCODER")
    def set_json_encoder(self, encoder: type[JSONEncoder] | str) -> None:
        raise NotImplementedError

    @from_env("LOGGIA_CAPTURE_LOGURU")
    def set_loguru_capture(self, enabled: str) -> None:
        """Explicitely disable Loggia-Loguru interop.

        When set to true, Loggia will attempt to configure Loguru if it is
        installed. You do not need to explicitely disable the Loguru interop
        if Loguru is not installed.
        """
        self.capture_loguru = is_truthy_string(enabled)

    @from_env("LOGGIA_DISALLOW_LOGURU_RECONFIG")
    def set_loguru_reconfiguration_block(self, enabled: str) -> None:
        """Explicitely allow loguru to be reconfigured.

        Loggia hacks Loguru to prevent other systems to overwrite its interop.
        This is to early-detect problems arising from conflicting configurations.
        You may have to use this setting if your software fails to initialize.
        """
        self.disallow_loguru_reconfig = is_truthy_string(enabled)

    @from_env("LOGGIA_SET_EXCEPTHOOK")
    def set_excepthook(self, enabled: str) -> None:
        """Explicitely disable the excepthook.

        When set to true, Loggia will attempt to log unhandled exceptions.
        """
        self.setup_excepthook = is_truthy_string(enabled)

    @from_env("LOGGIA_CAPTURE_WARNINGS")
    def set_capture_warnings(self, enabled: str) -> None:
        """Explicitely enable the capture of warnings.

        When set to true, Loggia will attempt to log warnings.
        """
        self.capture_warnings = is_truthy_string(enabled)


__all__ = ["LoggerConfiguration"]
