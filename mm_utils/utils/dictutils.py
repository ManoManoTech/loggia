import asyncio
import re
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import Future
from copy import deepcopy
from typing import Any, Coroutine, Optional, TypeVar, Union

ALNUM_RE = re.compile("[^a-zA-Z0-9_]")
K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


def literal_str(v: Any):
    type_ = type(v)
    if type_ == str:
        return f'"{v}"'
    return str(v)


def get_all(dict_or_list, keys: list[str], default=None) -> Optional[Union[list[Any], Any]]:
    """
    Get possibly many values from arbitrarily nested dicts.
    Returns an empty list when values cannot be resolved.
    """
    assert isinstance(keys, list)
    if not keys:
        return dict_or_list

    def get_in_dict(thing, accu, idx):
        if len(keys) == idx + 1:
            if keys[idx] == "*":
                # If thing is a dict, we add all values()
                accu.extend(thing.values())
            else:
                # If last key is not a *, we can just extract data from a dict
                value = thing.get(keys[idx], default)
                if value is not None:
                    accu.append(value)
        else:
            if keys[idx] == "*":
                accu.extend(x for e in thing.values() for x in get_in_(e, [], idx + 1))
            else:
                get_in_(thing.get(keys[idx], {}), accu, idx + 1)
        return accu

    def get_in_list(thing, accu, idx):
        if len(keys) == idx + 1:
            if keys[idx] == "*":
                # If it's a list, we add all list elements
                accu.extend(thing)
        else:
            if keys[idx] == "*":
                # If thing is a list, we make a recursive call for all element of the list
                accu.extend(x for e in thing for x in get_in_(e, [], idx + 1))
        return accu

    def get_in_(thing, accu, idx):
        # If thing is not a dict of a list, this is a leaf. Skip it.
        # if not isinstance(thing, Iterable):
        #     return accu
        if thing is None:
            return accu
        if len(keys) <= idx:
            return accu
        if hasattr(thing, "values"):
            return get_in_dict(thing, accu, idx)
        return get_in_list(thing, accu, idx)

    result = get_in_(dict_or_list, [], 0)
    if len(result) == 0:
        return default
    return result  # if len(result) > 1 else result[0]


def make_fast_get_in(keys: list[str], default: V | None = None) -> Callable[[dict[str, V] | list[V]], V]:
    function_name = f"GENERATED_get_{'_'.join(keys)}_in"
    function_name = re.sub(ALNUM_RE, "", function_name)

    if not keys:
        raise ValueError("keys must have at least one element")

    # The simplest case has the easiest implementation
    if len(keys) == 1:
        key = keys[0]

        def fixed_getter(d: dict):
            return d.get(key, default)

        fixed_getter.__name__ = f"get_{key}"
        return fixed_getter

    # the x[k1][k2][k3] notation appears slightly faster than x.__getitem__(k1).__getitem__(k2).__getitem__(k3)
    # but it's within margin of error.
    # TODO: Revisit this in Python 3.11

    linear_get_in = "".join([f"[{literal_str(k)}]" for k in keys])
    function_statements = [
        f"def {function_name}(d: dict):",
        '    """',
        f"    GENERATED FUNCTION: gets nested values inside the passed dict 'd', at the keys {keys},",
        f"    returning {default} when it can't be found.",
        '    """',
        "    try:",
        f"        return d{linear_get_in}",
        "    except (KeyError, AttributeError, TypeError):",
        f"        return {literal_str(default)}",
        "    return d",
    ]

    function_body_string = "\n".join(function_statements)
    exec(function_body_string)  # pylint: disable=exec-used
    function_object = locals().get(function_name)
    setattr(function_object, "__radiologist_codegen__", function_body_string)
    return function_object


def has_nested_keys(dictionary: dict, *args) -> bool:
    # XXX this doesn't seem to behave properly for dicts containing None
    #     it should use `key in dict` construct
    o = dictionary
    args = list(args)
    while len(args) > 0:
        o = o.get(args.pop(0))
        if o is None:
            return False
    return True


def get_in(_dict: dict, keys: list[str], default=None):
    """Get a value from arbitrarily nested dicts."""
    assert isinstance(keys, list)
    if not keys:
        return _dict
    if len(keys) == 1:
        return _dict.get(keys[0], default)
    return get_in(_dict.get(keys[0], {}), keys[1:], default)


def set_in(_dict: dict, keys: list[str], value: Any, create=False):
    """Set a value in arbitrarily nested dict, while optionally creating nested dicts."""
    assert isinstance(keys, list)
    container = get_in(_dict, keys[:-1])
    if not isinstance(container, dict) and not hasattr(container, "__setitem__"):
        if create:
            container = dict()
            set_in(_dict, keys[:-1], container, True)
        else:
            raise KeyError(f"Cannot find a dict at '{'.'.join(keys)}' to set value in. " f"Found object of type {type(container)} instead.")
    container[keys[-1]] = value


def get_path_in(_dict: dict, dot_separated_keys: str, default=None):
    return get_in(_dict, dot_separated_keys.split("."), default)


def set_in_path(_dict: dict, dot_separated_keys: str, value: Any, create=False):
    return set_in(_dict, dot_separated_keys.split("."), value, create)


def groupby(iterable: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    """
    Groups by elements from an iterable into a dict. Takes arguments very similar
    to [itertools.groupby][].

    Unlike [itertools.groupby][], does not require prior sorting.
    Unlike [itertools.groupby][], this operates greedily and not lazily.
    """
    result: dict[K, list[T]] = {}
    for e in iterable:
        k = key(e)
        if k not in result:
            result[k] = []
        result[k].append(e)
    return result


def index_by(iterable, indexfn: Callable):
    return {indexfn(e): e for e in iterable}


def select_keys(_dict, keys: list):
    """Returns a dict containing only those entries in dict whose key is in keys"""
    output_keys = keys & _dict.keys()
    return {k: v for k, v in _dict.items() if k in output_keys}


def mv_attr(obj, src_key, dst_key):
    if src_key in obj:
        obj[dst_key] = obj[src_key]
        del obj[src_key]


def mapdict(dict_: dict, fn: Callable[[dict], dict]) -> dict:
    """
    Creates a deep copy of dict_, then call fn on it, replacing it by its result.
    The same operation is recursively carried out on any nested dict.
    Mutating the dict passed to fn will never mutate the original dict_
    """
    result = deepcopy(dict_)

    def _mapdict(dict__):
        result = fn(dict__)
        for k, v in result.items():
            if isinstance(v, dict):
                result[k] = _mapdict(v)
        return result

    return _mapdict(result)


NestableContainer = Union[Mapping, Iterable]


def recursive_map(thing: NestableContainer, fn: Callable[[NestableContainer], NestableContainer]) -> NestableContainer:
    result = deepcopy(thing)

    def _recursive_map(thing_):
        result = fn(thing_)

        if isinstance(result, Mapping):
            for k, v in result.items():
                if isinstance(v, (Mapping, Iterable)):
                    result[k] = _recursive_map(v)
        elif isinstance(result, Iterable):
            result = result.__class__(_recursive_map(e) for e in result)
        return result

    return _recursive_map(result)


# From https://gist.github.com/privatwolke/11711cc26a843784afd1aeeb16308a30 (Public domain)
async def gather_dict(tasks: dict[K, Future[V]]) -> dict[K, V]:
    """Return a dict of (key, returned_values) from a dict of (key, future)"""

    async def mark(key: K, coro: Coroutine[Any, Any, V]):
        return key, await coro

    return dict(await asyncio.gather(*(mark(key, coro) for (key, coro) in tasks.items())))
