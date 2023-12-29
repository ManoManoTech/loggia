"""An overarching preset for a no-frills JSON production logger to stdout."""
from __future__ import annotations

from typing import TYPE_CHECKING

from loggia.base_preset import BasePreset
from loggia.stdlib_formatters.json_formatter import CustomJsonEncoder, CustomJsonFormatter

if TYPE_CHECKING:
    import logging

    from loggia.conf import LoggerConfiguration
    from loggia.types import UserDefinedObject


def _build_json_formatter() -> UserDefinedObject[logging.Formatter]:
    attr_allowlist = {"name", "levelname", "pathname", "lineno", "funcName"}
    attrs = [x for x in CustomJsonFormatter.RESERVED_ATTRS if x not in attr_allowlist]

    def custom_json_formatter_ctor() -> CustomJsonFormatter:
        return CustomJsonFormatter(json_indent=None, json_encoder=CustomJsonEncoder, reserved_attrs=attrs, timestamp=True)

    return {"()": custom_json_formatter_ctor}


class Prod(BasePreset):
    @classmethod
    def slots(cls) -> list[str]:
        return ["main"]

    def apply(self, conf: LoggerConfiguration) -> None:
        conf.set_default_formatter(_build_json_formatter())
        conf.set_general_level("INFO")
        conf.set_excepthook(enabled=True)
        conf.set_unraisablehook(enabled=True)
        conf.set_threading_excepthook(enabled=True)

        # No access logs in production, ingress/api gateways provide them.
        conf.set_logger_level("hypercorn.access", "WARNING")
