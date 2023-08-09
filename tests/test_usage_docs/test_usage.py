import logging
import os

import pytest

from mm_logger.logger import configure_logging


def test_usage(capsys: pytest.CaptureFixture[str]) -> None:
    # Configure the logger with default settings
    os.environ["ENV"] = "dev"
    configure_logging()

    logging.getLogger("test").warning("hello from logging", extra={"foo": "bar"})

    logging.getLogger("test").error("error from logging", extra={"foo": "bar"})
    try:
        raise ValueError("test")
    except ValueError:
        logging.getLogger("test").exception("exception from logging", extra={"foo": "bar"})

    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "test" in captured.err
    assert "hello from logging" in captured.err
    assert "ERROR" in captured.err
    assert "error from logging" in captured.err
