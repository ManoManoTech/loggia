from __future__ import annotations

import builtins
import re
from functools import cache
from importlib import import_module
from inspect import signature
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, overload

if TYPE_CHECKING:
    import sys
    from types import ModuleType

    if sys.version_info < (3, 11):
        from typing_extensions import Never
    else:
        from typing import Never

T = TypeVar("T")


@overload
def import_fqn(fully_qualified_name: str, *, ensure_instance_of: type[T], ensure_subclass_of: None = None) -> T:
    ...


@overload
def import_fqn(fully_qualified_name: str, *, ensure_subclass_of: type, ensure_instance_of: type) -> Never:
    ...


@overload
def import_fqn(fully_qualified_name: str, *, ensure_subclass_of: type[T], ensure_instance_of: None = None) -> type[T]:
    ...


@overload
def import_fqn(fully_qualified_name: str, *, ensure_instance_of: None = None, ensure_subclass_of: None = None) -> Any:
    ...


# XXX overload for ensure_callable
def import_fqn(fully_qualified_name: str, *, ensure_instance_of: type | None = None, ensure_subclass_of: type | None = None) -> Any:
    """Import Python from a fully qualified name.

    Args:
        fully_qualified_name (str): FQN of the class/thing to import
        ensure_instance_of (type | None, optional): Check whether the object
            is an instance of this type, raise if not. Defaults to None.
        ensure_subclass_of (type | None, optional): Check whether the object
            is a type, and that this types subclasses the given type.

    Raises:
        ImportError: If the FQN could not be imported, or conditions are not met.
        ValueError:

    """
    if ensure_instance_of and ensure_subclass_of:
        raise ValueError("Specify only one of ensure_instance_of and ensure_subclass_of")

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

    if ensure_instance_of is not None and not isinstance(result, ensure_instance_of):
        raise ImportError(f"Object '{fully_qualified_name}' isn't instance of {ensure_instance_of}")

    if ensure_subclass_of is not None and not issubclass(result, ensure_subclass_of):
        raise ImportError(f"Object '{fully_qualified_name}' is not a subclass of {ensure_subclass_of}.")

    return result


def class_fqn_of(o: object) -> str:
    """Return the FQN of an object's class."""
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
        except ValueError:  # noqa: PERF203
            result.append(typish_thing)
    return {result.__name__: result for result in result}


def resolve_type_string(ts: str) -> Any:
    types = builtin_types()
    if ts in types:
        return types[ts]
    return import_fqn(ts, ensure_instance_of=type)


def import_all_files(subtree: str, *, base_dir: Path | None = None) -> list[ModuleType]:
    base_dir = base_dir or (Path(__file__).parent / "../..").resolve()

    target_dir = (base_dir / subtree).resolve()

    if not target_dir.exists():
        raise RuntimeError(f"{target_dir}: file not found")

    if not target_dir.is_dir():
        raise RuntimeError(f"{target_dir}: not a directory")

    results: list[ModuleType] = []
    for p in target_dir.glob("**/*.py"):
        if p.name == "__init__.py":
            continue
        rel_path = p.relative_to(base_dir)
        fqn = rel_path.as_posix()[:-3].replace("/", ".")
        mod = import_module(fqn)
        results.append(mod)

    return results
