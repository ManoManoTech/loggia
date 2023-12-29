"""Utilities for working with dictionaries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

K = TypeVar("K")

if TYPE_CHECKING:
    import logging.config
    from collections.abc import Mapping, MutableMapping


def mv_attr(obj: MutableMapping[K, Any], src_key: K, dst_key: K) -> None:
    """Move an attribute from one key to another.

    Args:
        obj (MutableMapping[K, Any]): The object to modify.
        src_key (K): The key to move from.
        dst_key (K): The key to move to.
    """
    if src_key in obj:
        obj[dst_key] = obj[src_key]
        del obj[src_key]


def del_if_possible(obj: MutableMapping[K, Any], key: K) -> None:
    """Delete a key from a dictionary, if it exists.

    Args:
        obj (MutableMapping[K, Any]): The object to modify.
        key (K): The key to delete.
    """
    try:
        del obj[key]
    except KeyError:
        pass


def del_many_if_possible(obj: MutableMapping[K, Any], keys: list[K]) -> None:
    """Delete many keys from a dictionary, if they exist.

    Args:
        obj (MutableMapping[K, Any]): The object to modify.
        keys (list[K]): The keys to delete.
    """
    for key in keys:
        del_if_possible(obj, key)


def deep_merge_log_config(
    dict_cfg: logging.config._DictConfigArgs,
    opt_dict_cfg: logging.config._DictConfigArgs | dict[str, Any],
) -> logging.config._DictConfigArgs:
    """Deep merge two logging config dictionaries. If there are conflicts, it takes the value from the second dictionary.

    Args:
        dict_cfg (logging.config._DictConfigArgs): Full logging config dictionary.
        opt_dict_cfg (logging.config._DictConfigArgs | dict[str, Any]): Partial logging config dictionary.

    Returns:
        logging.config._DictConfigArgs: The merged logging config dictionary.
    """
    for key, value in opt_dict_cfg.items():
        if key in dict_cfg and isinstance(value, dict) and isinstance(dict_cfg[key], dict):  # type: ignore[literal-required]
            dict_cfg[key] = deep_merge_log_config(dict_cfg[key], value)  # type: ignore[literal-required]
        else:
            dict_cfg[key] = value  # type: ignore[literal-required]
    return dict_cfg


def get_in(_dict: Mapping[Any, Any], keys: list[str] | tuple[str], default: Any = None) -> Any | None:
    """Get value from a dict using a path. Never raises."""
    if not keys:
        return _dict
    if len(keys) == 1:
        return _dict.get(keys[0], default)
    idx = 0
    current = _dict
    while idx < len(keys) and current != default:
        current = current.get(keys[idx], default)
        idx += 1
    return current
