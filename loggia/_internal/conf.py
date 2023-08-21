from collections.abc import Callable
from os import environ
from typing import Any, NamedTuple, TypeVar

import loggia._internal.env_parsers as ep
from loggia.constants import FALSY_STRINGS

EnvParser = Callable[[str], list[list[str]]]


class EnvConfigurable(NamedTuple):
    parser: EnvParser
    method: Callable


_ALL_ENV_KEYS: set[str] = set()
T = TypeVar("T")


def is_truthy_string(s: str) -> bool:
    if s and s.upper() not in FALSY_STRINGS:
        return True
    return False


class EnvironmentLoader:
    _parsers: dict[str, EnvConfigurable]

    def __init__(self) -> None:
        self._parsers = {}

    def register(self, env_var_name: str | None = None, *, parser: EnvParser = ep.default):
        """Enable a configuration classmethod to be invoked by setting an environment variable.

        This annotation mostly registers the intent, the actual parsing of environment
        variable and configuration loading is done in apply_env(...)
        """

        def decorator(fn: Callable) -> Callable:
            nonlocal env_var_name

            if env_var_name is None:
                env_var_name = fn.__name__.upper()

            if env_var_name in _ALL_ENV_KEYS:
                raise RuntimeError(f"Cannot use the same environment binding twice: {env_var_name}")
            # XXX check fn signature, and cast to int if requested and/or possible
            _ALL_ENV_KEYS.add(env_var_name)
            self._parsers[env_var_name] = EnvConfigurable(parser, fn)
            return fn

        return decorator

    def apply_env(self, configurable: Any, env: dict[str, str] | None = None) -> None:
        """Parse environment values into a logger configuration.

        Browse an environment dict for supported environment variables, parse the values
        of the variables, and use the parsed output as the function args on the configuration.
        """
        if env is None:
            env = environ

        for env_key, (parser, method) in self._parsers.items():
            if env_key in env:
                value = env[env_key]
                parsed_values = parser(value)
                for pv in parsed_values:
                    method(configurable, *pv)
