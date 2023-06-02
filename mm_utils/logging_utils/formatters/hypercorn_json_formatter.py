from logging import Filter, LogRecord
from os import getenv
from typing import Any

from pythonjsonlogger.jsonlogger import RESERVED_ATTRS, JsonFormatter

from mm_utils.logging_utils.constants import GUNICORN_HYPERCORN_KEY_RE, HYPERCORN_ATTRIBUTES_MAP, SAFE_HEADER_ATTRIBUTES
from mm_utils.utils.dictutils import del_if_possible, mv_attr


# pylint:disable=too-many-branches
class CustomJsonFormatter(JsonFormatter):
    RESERVED_ATTRS = RESERVED_ATTRS

    def add_fields(self, log_record: dict[str, Any], record: LogRecord, message_dict: dict[str, Any]) -> None:
        # XXX probably send empty message dict and merge it ourselves instead of top level
        super().add_fields(log_record, record, message_dict)

        # Cleanup: just don't log cookies
        if "cookie" in log_record:
            log_record["cookie"] = "STRIPPED_AT_EMISSION"

        # Normalization: ManoMano attributes
        log_record["owner"] = "pulse"
        log_record["service"] = getenv("DD_SERVICE", "ms-radiologist-collector-python")
        log_record["project"] = getenv("PROJECT", "radiologist-collector-python")
        log_record["env"] = getenv("ENV", "dev")

        # Normalisation: Datadog source code attributes
        log_record["logger.name"] = record.name
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

        # Normalization: Datadog stack trace
        if "exc_info" in log_record:
            exc_info_lines = log_record["exc_info"].split("\n")
            log_record["error.stack"] = "\n".join(exc_info_lines[0:-1])
            log_record["error.message"] = exc_info_lines[-1]
            if log_record["error.message"]:
                log_record["error.kind"] = log_record["error.message"].split(":")[0]
            del log_record["exc_info"]

        # Cleanup and expansion of hypercorn specific log attributes
        if "hypercorn" in log_record["logger.name"]:
            if hasattr(record.args, "items"):
                for k, v in record.args.items():  # type: ignore
                    if k in HYPERCORN_ATTRIBUTES_MAP:
                        log_record[HYPERCORN_ATTRIBUTES_MAP[k]] = v
                    if "{" not in k or k.startswith("{http_") or "}e" in k:
                        continue
                    m = GUNICORN_HYPERCORN_KEY_RE.search(k)
                    if m:
                        log_record[m[1]] = v
            else:
                log_record["args.type"] = str(type(record.args))
                log_record["args"] = str(record.args)
        # Normalization: duration in nanoseconds from milliseconds
        if "duration" in log_record:
            log_record["duration"] = int(log_record["duration"] * 1000)
        # Normalisation: Datadog HTTP Attributes
        mv_attr(log_record, "raw_uri", "http.uri")
        mv_attr(log_record, "request_method", "http.method")
        mv_attr(log_record, "referer", "http.referer")
        mv_attr(log_record, "user_agent", "http.user_agent")
        mv_attr(log_record, "server_protocol", "http.version")

        header_attributes = SAFE_HEADER_ATTRIBUTES
        xtra_ks = [k for k in log_record.keys() if k.startswith("x-") or k.startswith("sec-")]
        header_attributes.extend(xtra_ks)
        for header_attr in header_attributes:
            mv_attr(log_record, header_attr, f"http.headers.{header_attr}")

        # XXX Normalisation: Client IP


class AccessLogFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        if not record.args:
            return True
        raw_uri: str = record.args["U"]  # type: ignore
        if "api/monitoring/" in raw_uri and record.levelno <= 20:
            return False

        return True
