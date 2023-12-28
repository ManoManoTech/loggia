import pytest

from loggia.utils.envutils import with_env


def test_usage_preset_env(capsys: pytest.CaptureFixture[str]) -> None:
    # <!-- DOC:START -->
    # We're forcing the `dev` preset to fill the `main` slot
    with_env("LOGGIA_PRESETS", "dev")

    from loggia.logger import initialize

    initialize()

    import logging

    logging.getLogger("test").warning("hello from logging", extra={"with_extra": "100% yes!"})  # Will show up colored
    # <!-- DOC:END -->

    captured = capsys.readouterr()
    assert "hello from logging" in captured.err
    assert "WARN" in captured.err
    assert "\x1b[0m" in captured.err
