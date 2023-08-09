import pytest


def test_usage_custom_params(capsys: pytest.CaptureFixture[str]):
    # <!-- DOC:START -->
    # Setup

    from mm_logger.logger import configure_logging
    from mm_logger.settings import MMLogsConfig

    # Prepare a configuration
    # Here, debug_show_config will be ignored because it's not a boolean!
    log_config = MMLogsConfig(env="special_env", debug_show_config="invalid_should_be_bool")
    log_config.log_formatter_name = "structured"
    log_config.log_level = 5
    log_config.debug_check_duplicate_processors = True

    configure_logging(log_config)

    # Use just like the standard logger
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Hello world!")
    # <!-- DOC:END -->

    assert log_config.env == "special_env"
    assert log_config.debug_show_config is False  # Default is used instead
    assert log_config.debug_check_duplicate_processors is True
    assert len(log_config._configuration_errors) == 1
    assert log_config._configuration_errors[0].field_name == "debug_show_config"

    captured = capsys.readouterr()
    assert '"logger.name":"test_usage_custom_params"' in captured.err
    assert '"message":"Hello world!"' in captured.err

    # Assert we can parse JSON lines
    import json

    # Split the lines
    lines = captured.err.split("\n")
    # Remove the last empty line
    lines.pop()
    # Parse each line
    for line in lines:
        json.loads(line)
        assert "logger.name" in line
        assert "status" in line
        assert "message" in line
