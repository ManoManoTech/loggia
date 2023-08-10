from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING

import loggia._internal.env_parsers as ep
from loggia._internal.conf import EnvironmentLoader, is_truthy_string
from loggia.base_preset import BasePreset
from loggia.constants import BASE_DICTCONFIG
from loggia.utils.loaderutils import import_all_files

if TYPE_CHECKING:
    import logging.config
    from json import JSONEncoder


env = EnvironmentLoader()


def get_default_presets() -> list[type[BasePreset]]:
    base_dir = (Path(__file__).parent / "..").resolve()
    all_preset_modules = import_all_files("loggia/presets", base_dir=base_dir)
    results: list[type[BasePreset]] = []
    for mod in all_preset_modules:
        for thing_name in dir(mod):
            thing = getattr(mod, thing_name)
            if isinstance(thing, type) and \
               issubclass(thing, BasePreset) and \
               thing is not BasePreset:
                results.append(thing)
    return results


class LoggerConfiguration:
    """Environment-aware configuration container for loggia."""

    _dictconfig: logging.config._DictConfigArgs
    setup_excepthook: bool = False
    capture_warnings: bool = False
    capture_loguru: bool = True
    disallow_loguru_reconfig: bool = True

    def __init__(self,
                 overrides: dict[str, str] | None = None,
                 presets: list[BasePreset] | None = None):
        self.reset_dictconfig()

        # load presets (overrides defaults only / provides new defaults)
        # XXX: better specify default presets
        for preset_type in get_default_presets():
            preset = preset_type()
            env_loader = preset_type.env_loader()
            if env_loader:
                env_loader.apply_env(preset, overrides)
            preset.apply(self)

        # constructor parameter overrides defaults, presets
        if overrides:
            env.apply_env(self, overrides)

        # environment variables overrides defaults, presets and constructor params
        env.apply_env(self)

        # procedural edits override everything

    def reset_dictconfig(self) -> None:
        self._dictconfig = deepcopy(BASE_DICTCONFIG)

    @env.register("LOGGIA_LEVEL")
    def set_general_level(self, level: int | str) -> None:
        """Set the general, or default, log level."""
        # XXX(dugab): does not handle lowercase `trace`
        # XXX(dugab): does not handle log int (eg. 5)
        assert "loggers" in self._dictconfig  # noqa: S101
        self._dictconfig["loggers"][""]["level"] = level

    @property
    def log_level(self) -> int | str:
        return self._dictconfig["loggers"][""]["level"]

    # LOGGIA_SUB_LEVEL=numba:INFO,numpy:TRACE,...
    @env.register("LOGGIA_SUB_LEVEL", parser=ep.comma_colon)
    def set_logger_level(self, logger_name: str, level: int | str) -> None:
        """Set a specific log level for a specific logger.

        This allows you to fine tune verbosity according to your needs.
        """
        assert "loggers" in self._dictconfig  # noqa: S101
        if logger_name not in self._dictconfig["loggers"]:
            self._dictconfig["loggers"][logger_name] = {}
            self._dictconfig["loggers"][logger_name]["handlers"] = ["default"]
        self._dictconfig["loggers"][logger_name]["level"] = level

    @env.register("LOGGIA_SUB_PROPAGATION", parser=ep.comma_colon)
    def set_logger_propagation(self, logger_name: str, does_propagate: str) -> None:
        assert "loggers" in self._dictconfig  # noqa: S101
        if logger_name not in self._dictconfig["loggers"]:
            self._dictconfig["loggers"][logger_name] = {}
            self._dictconfig["loggers"][logger_name]["handlers"] = ["default"]
        does_propagate_b = is_truthy_string(does_propagate)
        self._dictconfig["loggers"][logger_name]["propagate"] = does_propagate_b


    # LOGGIA_EXTRA_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @env.register("LOGGIA_EXTRA_FILTERS", parser=ep.comma_colon)
    def add_log_filter(self, logger_name: str, filter_fqn: str) -> None:
        assert "filters" in self._dictconfig  # noqa: S101

        # XXX: changing the way we derive IDs will prevent conflicts to ever happen
        filter_id = filter_fqn.split(".")[-1]

        if filter_id not in self._dictconfig["filters"]:
            self._dictconfig["filters"][filter_id] = {"class": filter_fqn}
        else:
            registered_filter_fqn = self._dictconfig["filters"][filter_id]["class"]
            if registered_filter_fqn != filter_fqn:
                raise RuntimeError(f"Filter {filter_fqn} conflicts with {registered_filter_fqn}")

        logger_config = self._dictconfig["loggers"][logger_name]
        if "filters" not in logger_config:
            logger_config["filters"] = []
        assert isinstance(logger_config["filters"], list)  # noqa: S101 # XXX tuples?
        logger_config["filters"].append(filter_id)

    # LOGGIA_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
    @env.register("LOGGIA_DISABLED_FILTERS", parser=ep.comma_colon)
    def remove_log_filter(self, logger_name: str, filter_fqn: str) -> None:
        raise NotImplementedError

    # LOGGIA_DEV_FORMATTER=prettyformatter|simpleformatter
    @env.register("LOGGIA_FORMATTER")
    def set_default_formatter(self, formatter: str) -> None:
        """Sets the default formatter."""
        # XXX formatter registry
        # XXX formatter FQN
        # XXX throw if formatter doesn't exist
        assert "handlers" in self._dictconfig  # noqa: S101
        self._dictconfig["handlers"]["default"]["formatter"] = formatter

    # LOGGIA_PALETTE=dark256|classic16
    @env.register("LOGGIA_PRETTY_PALETTE")
    def set_pretty_formatter_palette(self, palette: str) -> None:
        raise NotImplementedError

    # LOGGIA_JSON_ENCODER=xxx
    @env.register("LOGGIA_JSON_ENCODER")
    def set_json_encoder(self, encoder: type[JSONEncoder] | str) -> None:
        raise NotImplementedError

    @env.register("LOGGIA_CAPTURE_LOGURU")
    def set_loguru_capture(self, enabled: str) -> None:
        """Explicitely disable Loggia-Loguru interop.

        When set to true, Loggia will attempt to configure Loguru if it is
        installed. You do not need to explicitely disable the Loguru interop
        if Loguru is not installed.
        """
        self.capture_loguru = is_truthy_string(enabled)

    @env.register("LOGGIA_DISALLOW_LOGURU_RECONFIG")
    def set_loguru_reconfiguration_block(self, enabled: str) -> None:
        """Explicitely allow loguru to be reconfigured.

        Loggia hacks Loguru to prevent other systems to overwrite its interop.
        This is to early-detect problems arising from conflicting configurations.
        You may have to use this setting if your software fails to initialize.
        """
        self.disallow_loguru_reconfig = is_truthy_string(enabled)

    @env.register("LOGGIA_SET_EXCEPTHOOK")
    def set_excepthook(self, enabled: str) -> None:
        """Explicitely disable the excepthook.

        When set to true, Loggia will attempt to log unhandled exceptions.
        """
        self.setup_excepthook = is_truthy_string(enabled)

    @env.register("LOGGIA_CAPTURE_WARNINGS")
    def set_capture_warnings(self, enabled: str) -> None:
        """Explicitely enable the capture of warnings.

        When set to true, Loggia will attempt to log warnings.
        """
        self.capture_warnings = is_truthy_string(enabled)


__all__ = ["LoggerConfiguration"]
