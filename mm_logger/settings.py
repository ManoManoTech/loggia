from __future__ import annotations

import dataclasses
import logging
import logging.config
import os
import types
from collections.abc import Callable  # noqa: TCH003 # We want all types present, for dynamic type checking of the config
from copy import deepcopy
from typing import Any, ClassVar, Final, ForwardRef, TypedDict, Union, Unpack, get_args

from mm_logger.constants import DEFAULT_STDLIB_DICT_CONFIG, SETTINGS_PREFIX
from mm_logger.utils.dictutils import deep_merge_log_config

EnvType = str
DEV: Final[EnvType] = "dev"
PRD: Final[EnvType] = "production"

PREFIX: Final[str] = SETTINGS_PREFIX


class MMLogsConfigPartial(TypedDict, total=False):
    """Temporary type for the config dict. This is not the final type, but helps for strictly typechecking the config class."""

    env: EnvType
    log_level: int
    set_excepthook: bool
    log_formatter_name: str
    debug: bool
    debug_show_config: bool
    debug_show_extra_args: bool
    debug_json_indent: int | None
    debug_check_duplicate_processors: bool
    debug_disallow_loguru_reconfig: bool
    capture_warnings: bool
    capture_loguru: bool
    custom_stdlib_logging_dict_config: logging.config._OptionalDictConfigArgs | logging.config._DictConfigArgs | None


def _log_level_converter(log_level: str | int) -> int:
    """Convert and validate a log level to an int if it's a string or return as is if it's an int.

    Then, from an arbitrary log level value (not only the default one), get the closest smaller or equal default log level value.

    Examples:
    - if log_level is 30 or 'WARNING', it will return 30 (WARNING)
    - if log_level is 4 or 'DEBUG', it will return 0 (NOTSET)
    - if log_level is 42 or 'ERROR', it will return 40 (ERROR)
    - if log_level is 143 or 'CRITICAL', it will return 50 (CRITICAL)
    """
    if isinstance(log_level, str) and not log_level.isdigit():
        log_level = logging.getLevelName(log_level.upper())
        if not isinstance(log_level, int):
            raise ValueError(f"Invalid log level: {log_level}")
    else:
        log_level = int(log_level)
    # Get the closest smaller or equal default log level value
    all_log_level_values_sorted = sorted(set(logging.getLevelNamesMapping().values()))
    closest_smaller_log_level = min(all_log_level_values_sorted)
    for level in all_log_level_values_sorted:
        if level > log_level:
            break
        closest_smaller_log_level = level
    return closest_smaller_log_level


def _true_if_debug(self: MMLogsConfig) -> bool:
    return self.debug


