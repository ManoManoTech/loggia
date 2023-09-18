from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from loggia.base_preset import BasePreset
from loggia.presets.dev import Dev
from loggia.utils.envutils import with_env

if TYPE_CHECKING:
    from loggia.conf import LoggerConfiguration
    from tests.conftest import BootstrapLoggerFixture


class TestUnslottedPreset(BasePreset):
    def apply(self, conf: LoggerConfiguration) -> None:
        raise RuntimeError("TestUnslotted")


def test_fqn_unslotted_preset():
    with_env("LOGGIA_PRESETS", "dev,tests.test_presets.test_dynamic_import.TestUnslottedPreset")

    with pytest.raises(RuntimeError, match="TestUnslotted"):
        import loggia.auto  # noqa: F401


class TestSlottedPreset(BasePreset):
    @classmethod
    def slots(cls) -> list[str]:
        return ["newslot"]

    def apply(self, conf: LoggerConfiguration) -> None:
        raise RuntimeError("TestSlotted")


def test_fqn_slotted_preset():
    with_env("LOGGIA_PRESETS", "dev,tests.test_presets.test_dynamic_import.TestSlottedPreset")

    with pytest.raises(RuntimeError, match="TestSlotted"):
        import loggia.auto  # noqa: F401


class DevOverridePreset(Dev):
    def apply(self, conf: LoggerConfiguration) -> None:
        raise RuntimeError("TestDevOverride")


def test_fqn_overriding_preset():
    with_env("LOGGIA_PRESETS", "tests.test_presets.test_dynamic_import.DevOverridePreset")

    with pytest.raises(RuntimeError, match="TestDevOverride"):
        import loggia.auto  # noqa: F401


def test_fqn_overriding_preset_conflicting_preference(capbootstrap: BootstrapLoggerFixture):
    with_env("LOGGIA_PRESETS", "prod, tests.test_presets.test_dynamic_import.DevOverridePreset")

    # This pytest.raises assumes that dev_override_preset is the first preset
    # in the alphanumerically sorted list of presets for that slot
    with pytest.raises(RuntimeError, match="TestDevOverride"):
        import loggia.auto  # noqa: F401

    capbootstrap.assert_one_message()
    assert "ambiguous" in capbootstrap.first_entry.msg
    assert "defaulting to the 'dev_override_preset'" in capbootstrap.first_entry.msg
