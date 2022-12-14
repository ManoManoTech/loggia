from collections.abc import Hashable, Mapping

from mm_utils.utils.dictutils import NestableContainer, recursive_map


class HashableDict(dict):
    """
    A suitable way to make dicts hashable.
    A sure way to hurt yourself if you use this dict as a key then mutate it.
    """

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class HashableList(list):
    """
    A suitable way to make lists hashable.
    A sure way to hurt yourself if you use this list as a key then mutate it.
    """

    def __hash__(self):
        return hash(tuple(self))


def hashable(thing):
    if isinstance(thing, Hashable):
        return thing

    if isinstance(thing, Mapping):
        return HashableDict(thing)

    if isinstance(thing, list):
        return HashableList(thing)

    raise TypeError(f"Object of type {type(thing)} '{thing}' cannot be made hashable. Consider adding an implementation.")


def deep_hashable(thing: NestableContainer):
    return recursive_map(thing, hashable)