@dataclasses.dataclass(init=False)
class MMLogsConfig:
    """The configuration for the logger.

    All values are optional, and will be retrieved from environment variables if possible, or set to a default value.

    """

    env: EnvType = dataclasses.field(metadata=dict(transformer=str.lower, dyn_default=lambda self: PRD, extra_env_var="ENV"))
    "The environment to use. This is used to set the default log level, and to set the default log formatter."
    log_level: int = dataclasses.field(
        metadata=dict(transformer=_log_level_converter, dyn_default=lambda self: logging.INFO if self.env != DEV else logging.DEBUG),
    )
    "The log level value to use. Use the helper to get it from a string."
    log_formatter_name: str = dataclasses.field(
        metadata=(dict(dyn_default=lambda self: "structured" if self.env != DEV else "colored")),
    )
    'Which log formatter to use. Available by default are "structured" and "colored". You can also select the name of a custom formatter, which you can add to `extra_log_formatters`.'

    set_excepthook: bool = dataclasses.field(metadata=dict(dyn_default=lambda self: True))
    "Should our logger set the `sys.excepthook`? This is useful for logging uncaught exceptions."

    # XXX sys_breakpointhook too (for non dev/disable+warn)

    capture_warnings: bool = dataclasses.field(metadata=dict(dyn_default=lambda self: True))
    "Should our logger capture warnings from the `warnings` module?"

    capture_loguru: bool = dataclasses.field(metadata=dict(dyn_default=lambda self: False))
    "XXX Document in mkdocs."

    debug: bool = dataclasses.field(metadata=dict(dyn_default=lambda self: False))
    "Turn on all MM Logger debug options. This is a shortcut to turn on all the debug options below."

    debug_show_config: bool = dataclasses.field(metadata=dict(dyn_default=_true_if_debug))
    "Log the logging configuration at the end of `configure_logging()`, as DEBUG."

    debug_json_indent: int | None = dataclasses.field(
        metadata=dict(dyn_default=lambda self: 2 if self.env == "dev" or _true_if_debug(self) else None),
    )
    "Indent JSON logs. Should only be used for debugging, as newlines won't work properly in DataDog."

    debug_check_duplicate_processors: bool = dataclasses.field(metadata=dict(dyn_default=_true_if_debug))
    "Run a sanity check of the structlog configuration to make sure no processors are duplicated, in each chain."

    debug_disallow_loguru_reconfig: bool = dataclasses.field(metadata=dict(dyn_default=_true_if_debug))
    "Raise if Loguru is reconfigured (eg. by another lib) is loguru capture was enabled with [`capture_loguru`][mm_logger.settings.MMLogsConfig.capture_loguru]."

    debug_show_extra_args: bool = dataclasses.field(metadata=dict(dyn_default=_true_if_debug))
    "Unused."

    custom_stdlib_logging_dict_config: logging.config._OptionalDictConfigArgs | None = dataclasses.field(
        default_factory=lambda: None,
    )
    "If you want to add extra standard logging configuration, you can add them here. It will be merged with the default configuration, and passed to [stdlib's `dictConfig`][logging.config.dictConfig][]."

    stdlib_logging_dict_config: logging.config._DictConfigArgs = dataclasses.field(
        default_factory=lambda: deepcopy(DEFAULT_STDLIB_DICT_CONFIG),
    )
    extra_log_formatters: dict[str, dict[str, Any] | Callable[..., dict[str, Any]]] | None = None
    "If you want to add extra log formatters, you can add them here."

    _configuration_errors: list[LoggerConfigurationError] = dataclasses.field(default_factory=list, init=False, repr=False)

    def __init__(self, **kwargs: Unpack[MMLogsConfigPartial]) -> None:
        super().__setattr__("_configuration_errors", [])
        # For each field in the dataclass
        for field in dataclasses.fields(MMLogsConfig):
            if not field.name.startswith("_"):
                self._assign_and_validate_field(field, kwargs)

        # In case of any error, catch the exception, set the default value and add the error to the list

    def __setattr__(self, name: str, value: Any) -> None:
        # Check if the attribute is a dataclass field
        field = next((f for f in dataclasses.fields(self) if f.name == name), None)
        if not field:
            raise AttributeError(f"Invalid attribute: {name}")
        # Check the type of the value
        if not self._is_value_type_correct(field, value):
            old_value = value
            # Retrieve default value in case of invalid value type
            value = self._get_field_value_from_default(field)
            self._configuration_errors.append(
                LoggerConfigurationError(
                    msg=f"Invalid type for {name}: {value} is not a {field.type} when assigning.",
                    field_name=name,
                    set_to_value=value,
                    original_value=old_value,
                ),
            )
        # Apply the transformer if exists
        transformer = field.metadata.get("transformer")
        if transformer is not None:
            try:
                value = transformer(value)
            except (ValueError, TypeError):
                # Retrieve default value in case of transformer error
                value = self._get_field_value_from_default(field)

        super().__setattr__(name, value)

    def _assign_and_validate_field(self, field: dataclasses.Field[Any], kwargs: MMLogsConfigPartial) -> None:
        if field.name in kwargs:
            self._assign_and_validate_from_kwargs(field, kwargs)
        else:
            self._assign_and_validate_from_env_or_default(field)

    def _assign_and_validate_from_kwargs(self, field: dataclasses.Field[Any], kwargs: MMLogsConfigPartial) -> None:
        value = kwargs.get(field.name)
        self._assign_and_validate_value(field, value, skip_transformer=False)

    def _assign_and_validate_from_env_or_default(self, field: dataclasses.Field[Any]) -> None:
        env_var, env_val = self._get_env_value(field)
        if env_val is not None:
            value = self._get_field_value_from_env_value(field, env_var, env_val)
        else:
            value = self._get_field_value_from_default(field)

        self._assign_and_validate_value(field, value, skip_transformer=True)

    def _assign_and_validate_value(self, field: dataclasses.Field[Any], value: Any, *, skip_transformer: bool = False) -> None:
        if field.metadata.get("transformer") and not skip_transformer:
            try:
                value = field.metadata["transformer"](value)
            except (ValueError, TypeError) as e:
                self._configuration_errors.append(
                    LoggerConfigurationError(
                        msg=f"Error while transforming value for field {field.name}: {value}",
                        field_name=field.name,
                        original_value=value,
                        exc=e,
                    ),
                )
                value = self._get_field_value_from_default(field)

        if not self._is_value_type_correct(field, value):
            old_val = value
            value = self._get_field_value_from_default(field)
            self._configuration_errors.append(
                LoggerConfigurationError(
                    msg=f"Error assigning logger config field {field.name} to {old_val}: invalid type. Default {value} will be used.",
                    field_name=field.name,
                    original_value=value,
                    set_to_value=value,
                ),
            )

        super().__setattr__(field.name, value)

    def _is_value_type_correct(self, field: dataclasses.Field[Any], value: Any) -> bool:
        field_types = self._evaluate_field_type(field.type)

        if any(isinstance(value, field_type) for field_type in field_types if not isinstance(field_type, types.GenericAlias)):
            return True
        for field_type in field_types:
            # Check if we have a generic type
            if hasattr(field_type, "__args__") and field_type.__args__ and hasattr(field_type, "__origin__"):
                # Get the base generic type and the type parameters
                base_generic_type = field_type.__origin__
                type_parameters = field_type.__args__

                if base_generic_type is list and isinstance(value, list):
                    # Check the type of elements for a list
                    if all(isinstance(elem, type_parameters[0]) for elem in value):
                        return True

                elif base_generic_type is dict and isinstance(value, dict):
                    # Check only key if parameter is Any
                    if type_parameters[1] is Any and all(isinstance(key, type_parameters[0]) for key in value):
                        return True
                    # Check the type of keys and values
                    if all(isinstance(key, type_parameters[0]) and isinstance(val, type_parameters[1]) for key, val in value.items()):
                        return True
        return False

    def _evaluate_field_type(self, field_type: Any) -> list[type]:
        if isinstance(field_type, str):
            field_type = field_type.replace("logging.config._OptionalDictConfigArgs", "dict[str, Any]")
            field_type = field_type.replace("logging.config._DictConfigArgs", "dict[str, Any]")

        if isinstance(field_type, type):
            return [field_type]
        if hasattr(field_type, "__args__") and hasattr(field_type, "__origin__"):
            # This is a parameterized generic, we will extract the origin and its parameters
            origin = field_type.__origin__
            args = field_type.__args__

            # Evaluate the origin and its parameters separately
            evaluated_origin = self._evaluate_field_type(origin)
            evaluated_args = [self._evaluate_field_type(arg)[0] for arg in args]

            # Return a list of all evaluated types
            return evaluated_origin + evaluated_args
        if hasattr(field_type, "__origin__") and field_type.__origin__ is Union or isinstance(field_type, types.UnionType):
            # This is a Union type, we will extract the individual types
            union_args = get_args(field_type)
            args_list: list[type] = list(union_args)
            return args_list

        try:
            # Try to evaluate the field type in case it's a forward reference
            evaluated_type = ForwardRef(field_type)._evaluate(globals(), locals(), frozenset())
            return self._evaluate_field_type(evaluated_type)
        except (AttributeError, NameError) as e:
            raise TypeError(f"Cannot evaluate field type: {field_type}") from e

    def _get_field_value_from_default(self, field: dataclasses.Field[Any]) -> Any:
        # If dyn_default is specified, use it to convert the value
        if field.metadata.get("dyn_default", False):
            # Call the transformer with the namedtuple and store the result
            return field.metadata["dyn_default"](self)
            # Use the default value or default factory, else keep missing type
        if field.default_factory is not dataclasses.MISSING:
            return field.default_factory()
        return field.default

    def _get_field_value_from_env_value(
        self,
        field: dataclasses.Field[Any],
        env_var: str,
        env_val: str,
    ) -> Any:
        try:
            if field.metadata.get("transformer", False):
                return field.metadata["transformer"](env_val)
            return _convert(env_val, field.type)
        except (ValueError, TypeError) as e:
            val = self._get_field_value_from_default(field)
            self._configuration_errors.append(
                LoggerConfigurationError(
                    f"Invalid value for field {field.name}: {env_val} instead of {field.type}",
                    field_name=field.name,
                    env_var=env_var,
                    original_value=env_val,
                    set_to_value=val,
                    exc=e,
                ),
            )
            return val

    def _get_env_value(self, field: dataclasses.Field[Any]) -> tuple[str, str | None]:
        """Get the value for a field from the environment.

        Automatically adds the prefix to the environment variable name and supports `extra_env_var` dataclass metadata.

        Args:
            field (dataclasses.Field[Any]): The field to get the value for.

        Returns:
            tuple[str, str | None]: The environment variable name and value.
        """
        env_var = PREFIX + field.name.upper()
        if extra_env_var := field.metadata.get("extra_env_var"):
            env_val = os.getenv(env_var, os.getenv(extra_env_var))
        else:
            env_val = os.getenv(env_var)
        return env_var, env_val


