import pytest


def test_usage_custom_params(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->
    # Setup

    from loggia.logger import initialize
    from loggia.conf import LoggerConfiguration

    # Prepare a configuration
    # Here, debug_show_config will be ignored because it's not a boolean!
    log_config = LoggerConfiguration()
    log_config.set_default_formatter("structured")  # This is already the default
    log_config.set_general_level(5)  # This is the numerical level for 'TRACE'

    initialize(log_config)

    # Use just like the standard logger
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Hello world!")

    logger.log(5, "Hello trace")  # Sending a trace with typings OK
    # <!-- DOC:END -->

    # XXX caplog
    captured = capsys.readouterr()
    assert '"message": "Hello world!"' in captured.err

    # Assert we can parse JSON lines
    import json

    # Split the lines
    lines = captured.err.split("\n")
    # Remove the last empty line
    lines.pop()
    # Parse each line
    messages: list[str] = []
    for line in lines:
        parsed_line = json.loads(line)
        assert "logger.name" in parsed_line
        assert "status" in parsed_line
        assert "message" in parsed_line
        messages.append(parsed_line["message"])


    assert "Hello world!" in messages
    assert "Hello trace" in messages
