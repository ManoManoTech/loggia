"""An overarching preset for a no-frills JSON production logger to stdout."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loggia.base_preset import BasePreset
from loggia.stdlib_formatters.json_formatter import CustomJsonEncoder, CustomJsonFormatter

if TYPE_CHECKING:
    from logging import Formatter

    from loggia.conf import LoggerConfiguration


def _build_json_formatter() -> dict[str, type[Formatter] | Any]:
    attr_whitelist = {"name", "levelname", "pathname", "lineno", "funcName"}
    attrs = [x for x in CustomJsonFormatter.RESERVED_ATTRS if x not in attr_whitelist]
    return {
        "()": CustomJsonFormatter,
        "json_indent": None,
        "json_encoder": CustomJsonEncoder,
        "reserved_attrs": attrs,
        "timestamp": True,
    }


class Prod(BasePreset):
    @classmethod
    def slots(cls) -> list[str]:
        return ["main"]

    def apply(self, conf: LoggerConfiguration) -> None:
        conf.set_default_formatter(_build_json_formatter())

        # No access logs in production, ingress/api gateways provide them.
        conf.set_logger_level("hypercorn.access", "WARNING")
