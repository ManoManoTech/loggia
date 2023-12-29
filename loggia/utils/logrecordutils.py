"""A manifestation of our reluctance to introducing our own type of LogRecord.

This reluctance is gradually going away as this package expands.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Generator

STANDARD_FIELDS = set(logging.makeLogRecord({}).__dict__.keys())


T = TypeVar("T")


def popattr(record: logging.LogRecord, attr: str, default: T) -> T:
    """Behaves like dict.pop() but for random attributes on any object."""
    if not hasattr(record, attr):
        return default
    result = getattr(record, attr)
    delattr(record, attr)
    return result  # type: ignore[no-any-return]


def default_attr(record: logging.LogRecord, attr: str, value: Any) -> None:
    """Sets an attribute on a log record if that attribute is not already defined."""
    if not hasattr(record, attr):
        setattr(record, attr, value)


def extra_fields(record: logging.LogRecord, to_ignore: list[str] | None = None) -> Generator[tuple[str, Any], None, None]:
    if to_ignore is None:
        to_ignore = []
    for k, v in record.__dict__.items():
        if k not in STANDARD_FIELDS and k not in to_ignore:
            yield k, v
