"""Logging presets for Hypercorn."""
import logging
from logging import Filter

from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class DropColorMessageFilter(Filter):
    """Uvicorn sometimes add an extra `color_message`, which we want to drop.

    Not needed in JSON logging, and interferes with our own coloring in development.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__.pop("color_message", None)
        return True


class Uvicorn(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        conf.add_log_filter("uvicorn", {"()": DropColorMessageFilter})
