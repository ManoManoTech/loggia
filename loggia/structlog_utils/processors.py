"""This module contains custom processors for structlog.

They are used in the default configuration, but you can also use them in your own configuration.
"""
import logging
import logging.config
import os
import sys
import traceback
from collections.abc import Iterable, Mapping
from logging import Logger, LogRecord
from types import FrameType, TracebackType
from typing import Any

from loggia.presets.datadog_normalisation import _figure_out_exc_info

try:
    import ddtrace
except ImportError:
    ddtrace = None  # type: ignore[assignment]

EventDict = dict[str, Any]
ExcInfo = tuple[type[BaseException], BaseException, None | TracebackType]
CONSOLE = bool(os.getenv("ENV") == "DEV")


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


def datadog_add_logger_name(logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """Add the logger name to the event dict, using DataDog's naming convention, under the ``logger.name`` key."""
    record = event_dict.get("_record")
    if record is not None:
        event_dict["logger.name"] = record.name
    else:
        event_dict["logger.name"] = logger.name
    return event_dict


def datadog_add_log_level(_: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add the log level to the event dict under the ``status`` key.

    Since that's just the log method name, this processor works with non-stdlib
    logging as well.

    Modified to use DataDog's naming convention from structlog.stdlib.add_log_level.
    """
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"

    event_dict["status"] = method_name

    return event_dict


def extract_from_record_datadog(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    """Extract thread and process names and add them to the event dict.

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


def datadog_error_mapping_processor(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    """Extracts the exception information from the event dict and adds it to the event dict as error.stack, error.message and error.kind."""
    if "exc_info" in event_dict:
        exc_type, exc_value, exc_traceback = _figure_out_exc_info(event_dict.pop("exc_info"))
        if exc_type is None or exc_value is None or exc_traceback is None:
            return event_dict
        event_dict["error.stack"] = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        event_dict["error.message"] = str(exc_value)
        event_dict["error.kind"] = exc_type.__module__ + "." + exc_type.__name__

    return event_dict


class RemoveKeysProcessor:
    """Removes keys from the event dict, if they are present.

    The very naive code with a loop and pop is quite fast.

    Args:
        keys: Keys to remove.
    """

    def __init__(self, keys: Iterable[str]) -> None:
        self.keys = frozenset(keys)

    def __call__(self, logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        for key in self.keys:
            event_dict.pop(key, None)
        return event_dict


class RemoveKeysStartingWithProcessor:
    """Removes keys from the event dict, if they start with the given prefix."""

    def __init__(self, keys_prefix: Iterable[str]) -> None:
        self.keys_prefix = frozenset(keys_prefix)

    def __call__(self, logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        return {k: v for k, v in event_dict.items() if not any(k.startswith(prefix) for prefix in self.keys_prefix)}


class DataDogTraceInjectionProcessor:
    """Adds ddtrace trace and span ids to the event dict, as well as dd.env, dd.service and dd.owner.

    Requires [ddtrace](https://ddtrace.readthedocs.io/en/stable/) to be initialized.

    This processor does **not** configure ddtrace.

    Adapted from the[ official Datadog documentation](https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/#no-standard-library-logging)
    """

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        if not ddtrace:
            # XXX Should we ignore this silently?
            raise ImportError("ddtrace is not installed")
        self.ddtrace = ddtrace

    def __call__(self, logger: logging.Logger, log_method: str, event_dict: EventDict) -> EventDict:
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


def _find_first_app_frame_and_name(
    additional_ignores: list[str] | None = None,
) -> tuple[FrameType, str]:
    """Remove all intra-structlog calls and return the relevant app frame.

    :param additional_ignores: Additional names with which the first frame must
        not start.

    :returns: tuple of (frame, name)
    """
    ignores = ["structlog"] + (additional_ignores or [])
    f = sys._getframe()
    name = f.f_globals.get("__name__") or "?"
    while any(tuple(name.startswith(i) for i in ignores)):
        if f.f_back is None:
            name = "?"
            break
        f = f.f_back
        name = f.f_globals.get("__name__") or "?"
    return f, name


# class CallsiteParameterAdderWithStacklevel(CallsiteParameterAdder):
#     """ZOR."""

#     def __call__(
#         self,
#         logger: logging.Logger,
#         name: str,
#         event_dict: EventDict,
#     ) -> EventDict:
#         record: logging.LogRecord | None = event_dict.get("_record")
#         from_structlog: bool | None = event_dict.get("_from_structlog")
#         # If the event dictionary has a record, but it comes from structlog,
#         # then the callsite parameters of the record will not be correct.
#         if record is not None and not from_structlog:
#             for mapping in self._record_mappings:
#                 event_dict[mapping.event_dict_key] = record.__dict__[mapping.record_attribute]
#         else:
#             depth = 1
#             if "stacklevel" in event_dict:
#                 depth = int(event_dict["stacklevel"])

#             frame, module = _find_first_app_frame_and_name(
#                 additional_ignores=self._additional_ignores,
#             )
#             frame_info = inspect.getframeinfo(frame, depth)
#             for parameter, handler in self._active_handlers:
#                 event_dict[parameter.value] = handler(module, frame_info)
#         return event_dict
