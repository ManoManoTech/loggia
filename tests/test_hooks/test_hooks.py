import logging
import os.path
import subprocess
import sys

import pytest

from loggia.logger import _set_excepthook

__HERE__ = os.path.dirname(__file__)  # noqa: PTH120


def run_script(script_name, *args, expected_retcode: int = 1):
    completed_process = subprocess.run(
        ["python3", f"tests/test_hooks/{script_name}", *args],  # noqa: S603 S607
        capture_output=True,
        check=False,
    )
    assert completed_process.returncode == expected_retcode
    return completed_process


def test_set_excepthook_on(capsys: pytest.CaptureFixture[str]):
    # This only controls the settings/preset mechanics, not actual functionality
    logger = logging.getLogger("test_logger")
    previous_hook = sys.excepthook
    _set_excepthook(logger)
    assert logger is not None
    assert sys.excepthook is not previous_hook


@pytest.fixture()
def _env_setup_teardown():
    # Override the fixture to make it a no-op
    pass


def test_excepthook_1():
    ret = run_script("excepthook_test_1.py")
    assert "test unhandled exception" in ret.stderr.decode()


def test_excepthook_2():
    ret = run_script("excepthook_test_2.py", expected_retcode=10)
    assert "boom" in ret.stderr.decode()


def test_unraisablehook_1():
    ret = run_script("unraisablehook_test_1.py", expected_retcode=0)
    assert "error.stack" in ret.stderr.decode()
    assert "del is broken" in ret.stderr.decode()


def test_unraisablehook_2():
    ret = run_script("unraisablehook_test_2.py", expected_retcode=10)
    assert "boom" in ret.stderr.decode()


def test_threadinghook_1():
    ret = run_script("threadinghook_test_1.py", expected_retcode=0)
    assert "error.stack" in ret.stderr.decode()
    assert "thread unhandled" in ret.stderr.decode()


def test_threadinghook_2():
    ret = run_script("threadinghook_test_2.py", expected_retcode=10)
    assert "boom" in ret.stderr.decode()
