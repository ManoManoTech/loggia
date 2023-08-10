from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class Gunicorn(BasePreset):
    """Logging presets for Gunicorn."""
    def apply(self, conf: LoggerConfiguration) -> None:
        conf.set_logger_propagation("gunicorn.access", "0")
        conf.set_logger_propagation("gunicorn.error", "0")
        conf.set_logger_propagation("gunicorn.errors", "0")
