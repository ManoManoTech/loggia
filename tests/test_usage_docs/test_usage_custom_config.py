import pytest


def test_usage_custom_config(capsys: pytest.CaptureFixture[str]) -> None:
    # <!-- DOC:START -->
    # Setup
    from mm_logs.logger import configure_logging
    from mm_logs.settings import MMLogsConfig

    # Force colored logging, even if environment variables is set
    log_config = MMLogsConfig(
        custom_stdlib_logging_dict_config={
            "loggers": {
                "test.warn_only": {
                    "level": "WARNING",
                },
            },
        },
    )
    log_config.log_formatter_name = "colored"

    configure_logging(log_config)

    ## Use just like the standard logger
    import logging

    logger = logging.getLogger("test")
    logger.info("Hello world first!")
    logger = logging.getLogger("test.warn_only")
    logger.info("Hello world bis is not shown")
    logger.warning("Warning are shown")
    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "Hello world first!" in captured.err
    assert "Hello world bis is not shown" not in captured.err
    assert "Warning are shown" in captured.err
