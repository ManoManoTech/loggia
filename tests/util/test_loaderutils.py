import pytest

from mm_utils.utils.loaderutils import resolve_type_string


def test_resolve_type_string():
    result = resolve_type_string("str")

    assert result
    assert result.__qualname__ == "str"
    assert result.__class__.__name__ == "type"


def test_resolve_type_string_wrong_type():
    with pytest.raises(ValueError):
        _ = resolve_type_string("wrong_type")
