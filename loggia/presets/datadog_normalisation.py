"""Remap anything to Datadog standard and common attributes."""
from __future__ import annotations

import os
import sys
import traceback
from typing import TYPE_CHECKING, Any, Final

from loggia._internal.bootstrap_logger import bootstrap_logger
from loggia._internal.conf import is_truthy_string
from loggia.base_preset import BasePreset

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    pass

if TYPE_CHECKING:
    import logging
    from types import TracebackType

    from typing_extensions import TypeAlias

    from loggia.conf import LoggerConfiguration

ExcInfo: TypeAlias = "tuple[type[BaseException], BaseException, None | TracebackType]"

# XXX(GabDug): cleanup ddtrace import
DD_TRACE_ENABLED: Final[bool | None] = is_truthy_string(os.environ.get("DD_TRACE_ENABLED", False))
if DD_TRACE_ENABLED:
    try:
        import ddtrace
    except ImportError:
        bootstrap_logger.error("DD_TRACE_ENABLED environment variable is set but ddtrace package cannot be loaded")
        ddtrace = None  # type: ignore[assignment]

try:
    from loggia._version import __version__
except ImportError:
    __version__ = "unknown"

loggia_version_str = f"loggia/{__version__}"


def _figure_out_exc_info(v: Any) -> sys._OptExcInfo | ExcInfo:
    """Depending on the Python version will try to do the smartest thing possible to transform *v* into an ``exc_info`` tuple."""
    if isinstance(v, BaseException):
        return (v.__class__, v, v.__traceback__)

    if isinstance(v, tuple):
        return v

    if v:
        return sys.exc_info()

    return (None, None, None)


class DatadogNormalisation(BasePreset):
    @classmethod
    def slots(cls) -> list[str]:
        return ["normalization"]

    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return ["prod"]

    def apply(self, conf: LoggerConfiguration) -> None:
        # XXX: self.__something__ ?
        pass

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, "logger.name", record.name)
        setattr(record, "logger.thread_name", record.threadName)
        setattr(record, "logger.method_name", record.funcName)
        setattr(record, "logger.version", loggia_version_str)

        # Level normalisation (including our custom loguru levels)
        levelname = record.levelname
        if levelname == "warn":
            levelname = "warning"

        if levelname == "success":
            levelname = "info"
        record.status = levelname

        # Error normalization
        if record.exc_info:
            # XXX: do we need to popattr(record.exc_info)?
            exc_type, exc_value, exc_traceback = _figure_out_exc_info(record.exc_info)
            # XXX cannot get None values here despite what the typing implies
            traceback_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            setattr(record, "error.stack", "".join(traceback_lines))
            setattr(record, "error.message", str(exc_value))
            setattr(record, "error.kind", exc_type.__module__ + "." + exc_type.__name__)  # type: ignore[union-attr]

        # DDTrace compatibility
        # XXX: Check intersection with DDTrace standard logger support
        if ddtrace:
            span = ddtrace.tracer.current_span()
            trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)
            setattr(record, "dd.trace_id", str(trace_id or 0))
            setattr(record, "dd.span_id", str(span_id or 0))

            # XXX: Maybe should not clobber those
            if ddtrace.config.env:
                setattr(record, "dd.env", ddtrace.config.env)
            if ddtrace.config.service:
                setattr(record, "dd.service", ddtrace.config.service)
            if ddtrace.config.version:
                setattr(record, "dd.version", ddtrace.config.version)
        return True
