import os

import pytest


def test_usage_basic(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->

    # Setup
    from mm_logger.logger import initialize

    # One-line setup -- get the default config from environment variables
    initialize({"MM_LOGGER_FORMATTER": "pretty"})

    # Use just like the standard logger
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Hello world!")

    # <!-- DOC:END -->
    captured = capsys.readouterr()
    assert "INFO" in captured.err
    assert "test_usage_basic" in captured.err
    assert "Hello world!" in captured.err
    assert captured.err.count("\n") == 1
