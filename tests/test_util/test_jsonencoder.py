import json

import pytest

from loggia.stdlib_formatters.json_formatter import CustomJsonEncoder, JsonSerializable


def test_json_dunder_ok():
    class JsonEncodable:
        def __json__(self) -> str:
            return "ok"

    output = json.dumps(JsonEncodable(), cls=CustomJsonEncoder)
    assert output == "ok"


# We skip this because it's ahead of its time. We could revisit with
# either homegrown checking, or better support from standard library.
#
# python/3.11.3/lib/python3.11/typing.py:2223 (runtime_checkable)
# > Warning: this will check only the presence of the required methods,
# > not their type signatures!
@pytest.mark.skip("ahead of its time")
def test_json_dunder_ko_type():
    class JsonEncodable:
        def __json__(self) -> int:
            return 1

    if isinstance(JsonEncodable(), JsonSerializable):
        raise RuntimeError("This should not be true")
    output = json.dumps(JsonEncodable(), cls=CustomJsonEncoder)
    assert output == "ok"
