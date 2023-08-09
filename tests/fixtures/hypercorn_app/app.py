import logging

logger = logging.getLogger(__name__)


def app(environ, start_response):
    data = b"Hello, World!\n"
    logger.info("Hello, World!")
    start_response("200 OK", [("Content-Type", "text/plain"), ("Content-Length", str(len(data)))])
    return iter([data])
