import os
from importlib import reload

import pytest

from mm_logger import logger

os.environ["ENV"] = "test"


@pytest.fixture(autouse=True)
def _reload_modules():
    """Automatic fixture to reload modules between tests."""
    import logging

    import loguru

    import mm_logger.logger
    import mm_logger.loguru_sink

    yield

    # Repeat the above steps after test if required.
    logging.shutdown()
    logging = reload(logging)
    # Reinitialize logging
    logging.basicConfig()
    mm_logger.loguru_sink._unblock_loguru_reconfiguration()

    loguru.logger.remove()

    mm_logger = reload(mm_logger)
    mm_logger.logger = reload(logger)
    mm_logger.loguru_sink = reload(mm_logger.loguru_sink)


@pytest.fixture(autouse=True)
def _env_setup_teardown():
    """Reset the environment variables before and after each test. Better safe than sorry."""
    original_environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)
