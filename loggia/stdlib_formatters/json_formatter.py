from __future__ import annotations

import os
import re
from socket import socket
from typing import TYPE_CHECKING, Any, Final, Protocol, runtime_checkable
from uuid import UUID

from pythonjsonlogger.jsonlogger import RESERVED_ATTRS, JsonEncoder, JsonFormatter

from loggia._internal.bootstrap_logger import bootstrap_logger
from loggia._internal.conf import is_truthy_string
from loggia.constants import SAFE_HEADER_ATTRIBUTES
from loggia.utils.dictutils import del_if_possible, del_many_if_possible, mv_attr

if TYPE_CHECKING:
    import logging

GUNICORN_KEY_RE = re.compile("{([^}]+)}")
DD_TRACE_ENABLED: Final[bool | None] = is_truthy_string(os.environ.get("DD_TRACE_ENABLED", False))
if DD_TRACE_ENABLED:
    try:
        from ddtrace import tracer
    except ImportError:
        bootstrap_logger.error("DD_TRACE_ENABLED environment variable is set but ddtrace package cannot be loaded")
        tracer = None  # type: ignore[assignment]


@runtime_checkable
class JsonSerializable(Protocol):
    """Protocol for any object willing to cooperate with our CustomJsonEncoder."""

    def __json__(self) -> str:
        ...


class CustomJsonEncoder(JsonEncoder):
    """Custom JSON encoder, handling some extra types like UUID or socket."""

    def encode(self, o: Any) -> str:  # noqa: PLR0911 # pylint: disable=too-many-return-statements
        if hasattr(o, "__json__"):
            if not isinstance(o, JsonSerializable):
                raise RuntimeError(f"Method __json__ on {o} does not conform to expectations")
            return o.__json__()
        if isinstance(o, UUID):
            return super().encode(str(o))
        if hasattr(o, "__module__") and o.__module__ == "loguru._recattrs":
            return super().encode(str(o))
        if type(o).__name__ == "function":
            # We don't match on callable cause it could catch more than we intend
            return super().encode(o.__qualname__)
        if hasattr(o, "__dataclass_fields__"):
            return super().encode(o.__dict__)
        if isinstance(o, socket):
            return super().encode({"socket": {"peer": o.getpeername()}})
        return super().encode(o)


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter for Loggia."""

    RESERVED_ATTRS = RESERVED_ATTRS

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)  # type: ignore[no-untyped-call]
        if DD_TRACE_ENABLED and tracer is not None:
            self.process_ddtrace = _process_ddtrace
        else:
            self.process_ddtrace = lambda log_record: None

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        # pylint: disable=too-many-statements
        # XXX probably send empty message dict and merge it ourselves instead of top level
        super().add_fields(log_record, record, message_dict)

        # Cleanup: just don't log cookies
        if "cookie" in log_record:
            log_record["cookie"] = "STRIPPED_AT_EMISSION"

        self.process_ddtrace(log_record)

        # Normalisation: Datadog source code attributes
        log_record["logger.name"] = record.name or "__undefined__"
        log_record["logger.thread_name"] = record.threadName
        log_record["logger.method_name"] = record.funcName
        mv_attr(log_record, "pathname", "logger.path_name")
        mv_attr(log_record, "lineno", "logger.lineno")
        del_if_possible(log_record, "name")
        del_if_possible(log_record, "funcName")

        # Normalisation: Datadog severity
        if "levelname" in log_record:
            log_record["status"] = log_record["levelname"]
            del log_record["levelname"]

        # Normalisation: Datadog duration (in nanoseconds)
        if record.args and "duration" in record.args and hasattr(record.args, "__getitem__"):
            log_record["duration"] = record.args["duration"]  # type: ignore[call-overload] # XXX document

        # Normalization: Datadog stack trace
        self._process_datadog_stack_trace(log_record)

        # Cleanup and expansion of gunicorn specific log attributes
        self._process_gunicorn_extra(log_record, record)

        # Normalisation: Datadog HTTP Attributes
        mv_attr(log_record, "raw_uri", "http.uri")
        mv_attr(log_record, "request_method", "http.method")
        mv_attr(log_record, "referer", "http.referer")
        mv_attr(log_record, "user_agent", "http.useragent")
        mv_attr(log_record, "server_protocol", "http.version")

        header_attributes = SAFE_HEADER_ATTRIBUTES
        xtra_ks = [k for k in log_record if k.startswith(("x-", "sec-", "mm-"))]
        header_attributes.extend(xtra_ks)
        for header_attr in header_attributes:
            mv_attr(log_record, header_attr, f"http.headers.{header_attr}")

        # Cleanup useless attributes
        del_many_if_possible(
            log_record,
            [
                "gunicorn.socket",
                "wsgi.file_wrapper",
                "wsgi.input_terminated",
                "wsgi.multiprocess",
                "wsgi.multithread",
                "wsgi.run_once",
                "wsgi.url_scheme",
                "wsgi.version",
                "wsgi.errors",
                "wsgi.input",
            ],
        )

    def _process_gunicorn_extra(self, log_record: dict[str, Any], record: logging.LogRecord) -> None:
        if "gunicorn" in log_record["logger.name"]:
            if hasattr(record.args, "items"):
                for k, v in record.args.items():  # type: ignore[union-attr]
                    if "{" not in k or k.startswith("{http_"):
                        continue
                    m = GUNICORN_KEY_RE.search(k)
                    if m:
                        log_record[m[1]] = v
            else:
                log_record["args.type"] = str(type(record.args))
                log_record["args"] = str(record.args)

    def _process_datadog_stack_trace(self, log_record: dict[str, Any]) -> None:
        if "exc_info" in log_record:
            exc_info_lines = log_record["exc_info"].split("\n")
            log_record["error.stack"] = "\n".join(exc_info_lines[0:-1])
            log_record["error.message"] = exc_info_lines[-1]
            if log_record["error.message"]:
                log_record["error.kind"] = log_record["error.message"].split(":")[0]
            del log_record["exc_info"]


def _process_ddtrace(log_record: dict[str, Any]) -> None:
    if tracer is None:
        return  # type: ignore[unreachable]
    span = tracer.current_span()
    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

    log_record["dd.trace_id"] = str(trace_id or 0)
    log_record["dd.span_id"] = str(span_id or 0)
