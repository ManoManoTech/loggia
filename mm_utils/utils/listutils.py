# From https://stackoverflow.com/a/2158532
# Cristian, CC-BY-SA 3.0
from typing import Any, Callable, Generator, Iterable, TypeVar

L = TypeVar("L", list, set)
T = TypeVar("T")
Q = TypeVar("Q", object, None)


def flatten_generator(l: list) -> Generator[Any, None, None]:
    for el in l:
        if isinstance(el, (list, set)):
            yield from flatten_generator(el)
        else:
            yield el


def flatten(l: list[L]) -> list[L]:
    """
    Flattens nested lists and sets together.
    Consider using more_itertools.flatten (one level) or more_itertools.collapse (arbitrary levels) instead.
    """
    return list(flatten_generator(l))


def lget(lst: list[T], i: int, default: Q = None) -> T | Q:
    """Returns i-th item from list if present, otherwise returns default."""
    try:
        return lst[i]
    except IndexError:
        return default


def lfind(lst: Iterable, fn: Callable, default=None):
    """Returns first item in list matching predicate fn, otherwise returns default."""
    for e in lst:
        v = fn(e)
        if v is not None and v:
            return e
    return default
