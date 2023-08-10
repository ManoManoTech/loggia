from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration
from loggia.stdlib_formatters.pretty_formatter import PrettyFormatter


class Dev(BasePreset):
    """An overarching preset for a delightful development experience."""
    @classmethod
    def slots(cls) -> list[str]:
        return ["main"]

    def apply(self, conf: LoggerConfiguration) -> None:
        conf.set_general_level("DEBUG")
        conf.set_default_formatter({"()": PrettyFormatter})

        debug_spammers = (
            "asyncio",
            "botocore",
            "boto3",
            "parso",
            "parso.cache",
            "parso.python.diff",
        )
        for logger in debug_spammers:
            conf.set_logger_level(logger, "INFO")
