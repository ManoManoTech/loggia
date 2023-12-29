"""Logging presets for Gunicorn."""
from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class Gunicorn(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        pass  # XXX TBD
