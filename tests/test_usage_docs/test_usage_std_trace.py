import pytest

# Skip if loguru is not present:
# # We try to import loguru
loguru_module = pytest.importorskip("loguru")


# ruff: noqa: F811
def test_trace_with_standard(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->
    # Assuming we want a very verbose logger
    import os

    os.environ["LOGGIA_LEVEL"] = "TRACE"

    # Setup
    from loggia.logger import initialize

    initialize(conf={"LOGGIA_CAPTURE_LOGURU": "True"})

    # Use standard logger
    import logging

    logger = logging.getLogger()

    # Use the added trace level
    logger.log(level=5, msg="Hello trace from the std_lib!")
    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "Hello trace from the std_lib!" in captured.err
