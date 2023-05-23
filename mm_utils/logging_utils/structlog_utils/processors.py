import inspect
import logging.config
import os
import sys
import traceback
from logging import Logger, LogRecord, _nameToLevel
from types import TracebackType
from typing import Any, Iterable, Mapping, Protocol, Union

try:
    import ddtrace
except ImportError:
    ddtrace = None
import structlog
from structlog.typing import EventDict, Processor, WrappedLogger

# XXX Make sure that all processors types are correct. With processor
ExcInfo = tuple[type[BaseException], BaseException, None | TracebackType]
CONSOLE = True if os.getenv("ENV") == "DEV" else True


class ManoManoDataDogAttributesProcessor:
    """Adds ManoMano specific attributes to the event dict.

    The attributes will override any existing attributes with the same name:
    service, owner, env, project.
    """

    def __init__(self, service: str | None = None, owner: str | None = None, env: str | None = None, project: str | None = None) -> None:
        service = service or os.getenv("SERVICE", os.getenv("DD_SERVICE"))
        owner = owner or os.getenv("OWNER", os.getenv("DD_OWNER"))
        env = env or os.getenv("ENV", os.getenv("DD_ENV"))
        project = project or os.getenv("PROJECT", os.getenv("DD_PROJECT"))
        # This dict is immutable, so we can't add to it.

        self.mm_dd_attributes: dict[str, str] = {}
        # Add if not None.
        for k, v in (("service", service), ("owner", owner), ("env", env), ("project", project)):
            if v is not None:
                self.mm_dd_attributes[k] = v

    def __call__(self, logger: Logger, name: str, event_dict: EventDict) -> EventDict:
        return {**event_dict, **self.mm_dd_attributes}


class EventAttributeMapper:
    """Maps event attributes to new names, if they are present.

    Args:
        event_attribute_map: A dict mapping the original attribute name to the new attribute name.
    """

    def __init__(self, event_attribute_map: Mapping[str, str]) -> None:
        self.event_attribute_map = event_attribute_map

    def __call__(self, logger: Logger, name: str, event_dict: EventDict) -> EventDict:
        for k, v in self.event_attribute_map.items():
            if k in event_dict:
                event_dict[v] = event_dict.pop(k)
        return event_dict


