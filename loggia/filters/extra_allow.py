from __future__ import annotations

from typing import TYPE_CHECKING

from loggia.utils.logrecordutils import extra_fields, popattr

if TYPE_CHECKING:
    from logging import LogRecord


class ExtraAllow:
    """A filter that only allows some specific fields as extra attributes on each log record passing through it."""

    def __init__(self, allow_list: list[str] | set[str]):
        self.allow_list = set(allow_list)

    def filter(self, record: LogRecord) -> bool:
        to_remove = [k for k, _ in extra_fields(record) if k not in self.allow_list]
        for k in to_remove:
            popattr(record, k, None)
        return True
