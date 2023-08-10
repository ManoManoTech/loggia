"""JSON encoder to use with the standard library logging module."""

import json
import re
from typing import Any
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    """JSON Encoder that can handle some extra types."""

    def default(self, o: Any) -> str | Any:  # pylint: disable=too-many-return-statements # noqa: PLR0911
        if hasattr(o, "__json__"):
            return o.__json__()
        if hasattr(o, "isoformat") and callable(o.isoformat):
            return o.isoformat()  # datetime and similar
        if isinstance(o, re.Match):
            return {
                "match": o.group(),
                "match_spans": [o.span(i) for i in range(len(o.groups()) + 1)],
                "match_type": "regex.Match",
                "matches": o.groups(),
            }
        if isinstance(o, UUID):
            return str(o)
        if hasattr(o, "__module__") and o.__module__ == "loguru._recattrs":
            return str(o)
        # if RESTObject is not None and isinstance(o, Path):
        #     return o.as_posix()
        # if RESTObject and isinstance(o, RESTObject):
        #     return o._attrs  # pylint:disable=protected-access
        if type(o).__name__ == "function":
            # We don't match on callable cause it could catch more than we intend
            return o.__qualname__
        if hasattr(o, "__dataclass_fields__"):
            return o.__dict__
        return super().encode(o)
