from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class Hypercorn(BasePreset):
    """Logging presets for Hypercorn."""
    def apply(self, conf: LoggerConfiguration) -> None:
        conf.set_logger_propagation("hypercorn.access", "0")
        conf.set_logger_propagation("hypercorn.error", "0")
