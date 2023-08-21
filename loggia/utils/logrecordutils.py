import logging
from collections.abc import Generator
from typing import Any, TypeVar

STANDARD_FIELDS = set(logging.makeLogRecord({}).__dict__.keys())


T = TypeVar("T")


def popattr(record: logging.LogRecord, attr: str, default: T) -> T:
    """Behaves like dict.pop() but for random attributes on any object."""
    if not hasattr(record, attr):
        return default
    result = getattr(record, attr)
    delattr(record, attr)
    return result


def default_attr(record: logging.LogRecord, attr: str, value: Any) -> None:
    """Sets an attribute on a log record if that attribute is not already defined."""
    if not hasattr(record, attr):
        setattr(record, attr, value)


def extra_fields(record: logging.LogRecord) -> Generator[tuple[str, Any], None, None]:
    for k, v in record.__dict__.items():
        if k not in STANDARD_FIELDS:
            yield k, v
