import os
from importlib import reload

import pytest

from loggia import logger

os.environ["ENV"] = "test"


@pytest.fixture(autouse=True)
def _reload_modules():
    """Automatic fixture to reload modules between tests."""
    import logging

    import loguru

    import loggia.logger
    import loggia.loguru_sink

    yield

    # Repeat the above steps after test if required.
    logging.shutdown()
    logging = reload(logging)
    # Reinitialize logging
    logging.basicConfig()
    loggia.loguru_sink._unblock_loguru_reconfiguration()

    loguru.logger.remove()

    loggia = reload(loggia)
    loggia.logger = reload(logger)
    loggia.loguru_sink = reload(loggia.loguru_sink)


@pytest.fixture(autouse=True)
def _env_setup_teardown():
    """Reset the environment variables before and after each test. Better safe than sorry."""
    original_environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)
