"""This modules provide a custom sink function for Loguru to pass log messages to Structlog.

It is an experimental feature and is not recommended for production use.

It should help if libraries use Loguru for logging and you want to use Structlog for your application.

It is not recommended to use it if your application primiraly uses Loguru for logging.

If you use primarily use loguru, you should consider using logging or structlog instead.


"""

import logging

import structlog
from loguru import logger as loguru_logger

from mm_utils.logging_utils.structlog_utils.log import configure_logging


class LoguruMessage(str):
    """From loguru._logger.Message."""

    __slots__ = ("record",)


# Custom sink function for Loguru to pass log messages to Structlog
def loguru_to_structlog_sink(message: LoguruMessage | str):
    record: dict = message.record
    # structlog_logger: structlog.stdlib.BoundLogger = structlog.wrap_logger(

    #     processors=[
    #         # Add your structlog processors here, e.g., filtering, formatting, etc.
    #         structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    #     ],
    #     context_class=dict,
    #     logger_factory=structlog.stdlib.LoggerFactory(),
    #     wrapper_class=structlog.stdlib.BoundLogger,
    # )
    structlog_logger = structlog.getLogger(record["name"])
    # structlog_logger.log()
    # XXX log_method is not perfect (loguru supports trace for example)
    # XXX test with loguru.log
    # log_method = getattr(structlog_logger, record["level"].no)
    lineno = record.get("line")
    pathname = record.get("path")
    file = record.get("file")

    filename = file.name if file else None
    pathname = file.path if file else None
    module = record.get("module")

    structlog_logger.log(
        level=record["level"].no,
        event=record["message"],
        # {
        **{"lineno": lineno, "module": module, "pathname": pathname, "filename": filename},
        **record["extra"],
        # },
        stacklevel=5,
        # stack_info=True,
    )


def configure_loguru():
    # # Remove Loguru's default handler and add the custom sink function
    loguru_logger.remove()
    loguru_logger.add(loguru_to_structlog_sink, level=logging.DEBUG)


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

# configure_logging()
# # Test logging with Loguru
# loguru_logger.debug("Debug log from Loguru", argument1="test", argument2="test2")
# loguru_logger.info("Info log from Loguru")
# loguru_logger.warning("Warning log from Loguru")
# loguru_logger.error("Error log from Loguru")
# loguru_logger.critical("Critical log from Loguru", argument1="test", argument2="test2")
# loguru_logger.trace("Trace log from Loguru")  # XXX Is ignored rn
# loguru_logger.log("CRITICAL", "Critical log from Loguru, using log method")
# loguru_logger.success("Success log from Loguru")  # XXX Is ignored rn
