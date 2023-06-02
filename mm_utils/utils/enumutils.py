from enum import Enum


class EasyEnum(Enum):
    """A base class for enums that makes it easier to get a list of allowed values and provider better error messages."""

    @classmethod
    def allowed_values(cls) -> str:
        quoted_members = (f"'{s}'" for s in cls.__members__)
        return ", ".join(quoted_members)

    @classmethod
    def error_message_for(cls, thing) -> str:
        return f"'{thing}' is not a valid {cls}." f" Allowed: {cls.allowed_values()}"
