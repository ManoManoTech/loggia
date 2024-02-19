from __future__ import annotations

import logging
import logging.config
import os
from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Callable, Literal, cast

import loggia._internal.env_parsers as ep
from loggia._internal.conf import EnvironmentLoader, is_falsy_string, is_truthy_string
from loggia._internal.presets import Presets
from loggia.constants import BASE_DICTCONFIG
from loggia.types import SupportsFilter, UserDefinedObject
from loggia.utils.dictutils import get_in
from loggia.utils.strutils import clean_log_level

if TYPE_CHECKING:
    from json import JSONEncoder

    from loggia.types import UserDefinedFilter


class FlexibleFlag(Enum):
    ENABLED = 1
    DISABLED = 2
    AUTO = 3

    @classmethod
    def from_any(cls, anything: str | bool | FlexibleFlag) -> FlexibleFlag:
        if isinstance(anything, FlexibleFlag):
            return anything
        if is_falsy_string(anything):
            return FlexibleFlag.DISABLED
        if is_truthy_string(anything):
            return FlexibleFlag.ENABLED
        if isinstance(anything, str) and anything.upper() == "AUTO":
            return FlexibleFlag.AUTO
        raise ValueError(f"Can't cast '{anything}' to either ENABLED, DISABLED or AUTO")


env = EnvironmentLoader()


