from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Protocol, TypedDict, TypeVar

if TYPE_CHECKING:
    from logging import LogRecord


class SupportsFilter(Protocol):
    """Standard logging compatible filter instances implement this."""

    def filter(self, __record: LogRecord) -> bool:
        ...


T = TypeVar("T")
UserDefinedObject = TypedDict("UserDefinedObject", {"()": Callable[..., T]}, total=False)
UserDefinedFilter = TypedDict("UserDefinedFilter", {"()": Callable[[], SupportsFilter]})
