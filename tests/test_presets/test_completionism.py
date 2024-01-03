"""Somewhat stupid tests to have 100% coverage of preset-related things."""
import pytest

from loggia.base_preset import BasePreset


class AbstractTestPreset(BasePreset):
    ...


def test_abc():
    with pytest.raises(TypeError):
        BasePreset()


def test_abc2():
    with pytest.raises(TypeError):
        AbstractTestPreset()
