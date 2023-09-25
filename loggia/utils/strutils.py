"""Text utils, unused."""
from __future__ import annotations

import re

_snake_case_re = re.compile(r"(?<!^)(?=[A-Z])")


# XXX Tests
def to_snake_case(s: str) -> str:
    return _snake_case_re.sub("_", s).lower()
