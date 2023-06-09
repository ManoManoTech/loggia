import os
from importlib import reload

import pytest

from mm_logs import logger, structlog_utils

os.environ["ENV"] = "test"


@pytest.fixture(autouse=True)
def _reload_modules():
    """Automatic fixture to reload modules between tests."""
    import logging

    import loguru
    import structlog
    import structlog.stdlib

    import mm_logs.logger
    import mm_logs.loguru_sink
    import mm_logs.structlog_utils

    yield

    # Repeat the above steps after test if required.
    logging.shutdown()
    logging = reload(logging)
    # Reinitialize logging
    logging.basicConfig()
    mm_logs.loguru_sink._unblock_loguru_reconfiguration()

    loguru.logger.remove()

    structlog = reload(structlog)
    structlog.stdlib = reload(structlog.stdlib)

    mm_logs = reload(mm_logs)
    mm_logs.logger = reload(logger)
    mm_logs.structlog_utils = reload(structlog_utils)
    mm_logs.loguru_sink = reload(mm_logs.loguru_sink)


@pytest.fixture(autouse=True)
def _env_setup_teardown():
    """Reset the environment variables before and after each test. Better safe than sorry."""
    original_environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)
