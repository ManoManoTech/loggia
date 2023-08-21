"""Dev is the overarching preset for a delightful development experience."""
from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration
from loggia.stdlib_formatters.pretty_formatter import PrettyFormatter
from loggia._internal.conf import EnvironmentLoader
import loggia._internal.env_parsers as ep


env = EnvironmentLoader()


class Dev(BasePreset):    
    def __init__(self) -> None:
        self.add_filename_to_logs_with_modified_stack = True

    @classmethod
    def slots(cls) -> list[str]:
        return ["main"]

    @env.register(parser=ep.single_boolean_string)
    def set_add_filename_to_logs_with_modified_stack(self, value: bool):  # noqa:FBT001
        self.add_filename_to_logs_with_modified_stack = value

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
