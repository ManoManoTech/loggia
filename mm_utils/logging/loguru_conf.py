import os
import sys

from mm_utils.logging.loguru_dd_format import datadog_formatter

try:
    from loguru import logger
except ImportError:
    logger = None


def loguru_production_mode():
    if logger is None:
        raise ImportError("loguru is not installed")
    logger.remove()
    logger.add(
        sys.__stdout__,
        format=datadog_formatter,
        level=os.environ.get("LOGURU_LEVEL", os.environ.get("LOG_LEVEL", "INFO")),
    )


def loguru_extra_levels():
    if logger is None:
        raise ImportError("loguru is not installed")
    logger.level("NIT_ERROR", no=4, color="<red><bold>", icon="🛑")
    logger.level("NIT_WARNING", no=3, color="<yellow>", icon="⚠️")
    logger.level("NIT_INFO", no=2, color="<blue>", icon="🐵")
    logger.level("NIT_DEBUG", no=1, color="<cyan>", icon="🐛")
