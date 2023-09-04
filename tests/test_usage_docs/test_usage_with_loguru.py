import pytest


# ruff: noqa: F811
def test_usage_with_loguru(capsys: pytest.CaptureFixture[str]):
    # NB: We keep the 'import loguru' below
    loguru = pytest.importorskip("loguru")

    from loggia._internal.loguru_stuff import _unblock_loguru_reconfiguration

    # If another test did not properly teardown, we need to unblock loguru
    _unblock_loguru_reconfiguration()
    # <!-- DOC:START -->
    # Setup
    from loggia.logger import initialize

    initialize()

    # Use loguru
    import loguru

    loguru.logger.info("Hello world loguru!")

    # Using standard logger should still work uniformly
    import logging

    logger = logging.getLogger()
    logger.info("Hello world std_lib!")
    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "Hello world std_lib!" in captured.err
    assert "Hello world loguru!" in captured.err
