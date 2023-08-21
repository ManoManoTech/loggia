from __future__ import annotations

import os
import re
from socket import socket
from typing import TYPE_CHECKING, Any

from pythonjsonlogger.jsonlogger import RESERVED_ATTRS, JsonEncoder, JsonFormatter

from loggia.utils.dictutils import del_if_possible, del_many_if_possible, mv_attr

if TYPE_CHECKING:
    from logging import LogRecord

GUNICORN_KEY_RE = re.compile("{([^}]+)}")

DD_TRACE_ENABLED = os.environ.get("DD_TRACE_ENABLED")
if DD_TRACE_ENABLED:
    try:
        from ddtrace import tracer
    except ImportError:
        tracer = object()
        tracer.current_span = lambda: 0
GUNICORN_KEY_RE = re.compile("{([^}]+)}")


class CustomJsonEncoder(JsonEncoder):
    """Custom JSON encoder for xSGI server logs."""

    def encode(self, o: Any) -> str:
        if isinstance(o, socket):
            return super().encode({"socket": {"peer": o.getpeername()}})
        return super().encode(o)


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter for Loggia."""

    RESERVED_ATTRS = RESERVED_ATTRS

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        # pylint: disable=too-many-statements
        # XXX probably send empty message dict and merge it ourselves instead of top level
        super().add_fields(log_record, record, message_dict)

        # Cleanup: just don't log cookies
        if "cookie" in log_record:
            log_record["cookie"] = "STRIPPED_AT_EMISSION"
        if DD_TRACE_ENABLED:
            span = tracer.current_span()
            trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

            # add ids to structlog event dictionary
            log_record["dd.trace_id"] = str(trace_id or 0)
            log_record["dd.span_id"] = str(span_id or 0)

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
            log_record["duration"] = record.args["duration"]  # XXX document

        # Normalization: Datadog stack trace
        if "exc_info" in log_record:
            exc_info_lines = log_record["exc_info"].split("\n")
            log_record["error.stack"] = "\n".join(exc_info_lines[0:-1])
            log_record["error.message"] = exc_info_lines[-1]
            if log_record["error.message"]:
                log_record["error.kind"] = log_record["error.message"].split(":")[0]
            del log_record["exc_info"]

        # Cleanup and expansion of gunicorn specific log attributes
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

        # Normalization: Datadog user
        mv_attr(log_record, "mm-ff-user-id", "usr.id")

        # Normalisation: Datadog HTTP Attributes
        mv_attr(log_record, "raw_uri", "http.uri")
        mv_attr(log_record, "request_method", "http.method")
        mv_attr(log_record, "referer", "http.referer")
        mv_attr(log_record, "user_agent", "http.useragent")
        mv_attr(log_record, "server_protocol", "http.version")

        header_attributes = [
            "accept",
            "accept-encoding",
            "accept-language",
            "access-control-allow-origin",
            "cache-control",
            "connection",
            "content_length",
            "content-encoding",
            "content-length",
            "content-type",
            "cookie",
            "etag",
            "pragma",
        ]
        xtra_ks = [k for k in log_record if k.startswith(("x-", "sec-", "mm-"))]
        header_attributes.extend(xtra_ks)
        for header_attr in header_attributes:
            mv_attr(log_record, header_attr, f"http.headers.{header_attr}")

        # Normalisation: DataDog Client IP

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
