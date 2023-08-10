from collections.abc import Callable
from os import environ
from typing import TYPE_CHECKING, NamedTuple, Any

import loggia._internal.env_parsers as ep

if TYPE_CHECKING:
    from loggia.conf import LoggerConfiguration


EnvParser = Callable[[str], list[list[str]]]


class EnvConfigurable(NamedTuple):
    parser: EnvParser
    method: Callable


_ENV_PARSERS: dict[str, EnvConfigurable] = {}


FALSY_STRINGS={"N", "NO", "NEIN", "NON", "0", "FALSE", "DISABLED", "BY CHTULU, NO!"}
def is_truthy_string(s: str) -> bool:
    if s and s.upper() not in FALSY_STRINGS:
        return True
    return False


def from_env(env_var_name: str, *, parser: EnvParser = ep.default):
    """Enable a configuration classmethod to be invoked by setting an environment variable.

    This annotation mostly registers the intent, the actual parsing of environment
    variable and configuration loading is done in apply_env(...)
    """
    def decorator(fn):
        if env_var_name in _ENV_PARSERS:
            raise RuntimeError(f"Cannot use the same environment binding twice: {env_var_name}")

        # XXX check fn signature, and cast to int if requested and/or possible

        _ENV_PARSERS[env_var_name] = EnvConfigurable(parser, fn)
        def decorated_fn(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorated_fn
    return decorator


def apply_env(logger_configuration: "LoggerConfiguration", env: dict[str, str] | None = None) -> None:
    """Parse environment values into a logger configuration.

    Browse an environment dict for supported environment variables, parse the values
    of the variables, and use the parsed output as the function args on the configuration.
    """
    if env is None:
        env = environ

    for env_key, (parser, method) in _ENV_PARSERS.items():
        if env_key in env:
            value = env[env_key]
            parsed_values = parser(value)
            for pv in parsed_values:
                method(logger_configuration, *pv)
