from enum import Enum


class EasyEnum(Enum):
    @classmethod
    def allowed_values(cls):
        quoted_members = map(lambda s: f"'{s}'", cls.__members__.keys())
        return ", ".join(quoted_members)

    @classmethod
    def error_message_for(cls, thing):
        return f"'{thing}' is not a valid {cls}." f" Allowed: {cls.allowed_values()}"