def datadog_add_logger_name(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add the logger name to the event dict, using DataDog's naming convention, under the ``logger.name`` key.
    """
    record = event_dict.get("_record")
    if record is None:
        event_dict["logger.name"] = logger.name
    else:
        event_dict["logger.name"] = record.name
    return event_dict


def datadog_add_log_level(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add the log level to the event dict under the ``status`` key.

    Since that's just the log method name, this processor works with non-stdlib
    logging as well.

    Modified to use DataDog's naming convention from structlog.stdlib.add_log_level.
    """
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"

    event_dict["status"] = method_name

    return event_dict


def extract_from_record_datadog(_, __, event_dict: EventDict) -> EventDict:
    """
    Extract thread and process names and add them to the event dict.
    They are added under the ``logger`` key to be compatible with DataDog's naming convention.

    """
    record: LogRecord = event_dict["_record"]
    event_dict["logger.thread_name"] = record.threadName
    event_dict["logger.name"] = record.name
    event_dict["logger.method_name"] = record.funcName

    # Extract tracebacks from the record if present
    if record.exc_info:
        event_dict["exc_info"] = record.exc_info

    return event_dict


# def extract_from_record(_, __, event_dict):
#     """
#     Extract thread and process names and add them to the event dict.
#     """
#     record = event_dict["_record"]
#     event_dict["thread_name"] = record.threadName
#     event_dict["process_name"] = record.processName

#     return event_dict


def datadog_error_mapping_processor(_, __, event_dict: EventDict) -> EventDict:
    """
    Extracts the exception information from the event dict and adds it to the
    event dict as error.stack, error.message and error.kind.
    """
    if "exc_info" in event_dict:
        exc_type, exc_value, exc_traceback = _figure_out_exc_info(event_dict.pop("exc_info"))
        if exc_type is None or exc_value is None or exc_traceback is None:
            return event_dict
        event_dict["error.stack"] = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        event_dict["error.message"] = str(exc_value)
        event_dict["error.kind"] = exc_type.__name__

    return event_dict


timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp")
logger_name = structlog.stdlib.add_logger_name if CONSOLE else datadog_add_logger_name


def _figure_out_exc_info(v: Any) -> Union["sys._OptExcInfo", "ExcInfo"]:
    """
    Depending on the Python version will try to do the smartest thing possible
    to transform *v* into an ``exc_info`` tuple.

    """
    if isinstance(v, BaseException):
        return (v.__class__, v, v.__traceback__)

    if isinstance(v, tuple):
        return v  # type: ignore[return-value]

    if v:
        return sys.exc_info()  # type: ignore[return-value]

    return (None, None, None)


class RemoveKeysProcessor:
    """Removes keys from the event dict, if they are present.

    This very naive code with a loop and pop is quite fast.

    Args:
        keys: Keys to remove.
    """

    def __init__(self, keys: Iterable[str]) -> None:
        self.keys = frozenset(keys)

    def __call__(self, logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        for key in self.keys:
            event_dict.pop(key, None)
        return event_dict


def add_log_level_number(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add the log level number to the event dict.

    Log level numbers map to the log level names. The Python stdlib uses them
    for filtering logic. This adds the same numbers so users can leverage
    similar filtering. Compare::

       level in ("warning", "error", "critical")
       level_number >= 30

    The mapping of names to numbers is in
    ``structlog.stdlib._log_levels._NAME_TO_LEVEL``.

    .. versionadded:: 18.2.0
    """
    # Supports custom log levels.
    # event_dict["level_number"] = logger._nameToLevel.get(method_name, 0)  # type: ignore[attr-defined]
    return event_dict


# all_levels = set(logging._nameToLevel.values())  # type: ignore[attr-defined]

# logging.addLevelName(TRACE, "TRACE")
# logging.getLevelNamesMapping


class DataDogTraceInjectionProcessor:
    """Adapted from the official Datadog documentation https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/#no-standard-library-logging"""

    def __init__(self, *args, **kwargs):
        if not ddtrace:
            # XXX Should we ignore this silently?
            raise ImportError("ddtrace is not installed")
        self.ddtrace = ddtrace

    def __call__(self, logger, log_method, event_dict: EventDict) -> EventDict:
        # get correlation ids from current tracer context
        span = self.ddtrace.tracer.current_span()
        trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

        # add ids to structlog event dictionary
        event_dict["dd.trace_id"] = str(trace_id or 0)
        event_dict["dd.span_id"] = str(span_id or 0)

        # add the env, service, and version configured for the tracer
        event_dict["dd.env"] = self.ddtrace.config.env or ""
        event_dict["dd.service"] = self.ddtrace.config.service or ""
        event_dict["dd.version"] = self.ddtrace.config.version or ""
        return event_dict


import enum
import inspect
import logging
import os
import threading
from typing import Any, Callable, ClassVar, Collection, NamedTuple, Optional

from structlog.processors import CallsiteParameter, CallsiteParameterAdder, _find_first_app_frame_and_name

# from structlog.stdlib import get_processname
from structlog.types import EventDict


class CustomCallsiteParameter(enum.Enum):
    FUNCNAME = "logger.method_name"


# Define a type alias for convenience
CallsiteParameterType = Union[CallsiteParameter, CustomCallsiteParameter]


class CustomCallsiteParameterAdder(CallsiteParameterAdder):
    def __init__(
        self,
        parameters: Collection[CallsiteParameter] = CallsiteParameterAdder._all_parameters,
        additional_ignores: list[str] | None = None,
        custom_attribute_names: dict[CallsiteParameter, str] | None = None,
    ) -> None:
        super().__init__(parameters=parameters, additional_ignores=additional_ignores)
        self._custom_attribute_names = custom_attribute_names or {}

        for parameter, custom_name in self._custom_attribute_names.items():
            self._record_mappings.append(self._RecordMapping(custom_name, self._record_attribute_map[parameter]))

    def __call__(self, logger: logging.Logger, name: str, event_dict: EventDict) -> EventDict:
        record: logging.LogRecord | None = event_dict.get("_record")
        from_structlog: bool | None = event_dict.get("_from_structlog")

        if record is not None and not from_structlog:
            for mapping in self._record_mappings:
                if mapping.event_dict_key not in event_dict:
                    event_dict[mapping.event_dict_key] = record.__dict__[mapping.record_attribute]
        else:
            frame, module = _find_first_app_frame_and_name(additional_ignores=self._additional_ignores)
            frame_info = inspect.getframeinfo(frame)
            for parameter, handler in self._active_handlers:
                if parameter.value not in event_dict:
                    new_key = self._custom_attribute_names.get(parameter, parameter.value)
                    event_dict[new_key] = handler(module, frame_info)
        return event_dict
