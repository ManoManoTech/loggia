from __future__ import annotations

import pytest

from loggia.utils.envutils import with_env
from tests.test_preset import TestPreset


class TestA(TestPreset):
    ...


class TestB(TestPreset):
    ...


class TestC(TestPreset):
    ...


class TestNeedsA1(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["TestA"]]


class TestNeedsA2(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["test_a"]]


class TestAnB(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["test_a", "test_b"]]


class TestAoB(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return ["TestA", "TestB"]


class TestAnBnC1(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["TestAnB", "TestC"]]


class TestAnBnC2(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["TestA", "TestB", "TestC"]]


class TestAnBoC1(TestPreset):
    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        return [["TestA", "TestB"], "TestC"]


def _lp(*suffixes: str):
    """Generates a suitable string for LOGGIA_PRESETS from the suffix only.
    Makes tests much more legible."""
    return ",".join(f"tests.test_presets.test_requirements.Test{suffix[1:]}" if suffix.startswith("*") else suffix for suffix in suffixes)


@pytest.fixture(autouse=True)
def _clear_test_applies():
    try:
        yield
    finally:
        TestPreset.APPLICATIONS.clear()


def test_needs_a1_met():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*NeedsA1"))
    import loggia.auto  # noqa: F401

    assert {"A", "NeedsA1"} == TestPreset.APPLICATIONS


def test_needs_a1_unmet():
    with_env("LOGGIA_PRESETS", _lp("prod", "*NeedsA1"))
    import loggia.auto  # noqa: F401

    assert set() == TestPreset.APPLICATIONS


def test_needs_a2_met():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*NeedsA2"))
    import loggia.auto  # noqa: F401

    assert {"A", "NeedsA2"} == TestPreset.APPLICATIONS


def test_needs_a2_unmet():
    with_env("LOGGIA_PRESETS", _lp("prod", "*NeedsA2"))
    import loggia.auto  # noqa: F401

    assert set() == TestPreset.APPLICATIONS


def test_a_or_b_met1():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*B", "*AoB"))
    import loggia.auto  # noqa: F401

    assert {"A", "B", "AoB"} == TestPreset.APPLICATIONS


def test_a_or_b_met2():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*AoB"))
    import loggia.auto  # noqa: F401

    assert {"A", "AoB"} == TestPreset.APPLICATIONS


def test_a_or_b_met3():
    with_env("LOGGIA_PRESETS", _lp("prod", "*B", "*AoB"))
    import loggia.auto  # noqa: F401

    assert {"B", "AoB"} == TestPreset.APPLICATIONS


def test_a_or_b_unmet():
    with_env("LOGGIA_PRESETS", _lp("prod", "*C", "*AoB"))
    import loggia.auto  # noqa: F401

    assert {"C"} == TestPreset.APPLICATIONS


def test_a_and_b_unmet_1():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*AnB"))
    import loggia.auto  # noqa: F401

    assert {"A"} == TestPreset.APPLICATIONS


def test_a_and_b_unmet_2():
    with_env("LOGGIA_PRESETS", _lp("prod", "*B", "*AnB"))
    import loggia.auto  # noqa: F401

    assert {"B"} == TestPreset.APPLICATIONS


# NB: This test is the only one that makes the topological sort ~necessary (even though you could get lucky on set iteration...)
def test_anbnc1_met():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*B", "*C", "*AnB", "*AnBnC1"))
    import loggia.auto  # noqa: F401

    assert {"A", "B", "C", "AnB", "AnBnC1"} == TestPreset.APPLICATIONS


def test_anbnc2_met():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*B", "*C", "*AnBnC2"))
    import loggia.auto  # noqa: F401

    assert {"A", "B", "C", "AnBnC2"} == TestPreset.APPLICATIONS


def test_anboc1_met1():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*B", "*AnBoC1"))
    import loggia.auto  # noqa: F401

    assert {"A", "B", "AnBoC1"} == TestPreset.APPLICATIONS


def test_anboc1_met2():
    with_env("LOGGIA_PRESETS", _lp("prod", "*C", "*AnBoC1"))
    import loggia.auto  # noqa: F401

    assert {"C", "AnBoC1"} == TestPreset.APPLICATIONS


def test_anboc1_unmet():
    with_env("LOGGIA_PRESETS", _lp("prod", "*A", "*AnBoC1"))
    import loggia.auto  # noqa: F401

    assert {"A"} == TestPreset.APPLICATIONS
