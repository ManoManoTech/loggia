import pytest


def test_usage_custom_config(capsys: pytest.CaptureFixture[str]) -> None:
    # <!-- DOC:START -->
    # Setup
    from mm_logger.logger import initialize
    from mm_logger.conf import LoggerConfiguration

    # Force colored logging, even if environment variables is set
    log_config = LoggerConfiguration({
        "MM_LOGGER_FORCE_LEVEL": "test.warn_only:WARNING",
        "MM_LOGGER_FORMATTER": "pretty",
    })
    initialize(log_config)

    ## Use just like the standard logger
    import logging

    logger = logging.getLogger("test")
    logger.info("Hello world first!")
    logger = logging.getLogger("test.warn_only")
    logger.info("Hello world bis is not shown")
    logger.warning("Warning are shown")
    # <!-- DOC:END -->

    # XXX try to use caplog instead
    captured = capsys.readouterr()
    assert "Hello world first!" in captured.err
    assert "Hello world bis is not shown" not in captured.err
    assert "Warning are shown" in captured.err
