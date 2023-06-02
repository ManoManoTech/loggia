import re
from datetime import timedelta
from functools import reduce
from typing import Final

__re: Final[re.Pattern[str]] = re.compile(
    r"""
        ^
        (?:(?P<weeks>-?[0-9]+(\.[0-9]+)?)(w|weeks?))?                   \ *
        (?:(?P<days>-?[0-9]+(\.[0-9]+)?)(d|days?))?                     \ *
        (?:(?P<hours>-?[0-9]+(\.[0-9]+)?)(h|hours?))?                   \ *
        (?:(?P<minutes>-?[0-9]+(\.[0-9]+)?)(m|minutes?))?               \ *
        (?:(?P<seconds>-?[0-9]+(\.[0-9]+)?)(s|seconds?))?               \ *
        (?:(?P<microseconds>-?[0-9]+(\.[0-9]+)?)(us|microseconds?))?    \ *
        (?:(?P<milliseconds>-?[0-9]+(\.[0-9]+)?)(ms|milliseconds?))?    \ *
        (?P<unitless>-?[0-9]+(\.[0-9]+)?)?
        $
        """,
    re.X,
)


__assumable_units_roots: set[str] = {"week", "day", "hour", "minute", "second", "microsecond", "millisecond"}
__assumable_units_keys = [(au, au[0], f"{au}s") for au in __assumable_units_roots]
__assumable_units: dict[str, str] = reduce(lambda m, e: m | {e[0]: e[2], e[1]: e[2], e[2]: e[2]}, __assumable_units_keys, {})
__assumable_units |= {"m": "minutes", "ms": "milliseconds", "us": "microseconds"}


def timedelta_from_string(input: str, assumed_unit: str = "s") -> timedelta:
    """Parse a human readable duration string and return a timedelta object.

    Args:
        input (str): The string to parse. For example: "1d 2h 3m 4s", or "1.5h".
        assumed_unit (str, optional): The unit to use if the string doesn't contain any unit. Defaults to "s".

    Raises:
        ValueError: If the string doesn't look like a valid duration string. For example: "1h30".

    Returns:
        timedelta: The parsed timedelta object.
    """
    if assumed_unit not in __assumable_units:
        raise ValueError(f"assumed_unit='{assumed_unit}' is invalid. valid choices: {list(__assumable_units.keys())}")
    assumed_unit = __assumable_units[assumed_unit]

    match = __re.match(input)
    if not match:
        raise ValueError(f"the string '{input}' doesn't look like a valid duration string.")
    mdict = {k: float(v) for k, v in match.groupdict().items() if v}
    set_items = set(mdict.keys())

    if "unitless" in set_items:
        if len(set_items) > 1:
            raise ValueError(f"cannot mix suffixed and unsuffixed values in duration string '{input}'. Valid: 1h30m or 30; Invalid: 1h30")
        kwargs = {assumed_unit: mdict["unitless"]}
    else:
        kwargs = mdict
    return timedelta(**kwargs)
