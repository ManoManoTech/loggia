import pytest

from loggia.utils.envutils import with_env
from tests.conftest import BootstrapLoggerFixture


def test_dual_use_slot(capbootstrap: BootstrapLoggerFixture) -> None:
    # These two presets conflict
    with_env("LOGGIA_PRESETS", "dev,prod")

    import loggia.auto  # noqa: F401

    capbootstrap.assert_one_message()
    assert capbootstrap.first_entry.levelstr == "WARNING"
    assert "ambiguous" in capbootstrap.first_entry.msg


def test_dual_use_slot_again(capbootstrap: BootstrapLoggerFixture) -> None:
    # These two presets conflict
    with_env("LOGGIA_PRESETS", "dev,prod")

    import loggia.auto  # noqa: F401

    capbootstrap.assert_one_message()
    assert capbootstrap.first_entry.levelstr == "WARNING"
    assert "ambiguous" in capbootstrap.first_entry.msg


def test_unknown_preset(caplog: pytest.LogCaptureFixture, capbootstrap: BootstrapLoggerFixture) -> None:
    with_env("LOGGIA_PRESETS", "thisPRESETdoesNOTexist,prod")

    import loggia.auto  # noqa: F401

    capbootstrap.assert_one_message()
    assert capbootstrap.first_entry.levelstr == "ERROR"
    assert "matches no builtin" in capbootstrap.first_entry.msg
    assert "thisPRESETdoesNOTexist" in capbootstrap.first_entry.msg
