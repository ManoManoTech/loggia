from collections.abc import MutableMapping
from typing import Any, TypeVar

K = TypeVar("K")


def mv_attr(obj: MutableMapping[K, Any], src_key: K, dst_key: K) -> None:
    if src_key in obj:
        obj[dst_key] = obj[src_key]
        del obj[src_key]


def del_if_possible(obj: MutableMapping[K, Any], key: K) -> None:
    try:
        del obj[key]
    except KeyError:
        pass


def del_many_if_possible(obj: MutableMapping[K, Any], keys: list[K]) -> None:
    for key in keys:
        del_if_possible(obj, key)
