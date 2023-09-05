from __future__ import annotations

import json
import os
import re
from importlib import reload
from typing import TYPE_CHECKING, Any

import pytest
from _pytest.capture import SysCapture

from loggia import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from _pytest.capture import CaptureManager
    from _pytest.fixtures import SubRequest

os.environ["ENV"] = "test"


@pytest.fixture(autouse=True)
def _reload_modules():
    """Automatic fixture to reload modules between tests."""
    import logging

    try:
        import loguru

        import loggia._internal.loguru_stuff
    except ImportError:
        loguru = None

    import loggia.logger
    import loggia.loguru_sink

    yield

    # Unload our optional dependencies

    # Repeat the above steps after test if required.
    logging.shutdown()
    logging = reload(logging)
    # Reinitialize logging
    logging.basicConfig()

    if loguru:
        loggia._internal.loguru_stuff._unblock_loguru_reconfiguration()
        loguru.logger.remove()

    loggia = reload(loggia)
    loggia.logger = reload(logger)

    if loguru:
        loggia.loguru_sink = reload(loggia.loguru_sink)


@pytest.fixture(autouse=True)
def _env_setup_teardown():
    """Reset the environment variables before and after each test. Better safe than sorry."""
    original_environ = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_environ)


class ErrlinesCaptureFixture(pytest.CaptureFixture[str]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lines: list[str] | None = None

    @property
    def lines(self):
        if self._lines:
            return self._lines

        captured = self.readouterr()
        err_lines = captured.err.split("\n")
        err_lines.remove("")  # ignore blank lines
        self._lines = err_lines
        return self._lines

    def strip_ansi_codes(self):
        def strip(text: str):
            return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)

        self._lines = [strip(line) for line in self._lines]

    @property
    def line(self):
        return self.lines[0] if self.lines else None

    def has_line_matching(self, fn: Callable[[str], bool]):
        return any(fn(line) for line in self._lines)

    def has_line_containing(self, substring: str):
        return any(substring in line for line in self._lines)


@pytest.fixture()
def caperrlines(request: SubRequest):
    """Convenience helper around capsys that only exposes non empty split stderr lines"""
    # most code lifted from upstreams capsys fixture
    capman: CaptureManager = request.config.pluginmanager.getplugin("capturemanager")
    capture_fixture = ErrlinesCaptureFixture(SysCapture, request, _ispytest=True)
    capman.set_fixture(capture_fixture)
    capture_fixture._start()
    yield capture_fixture
    capture_fixture.close()
    capman.unset_fixture()


class JsonStderrCaptureFixture(ErrlinesCaptureFixture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._records: list[Any] | None = None

    @property
    def records(self):
        if self._records:
            return self._records

        self._records = [json.loads(line) for line in self.lines]
        return self._records

    @property
    def record(self):
        return self.records[0] if self.records else None


@pytest.fixture()
def capjson(request: SubRequest):
    """Convenience helper around capsys that exposes parsed JSON records from stderr"""
    # most code lifted from upstreams capsys fixture
    capman: CaptureManager = request.config.pluginmanager.getplugin("capturemanager")
    capture_fixture = JsonStderrCaptureFixture(SysCapture, request, _ispytest=True)
    capman.set_fixture(capture_fixture)
    capture_fixture._start()
    yield capture_fixture
    capture_fixture.close()
    capman.unset_fixture()
