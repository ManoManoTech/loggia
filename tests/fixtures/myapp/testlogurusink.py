import logging

import structlog
from loguru import logger as loguru_logger

from mm_utils.logging_utils.structlog_utils.log import configure_logging
from mm_utils.logging_utils.structlog_utils.loguru_sink import configure_loguru

# # Remove Loguru's default handler and add the custom sink function
# loguru_logger.remove()
# loguru_logger.add(loguru_to_structlog_sink, level=logging.DEBUG)

# # Sample Structlog configuration
# structlog.configure(
#     processors=[
#         structlog.stdlib.filter_by_level,  # Filter by log level
#         structlog.stdlib.add_log_level,  # Add log level to the event dict
#         structlog.stdlib.PositionalArgumentsFormatter(),
#         structlog.processors.TimeStamper(fmt="iso"),
#         structlog.processors.StackInfoRenderer(),
#         structlog.processors.format_exc_info,
#         structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
#     ],
#     context_class=dict,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
# )

configure_logging()
configure_loguru()
# Test logging with Loguru
loguru_logger.debug("Debug log from Loguru", argument1="test", argument2="test2")
loguru_logger.info("Info log from Loguru")
loguru_logger.warning("Warning log from Loguru")
loguru_logger.error("Error log from Loguru")
loguru_logger.critical("Critical log from Loguru", argument1="test", argument2="test2")
loguru_logger.trace("Trace log from Loguru")  # XXX Is ignored rn
loguru_logger.log("CRITICAL", "Critical log from Loguru, using log method")
loguru_logger.success("Success log from Loguru")  # XXX Is ignored rn
logging.getLogger().info("Test log from logging")
structlog.getLogger().info("Test log from structlog")
