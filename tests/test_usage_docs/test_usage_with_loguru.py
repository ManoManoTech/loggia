import pytest


# ruff: noqa: F811
def test_usage_with_loguru(capsys: pytest.CaptureFixture[str]):
    import loguru

    from mm_logger.loguru_sink import _unblock_loguru_reconfiguration

    # If another test did not properly teardown, we need to unblock loguru
    _unblock_loguru_reconfiguration()
    # <!-- DOC:START -->
    # Setup
    from mm_logger.logger import initialize

    # Force colored logging, even if environment variables is set
    initialize({"MM_LOGGER_FORMATTER": "pretty"})

    # Use standard logger
    import logging

    logger = logging.getLogger()
    logger.info("Hello world std_lib!")

    # Use loguru
    import loguru

    loguru.logger.info("Hello world loguru!")
    # <!-- DOC:END -->

    captured = capsys.readouterr()

    assert "Hello world std_lib!" in captured.err
    assert "Hello world loguru!" in captured.err
