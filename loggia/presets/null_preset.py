from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class NullPreset(BasePreset):
    """Use this preset as an easy to cut and paste template to write you own.

    This preset does and changes strictly nothing.
    """
    def apply(self, conf: LoggerConfiguration) -> None:
        pass
