import pytest


def test_usage_basic(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->

    # Setup
    from loggia.logger import initialize

    # One-line setup -- get the default config from environment variables
    initialize()

    # Using the standard logger will now benefit from Loggia configuration
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Hello world!")

    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "INFO" in captured.err
    assert "test_usage_basic" in captured.err
    assert "Hello world!" in captured.err
    assert captured.err.count("\n") == 1
