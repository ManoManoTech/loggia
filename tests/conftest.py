import json
import os
from importlib import reload
from typing import TYPE_CHECKING, Any

import pytest
from _pytest.capture import SysCapture
from _pytest.fixtures import SubRequest

from loggia import logger

if TYPE_CHECKING:
    from _pytest.capture import CaptureManager

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


class JsonStderrCaptureFixture(pytest.CaptureFixture[str]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._records: list[Any] | None  = None

    @property
    def records(self):
        if self._records:
            return self._records

        captured = self.readouterr()
        err_lines = captured.err.split("\n")
        err_lines.remove("")  # ignore blank lines
        self._records = [json.loads(line) for line in err_lines]
        return self._records

    @property
    def record(self):
        return self.records[0]


@pytest.fixture()
def capjson(request: SubRequest):
    capman: CaptureManager = request.config.pluginmanager.getplugin("capturemanager")
    capture_fixture = JsonStderrCaptureFixture(SysCapture, request, _ispytest=True)
    capman.set_fixture(capture_fixture)
    capture_fixture._start()
    yield capture_fixture
    capture_fixture.close()
    capman.unset_fixture()
