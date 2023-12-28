import logging
import os

import pytest

from loggia.logger import initialize


def test_usage(capsys: pytest.CaptureFixture[str]) -> None:
    # Configure the logger with default settings
    os.environ["ENV"] = "dev"
    initialize()

    logging.getLogger("test").warning("hello from logging", extra={"foo": "bar1"})

    logging.getLogger("test").error("error from logging", extra={"foo": "bar2"})
    try:
        raise ValueError("test")
    except ValueError:
        logging.getLogger("test").exception("exception from logging", extra={"foo": "bar3"})

    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "test" in captured.err
    assert "hello from logging" in captured.err
    assert "ERROR" in captured.err
    assert "error from logging" in captured.err
    assert "exception from logging" in captured.err
    assert "bar1" in captured.err
    assert "bar2" in captured.err
    assert "bar3" in captured.err
