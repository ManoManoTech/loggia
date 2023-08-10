import sys
import traceback
from logging import LogRecord
from types import TracebackType
from typing import Any, Union

from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration

ExcInfo = tuple[type[BaseException], BaseException, None | TracebackType]


try:
    import ddtrace
except ImportError:
    ddtrace = None


def _figure_out_exc_info(v: Any) -> Union["sys._OptExcInfo", "ExcInfo"]:
    """Depending on the Python version will try to do the smartest thing possible to transform *v* into an ``exc_info`` tuple."""
    if isinstance(v, BaseException):
        return (v.__class__, v, v.__traceback__)

    if isinstance(v, tuple):
        return v  # type: ignore[return-value]

    if v:
        return sys.exc_info()

    return (None, None, None)


class DatadogNormalisation(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        # XXX: self.__something__ ?
        conf.add_log_filter("", "loggia.presets.DatadogNormalisation")

    def filter(self, record: LogRecord) -> bool:
        setattr(record, "logger.name", record.name)
        setattr(record, "logger.thread_name", record.threadName)
        setattr(record, "logger.method_name", record.funcName)
        # XXX dd.version?

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
            setattr(record, "error.kind", exc_type.__module__ + "." + exc_type.__name__)

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
                setattr(record, "dd.service", ddtrace.config.version)
        return True
