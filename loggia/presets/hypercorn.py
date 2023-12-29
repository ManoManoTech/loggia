"""Logging presets for Hypercorn."""
from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class Hypercorn(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        pass  # XXX TBD
