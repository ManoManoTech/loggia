import logging

from loguru import logger as loguru_logger

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize

# # Remove Loguru's default handler and add the custom sink function
# loguru_logger.remove()
# loguru_logger.add(loguru_to_structlog_sink, level=logging.DEBUG)

config = LoggerConfiguration({"LOGGIA_CAPTURE_LOGURU": "true"})
initialize(config)

# Test logging with Loguru
loguru_logger.trace("Trace log from Loguru")
loguru_logger.debug("Debug log from Loguru")
loguru_logger.info("Info log from Loguru")
loguru_logger.success("Success log from Loguru")
loguru_logger.warning("Warning log from Loguru")
loguru_logger.error("Error log from Loguru")
loguru_logger.critical("Critical log from Loguru", argument1="test", argument2="test2")
loguru_logger.log("CRITICAL", "Critical log from Loguru, using log method")
# Test from standard logging
logging.getLogger().log(5, "Test trace from logging")
logging.getLogger().debug("Test debug from logging")
logging.getLogger().info("Test log from logging")
logging.getLogger().log(25, "Test success from logging")
logging.getLogger().warning("Test warning from logging")
logging.getLogger().error("Test error from logging")
logging.getLogger().critical("Test critical from logging")
logging.getLogger().log(0, "Test unset from logging with level 0")