class LoggerConfiguration:
    """Environment-aware configuration container for loggia."""

    _dictconfig: logging.config._DictConfigArgs
    setup_excepthook: bool = False
    setup_unraisablehook: bool = False
    setup_threading_excepthook: bool = False
    capture_warnings: bool = False
    capture_loguru: FlexibleFlag = FlexibleFlag.AUTO
    disallow_loguru_reconfig: bool = False

    def __init__(self, *, settings: dict[str, str] | None = None, presets: str | list[str] | None = None):
        # XXX Well put docstring!

        # Base configuration is static:
        self._dictconfig = deepcopy(BASE_DICTCONFIG)

        # Load presets according to preferences
        presets = os.getenv("LOGGIA_PRESETS", presets)
        if isinstance(presets, str):
            presets = [preset.strip() for preset in presets.split(",")]
        self.preset_bank = Presets(presets)

        # Instanciate presets (overrides defaults only and may provide new defaults
        for preset_type in self.preset_bank.available_presets:
            preset = preset_type()
            env_loader = preset_type.env_loader()
            if env_loader:
                env_loader.apply_env(preset, settings)
            preset.apply(self)

        # Constructor parameters overrides anything in defaults or presets
        if env:
            env.apply_env(self, settings)

        # Environment variables overrides defaults, presets and constructor params
        env.apply_env(self)

        # Whatever you do to LoggerConfiguration after it's initialized has the
        # last word. Enjoy.

    @env.register("LOGGIA_LEVEL")
    def set_general_level(self, level: int | str) -> None:
        """Set the general/root, or default, log level.

        Can be either a level name string or a level numder int.
        """
        assert "loggers" in self._dictconfig  # noqa: S101
        level = clean_log_level(level)
        self._dictconfig["loggers"][""]["level"] = level

    @property
    def log_level(self) -> int:
        root_level = self._dictconfig["loggers"][""]["level"]
        root_level = clean_log_level(root_level)
        if isinstance(root_level, int):
            return root_level
        if isinstance(root_level, str):
            root_level_nb = logging.getLevelName(root_level)
            if not isinstance(root_level_nb, int):
                raise RuntimeError(f"Unexpected root level name {root_level}")
            return root_level_nb
        raise RuntimeError(f"Unexpected root level type str or int, got: {type(root_level)}")

    @env.register("LOGGIA_SUB_LEVEL", parser=ep.comma_colon)
    def set_logger_level(self, logger_name: str, level: int | str) -> None:
        """Set a specific log level for a specific logger.

        This allows you to fine tune verbosity according to your needs.
        """
        assert "loggers" in self._dictconfig  # noqa: S101
        self._enforce_logger(logger_name)
        self._dictconfig["loggers"][logger_name]["level"] = clean_log_level(level)

    @env.register("LOGGIA_SUB_PROPAGATION", parser=ep.comma_colon)
    def set_logger_propagation(self, logger_name: str, does_propagate: str) -> None:
        """Set a specific logger's propagation."""
        assert "loggers" in self._dictconfig  # noqa: S101
        self._enforce_logger(logger_name)
        self._dictconfig["loggers"][logger_name]["propagate"] = is_truthy_string(does_propagate)

    def _add_filter_to_config(self, path: list[str], filter_: UserDefinedFilter) -> None:
        target_object = get_in(self._dictconfig, path, None)
        if target_object is None:
            raise KeyError(f"can't locate dictconfig path {path}")
        filter_id = self._register("filters", filter_)
        if "filters" not in target_object:
            target_object["filters"] = []
        if not isinstance(target_object["filters"], list):
            raise ValueError(f"invalid typing for filters subdict, expected 'list', got {type(target_object['filters'])}")
        target_object["filters"].append(filter_id)

    def _nice_filter_to_dictconfig_filter(self, filter_: SupportsFilter | Callable[[logging.LogRecord], bool]) -> UserDefinedFilter:
        if hasattr(filter_, "__name__"):
            typename = f"CallableWrapper<{filter_.__module__}.{filter_.__name__}:{id(filter_)}>"
        else:
            typename = f"CallableWrapper<{filter_.__class__.__module__}.{filter_.__class__.__name__}:{id(filter_)}>"

        def ctor_proto() -> SupportsFilter:
            return cast(SupportsFilter, filter_)

        def ctor_callable() -> SupportsFilter:
            t = type(typename, (), {})
            t.filter = filter_  # type:ignore[attr-defined]
            return cast(SupportsFilter, t)

        ctor = ctor_callable if callable(filter_) else ctor_proto
        ctor.__name__ = typename
        return {"()": ctor}

    # XXX deprecate this, rename to add_logger_filter(...) which is more accurate/appropriate naming
    @env.register("LOGGIA_EXTRA_FILTERS", parser=ep.comma_colon)
    def add_log_filter(self, logger_name: str, filter_: SupportsFilter | Callable[[logging.LogRecord], bool]) -> None:
        """Add a filter to a specific logger.

        Use the empty string as logger name to add a filter to the root logger.

        NB: Filters do not propagate like handlers do, see https://docs.python.org/3/library/logging.html#logging.Logger.propagate
        for more information.

        If you want the filter to propagate, set it on the handler rather than
        the logger with add_handler_filter
        """
        self._enforce_logger(logger_name)
        self._add_filter_to_config(["loggers", logger_name], self._nice_filter_to_dictconfig_filter(filter_))

    # LOGGIA_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @env.register("LOGGIA_DISABLED_FILTERS", parser=ep.comma_colon)
    def remove_log_filter(self, logger_name: str, filter_fqn: str) -> None:
        raise NotImplementedError

    def add_default_handler_filter(self, filter_: SupportsFilter | Callable[[logging.LogRecord], bool]) -> None:
        self._add_filter_to_config(["handlers", "default"], self._nice_filter_to_dictconfig_filter(filter_))

    @env.register("LOGGIA_FORMATTER")
    def set_default_formatter(self, formatter: UserDefinedObject[logging.Formatter]) -> None:
        """Sets the default formatter."""
        assert "handlers" in self._dictconfig  # noqa: S101
        formatter_id = self._register("formatters", formatter)
        self._dictconfig["handlers"]["default"]["formatter"] = formatter_id

    # E.g. LOGGIA_PALETTE in dark256 | classic16
    @env.register("LOGGIA_PRETTY_PALETTE")
    def set_pretty_formatter_palette(self, palette: str) -> None:
        raise NotImplementedError

    # E.g. LOGGIA_JSON_ENCODER set to xxx.JSONEncoder
    @env.register("LOGGIA_JSON_ENCODER")
    def set_json_encoder(self, encoder: type[JSONEncoder] | str) -> None:
        raise NotImplementedError

    @env.register("LOGGIA_CAPTURE_LOGURU")
    def set_loguru_capture(self, enabled: FlexibleFlag | bool | str) -> None:
        """Explicitely disable Loggia-Loguru interop.

        When set to AUTO, Loggia will attempt to configure Loguru if possible,
        and be silent if it's not possible.

        When set to ENABLED, Loggia will attempt to configure Loguru, and will
        produce an error if it is not importable.

        When set to DISABLED, Loggia will not attempt to configure Loguru even
        if it is present.
        """
        self.capture_loguru = FlexibleFlag.from_any(enabled)

    @env.register("LOGGIA_DISALLOW_LOGURU_RECONFIG")
    def set_loguru_reconfiguration_block(self, enabled: bool | str) -> None:
        """Explicitely allow loguru to be reconfigured.

        Loggia may hack Loguru to prevent other systems to overwrite the interop.
        This allows early detection of problems arising from conflicting configurations.
        Generally speaking, Loggia does not support or test against any Loguru customizations.
        You may have to use this setting if your software fails to initialize.
        """
        self.disallow_loguru_reconfig = is_truthy_string(enabled)

    @env.register("LOGGIA_SET_EXCEPTHOOK")
    def set_excepthook(self, enabled: bool | str) -> None:
        """Explicitely enable or disable setting [sys.excepthook][].

        When set to true, Loggia log unhandled exceptions as CRITICAL errors.
        """
        self.setup_excepthook = is_truthy_string(enabled)

    @env.register("LOGGIA_SET_UNRAISABLEHOOK")
    def set_unraisablehook(self, enabled: bool | str) -> None:
        """Explicitely enable or disable setting [sys.unraisablehook][].

        When set to true, Loggia will log unraisable exceptions as CRITICAL errors.
        Unraisable exceptions are unusual, and may happen i.e. during finalization
        or garbage collection.
        """
        self.setup_unraisablehook = is_truthy_string(enabled)

    @env.register("LOGGIA_SET_THREADING_EXCEPTHOOK")
    def set_threading_excepthook(self, enabled: bool | str) -> None:
        """Explicitely enable or disable setting [threading.excepthook][].

        When set to true, Loggia will log uncaught exception in threads as CRITICAL errors.
        """
        self.setup_threading_excepthook = is_truthy_string(enabled)

    @env.register("LOGGIA_CAPTURE_WARNINGS")
    def set_capture_warnings(self, enabled: bool | str) -> None:
        """Explicitely enable the capture of warnings.

        When set to true, Loggia will attempt to log warnings.
        """
        self.capture_warnings = is_truthy_string(enabled)

    def _enforce_logger(self, logger_name: str) -> None:
        assert "loggers" in self._dictconfig  # noqa: S101
        if logger_name not in self._dictconfig["loggers"]:
            self._dictconfig["loggers"][logger_name] = {}

    def _register(self, kind: Literal["filters", "formatters"], thing: UserDefinedObject[logging.Formatter] | UserDefinedFilter) -> str:
        assert isinstance(thing, dict)  # noqa: S101
        assert "()" in thing  # noqa: S101
        assert callable(thing["()"])  # noqa: S101
        ctor = thing["()"]
        key = ctor.__name__.replace(".", "_")
        self._dictconfig[kind] = self._dictconfig.get(kind, {})
        assert kind in self._dictconfig  # noqa: S101
        if key not in self._dictconfig[kind]:
            self._dictconfig[kind][key] = thing  # type:ignore[assignment] # our types are subsets of the more general types accepted here
        return key


__all__ = ["LoggerConfiguration"]
