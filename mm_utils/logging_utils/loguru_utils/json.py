import json
import re
from types import _T_contra
from typing import Any, Protocol
from uuid import UUID


class SupportsWrite(Protocol[_T_contra]):
    def write(self, __s: _T_contra) -> object:
        ...


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> str | Any:  # pylint: disable=too-many-return-statements
        if hasattr(o, "__json__"):
            return o.__json__()
        if hasattr(o, "isoformat") and callable(o.isoformat):
            return o.isoformat()  # datetime and similar
        if isinstance(o, re.Match):  # XXX should be refactored into models.core.RegexMatch(models.core.Match)
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
            # XXX: Should we warn on this? It's a bit pointless to serialize :/
            return o.__qualname__
        if hasattr(o, "__dataclass_fields__"):
            return o.__dict__
        return super().encode(o)


class ShortJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "__short_json__"):
            return o.__short_json__()
        return super().default(o)


def dump(obj: Any, fp: SupportsWrite[str], **kwargs: Any) -> None:
    return json.dump(obj, fp, cls=JSONEncoder, **kwargs)


def dumps(obj: Any, **kwargs: Any) -> str:
    return json.dumps(obj, cls=JSONEncoder, **kwargs)
