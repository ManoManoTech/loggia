"""The null preset does nothing.

Use this preset as an easy to cut and paste template to write you own.
This preset changes strictly nothing.
"""
from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class NullPreset(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        pass
