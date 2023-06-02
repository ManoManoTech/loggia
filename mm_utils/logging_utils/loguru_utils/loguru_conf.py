import os
import sys

from mm_utils.logging_utils.loguru_utils.loguru_dd_format import datadog_formatter


def loguru_production_mode() -> None:
    try:
        from loguru import logger  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError("loguru is not installed") from exc

    logger.remove()
    logger.add(
        sys.__stdout__,
        format=datadog_formatter,  # type: ignore
        level=os.environ.get("LOGURU_LEVEL", os.environ.get("LOG_LEVEL", "INFO")),
    )


def loguru_extra_levels() -> None:
    try:
        from loguru import logger  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError("loguru is not installed") from exc

    logger.level("NIT_ERROR", no=4, color="<red><bold>", icon="🛑")
    logger.level("NIT_WARNING", no=3, color="<yellow>", icon="⚠️")
    logger.level("NIT_INFO", no=2, color="<blue>", icon="🐵")
    logger.level("NIT_DEBUG", no=1, color="<cyan>", icon="🐛")