def _convert(val: str, target_type: type[Any] | str | None) -> Any:
    # If using future annotations, the type will be a string
    if isinstance(target_type, str):
        # safely evaluate the string type hint using ForwardRef
        target_type = ForwardRef(target_type)._evaluate(globals(), locals(), frozenset())

    if target_type is None:
        raise ValueError("Cannot convert to None type")
    if target_type is int:
        return int(val)
    if target_type is bool:
        return val.lower() in ["true", "1", "yes"]
    return val


class ActiveMMLogsConfig:
    """A class to store the active configuration, so that it can be accessed from anywhere."""

    _cfg: ClassVar[MMLogsConfig | None] = None

    @classmethod
    def store(cls, cfg: MMLogsConfig) -> None:
        """Store the active configuration.

        Args:
            cfg (MMLogsConfig): The configuration to store.
        """
        cls._cfg = cfg

    @classmethod
    def get(cls) -> MMLogsConfig:
        """Get the active configuration.

        Raises:
            RuntimeError: If no configuration has been stored.

        Returns:
            MMLogsConfig: The active configuration.
        """
        if cls._cfg is None:
            raise RuntimeError("No active config")
        return cls._cfg


@dataclasses.dataclass
class LoggerConfigurationError:
    """We have no logging when configuring, so we keep the errors for later, as we always fallback to a default value."""

    msg: str
    field_name: str | None = None
    env_var: str | None = None
    original_value: str | None = None
    set_to_value: Any | None = None
    exc: Exception | None = None
