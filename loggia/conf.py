from __future__ import annotations

import logging
import logging.config
import os
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Literal

import loggia._internal.env_parsers as ep
from loggia._internal.conf import EnvironmentLoader, is_truthy_string
from loggia._internal.presets import Presets
from loggia.constants import BASE_DICTCONFIG

if TYPE_CHECKING:
    from json import JSONEncoder


env = EnvironmentLoader()


class LoggerConfiguration:
    """Environment-aware configuration container for loggia."""

    _dictconfig: logging.config._DictConfigArgs
    setup_excepthook: bool = False
    capture_warnings: bool = False
    capture_loguru: bool = True
    disallow_loguru_reconfig: bool = True

    def __init__(self, *, settings: dict[str, str] | None = None, presets: str | list[str] | None = None):
        # XXX Well put docstring!

        # Base configuration is static:
        self._dictconfig = deepcopy(BASE_DICTCONFIG)

        # Load presets according to preferences
        presets = os.getenv("LOGGIA_PRESETS", presets)
        if isinstance(presets, str):
            presets = presets.split(",")
        self.preset_bank = Presets(presets)

        # Instanciate presets (overrides defaults only and may provide new defaults
        for preset_type in self.preset_bank.available:
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
        if isinstance(level, str):
            level = level.upper()
            if level.isdigit():
                level = int(level)
        self._dictconfig["loggers"][""]["level"] = level

    @property
    def log_level(self) -> int:
        root_level = self._dictconfig["loggers"][""]["level"]
        if isinstance(root_level, str):
            if root_level.isdigit():
                return int(root_level)
            root_level = root_level.upper()
            root_level_nb = logging.getLevelName(root_level)
            if not isinstance(root_level_nb, int):
                raise RuntimeError(f"Unexpected root level name {root_level}")
            return root_level_nb
        if isinstance(root_level, int):
            return root_level
        raise RuntimeError(f"Unexpected root level type str or int, got: {type(root_level)}")

    @env.register("LOGGIA_SUB_LEVEL", parser=ep.comma_colon)
    def set_logger_level(self, logger_name: str, level: int | str) -> None:
        """Set a specific log level for a specific logger.

        This allows you to fine tune verbosity according to your needs.
        """
        assert "loggers" in self._dictconfig  # noqa: S101
        self._enforce_logger(logger_name)
        self._dictconfig["loggers"][logger_name]["level"] = level

    @env.register("LOGGIA_SUB_PROPAGATION", parser=ep.comma_colon)
    def set_logger_propagation(self, logger_name: str, does_propagate: str) -> None:
        """Set a specific logger's propagation."""
        assert "loggers" in self._dictconfig  # noqa: S101
        self._enforce_logger(logger_name)
        self._dictconfig["loggers"][logger_name]["propagate"] = is_truthy_string(does_propagate)

    @env.register("LOGGIA_EXTRA_FILTERS", parser=ep.comma_colon)
    def add_log_filter(self, logger_name: str, filter_: str | dict[str, Any]) -> None:
        """Add a filter to a specific logger."""
        assert "loggers" in self._dictconfig  # noqa: S101
        filter_id = self._register("filters", filter_)
        self._enforce_logger(logger_name)
        logger_config = self._dictconfig["loggers"][logger_name]
        if "filters" not in logger_config:
            logger_config["filters"] = []
        assert isinstance(logger_config["filters"], list)  # noqa: S101 # XXX tuples?
        logger_config["filters"].append(filter_id)

    # LOGGIA_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @env.register("LOGGIA_DISABLED_FILTERS", parser=ep.comma_colon)
    def remove_log_filter(self, logger_name: str, filter_fqn: str) -> None:
        raise NotImplementedError

    @env.register("LOGGIA_FORMATTER")
    def set_default_formatter(self, formatter: str | dict[str, Any]) -> None:
        """Sets the default formatter."""
        assert "handlers" in self._dictconfig  # noqa: S101
        formatter_id = self._register("formatters", formatter)
        self._dictconfig["handlers"]["default"]["formatter"] = formatter_id

    # LOGGIA_PALETTE=dark256|classic16
    @env.register("LOGGIA_PRETTY_PALETTE")
    def set_pretty_formatter_palette(self, palette: str) -> None:
        raise NotImplementedError

    # LOGGIA_JSON_ENCODER=xxx
    @env.register("LOGGIA_JSON_ENCODER")
    def set_json_encoder(self, encoder: type[JSONEncoder] | str) -> None:
        raise NotImplementedError

    @env.register("LOGGIA_CAPTURE_LOGURU")
    def set_loguru_capture(self, enabled: bool | str) -> None:
        """Explicitely disable Loggia-Loguru interop.

        When set to true, Loggia will attempt to configure Loguru if it is
        installed. You do not need to explicitely disable the Loguru interop
        if Loguru is not installed.
        """
        self.capture_loguru = is_truthy_string(enabled)

    @env.register("LOGGIA_DISALLOW_LOGURU_RECONFIG")
    def set_loguru_reconfiguration_block(self, enabled: bool | str) -> None:
        """Explicitely allow loguru to be reconfigured.

        Loggia hacks Loguru to prevent other systems to overwrite its interop.
        This is to early-detect problems arising from conflicting configurations.
        You may have to use this setting if your software fails to initialize.
        """
        self.disallow_loguru_reconfig = is_truthy_string(enabled)

    @env.register("LOGGIA_SET_EXCEPTHOOK")
    def set_excepthook(self, enabled: bool | str) -> None:
        """Explicitely disable the excepthook.

        When set to true, Loggia will attempt to log unhandled exceptions.
        """
        self.setup_excepthook = is_truthy_string(enabled)

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
            self._dictconfig["loggers"][logger_name]["handlers"] = ["default"]

    def _register(self, kind: Literal["filters", "formatters"], thing: str | dict[str, Any]) -> str:
        fqn = thing if isinstance(thing, str) else thing.__class__.__module__ + "." + thing.__class__.__name__

        # XXX: changing the way we derive IDs will prevent conflicts to ever happen
        key = fqn.split(".")[-1]

        self._dictconfig[kind] = self._dictconfig.get(kind, {})  # type: ignore[typeddict-item]
        assert kind in self._dictconfig  # noqa: S101
        if key not in self._dictconfig[kind]:
            if isinstance(thing, str):
                self._dictconfig[kind][key] = {"class": fqn}
            else:
                self._dictconfig[kind][key] = thing
        else:
            registered_thing = self._dictconfig[kind][key]["class"]  # type: ignore[typeddict-item]
            if isinstance(fqn, str) and registered_thing != fqn:
                # XXX dict compare for objects
                raise RuntimeError(f"{kind} {fqn} conflicts with {registered_thing}")
        return key


__all__ = ["LoggerConfiguration"]
