import pytest


# ruff: noqa: F811
def test_trace_with_standard(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->
    # Assuming we want a very verbose logger
    from os import environ
    environ["LOG_LEVEL"] = "TRACE"

    # Setup
    from mm_logger.logger import configure_logging
    configure_logging()

    # Use standard logger
    from logging import getLogger
    logger = getLogger()

    # Use the added trace level
    logger.log(level=5, msg="Hello trace from the std_lib!")
    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "Hello trace from the std_lib!" in captured.err
