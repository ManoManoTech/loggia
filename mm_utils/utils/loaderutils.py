import builtins
import re
from functools import cache
from importlib import import_module
from inspect import signature


def import_fqn(fully_qualified_name: str, ensure_instance_of=None, ensure_callable: bool = False):
    """_summary_

    Args:
        fully_qualified_name (str): FQN of the class/thing to import
        ensure_instance_of (_type_, optional): TODO Documentation. Unused. Defaults to None.
        ensure_callable (bool, optional): Check whether the object is callable, raise if not. Defaults to False.

    Raises:
        ImportError: If the FQN could not be imported, or conditions are not met.
    """
    fqn_atoms = fully_qualified_name.split(".")
    module_name = ".".join(fqn_atoms[0:-1])
    name = fqn_atoms[-1]
    try:
        resource_module = import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Can't import {module_name}") from e

    if not hasattr(resource_module, name):
        raise ImportError(f"Can't find '{name}' in {resource_module}")

    result = getattr(resource_module, name)

    if ensure_instance_of is not None:
        if not isinstance(result, ensure_instance_of):
            raise ImportError(f"Object '{fully_qualified_name}' isn't instance of {ensure_instance_of}")

    if ensure_callable:
        if not callable(result):
            raise ImportError(f"Object '{fully_qualified_name}' is not callable.")

    return result


def class_fqn_of(o: object) -> str:
    """
    Return the FQN of an object's class.
    """
    if hasattr(o, "__module__"):
        return f"{o.__module__}.{o.__class__.__name__}"
    return o.__class__.__name__


@cache
def builtin_types() -> dict[str, type]:
    rex = re.compile(r"[a-z][a-z_]+")
    builtin_things = [getattr(builtins, x) for x in dir(builtins) if rex.match(str(x))]
    typish_things = [x for x in builtin_things if "class" in str(x)]
    result = []
    for typish_thing in typish_things:
        try:
            signature(typish_thing)
        except ValueError:
            result.append(typish_thing)
    return {result.__name__: result for result in result}


def resolve_type_string(ts: str):
    types = builtin_types()
    if ts in types:
        return types[ts]
    return import_fqn(ts, type)
