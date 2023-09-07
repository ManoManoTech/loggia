import pytest


def test_usage_custom_config(capsys: pytest.CaptureFixture[str]) -> None:
    # <!-- DOC:START -->
    # Setup
    from loggia.conf import LoggerConfiguration
    from loggia.logger import initialize

    # Force colored logging, even if environment variables is set
    log_config = LoggerConfiguration(
        settings={
            "LOGGIA_SUB_LEVEL": "test.warn_only:WARNING",
        },
        presets=["dev"],
    )
    initialize(log_config)

    # Use just like the standard logger
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
