import os
import sys
import traceback
from datetime import timedelta

from loguru import logger
from loguru._recattrs import RecordException, RecordFile, RecordLevel, RecordProcess, RecordThread

from mm_utils.utils.dictutils import mv_attr

from .json import dumps


def datadog_formatter(record: dict):
    """
    Massage record to have attributes name consistently with the Datadog convention:
    https://docs.datadoghq.com/logs/log_configuration/attributes_naming_convention/#overview
    """

    # Normalization: Datadog source code attributes for standard Python logging attributes
    mv_attr(record, "name", "logger.name")
    mv_attr(record, "threadName", "logger.thread_name")
    mv_attr(record, "function", "logger.method_name")
    mv_attr(record, "funcName", "logger.method_name")
    mv_attr(record, "lineno", "logger.lineno")
    mv_attr(record, "line", "logger.lineno")

    # Normalization: Loguru Record
    # (These are not Datadog standard attributes per-se)
    if "file" in record and isinstance(record["file"], RecordFile):
        record["logger.path"] = record["file"].path
        record["logger.file_name"] = record["file"].name
        del record["file"]

    # Normalization: Loguru thread
    if "thread" in record and isinstance(record["thread"], RecordThread):
        record["logger.thread_name"] = record["thread"].name
        record["logger.thread_id"] = record["thread"].id
        del record["thread"]

    # Normalization: Loguru process
    if "process" in record and isinstance(record["process"], RecordProcess):
        record["logger.process_name"] = record["process"].name
        record["logger.process_id"] = record["process"].id
        del record["process"]

    # Normalization: Datadog severity (for standard Python logging)
    mv_attr(record, "levelname", "status")

    # Normalization: Datadog severity (for loguru logging)
    if "level" in record and isinstance(record["level"], RecordLevel):
        record["status"] = record["level"].name
        del record["level"]

    # Normalization: Datadog duration in nanoseconds (for standard Python logging)
    if "msecs" in record:
        record["duration"] = record.msecs * 1000000

    # Normalization: Datadog duration in nanoseconds (for loguru logging)
    if "elapsed" in record and isinstance(record["elapsed"], timedelta):
        mv_attr(record, "elapsed", "duration")
        record["duration"] = record["duration"].total_seconds() / 1000000000

    # Normalization: Datadog stack trace (for loguru logging)
    if "exception" in record and isinstance(record["exception"], RecordException):
        exc = record["exception"]
        exc_info_lines = traceback.format_exception(exc.type, exc.value, exc.traceback)
        record["error.stack"] = "\n".join(exc_info_lines[0:-1])
        record["error.message"] = exc_info_lines[-1].strip()
        record["error.kind"] = exc.type.__name__
        record["exception"] = None  # loguru expects this key to be present at all times

    # Normalization: Datadog stack trace (for standard Python logging)
    if "exc_info" in record:
        exc_info_lines = record["exc_info"].split("\n")
        record["error.stack"] = "\n".join(exc_info_lines[0:-1])
        record["error.message"] = exc_info_lines[-1].strip()
        if record["error.message"]:
            record["error.kind"] = record["error.message"].split(":")[0]
        del record["exc_info"]

    # Store serialized record in record and send that back to loguru
    record["_serialized"] = dumps(record)
    return "{_serialized}\n"
