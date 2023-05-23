import pytest

from mm_utils.utils.timeutils import timedelta_from_string as tdfs

# TODO go to full coverage - it's not hard it's just super tedious :D

_UNITS = {"w", "d", "h", "s", "ms", "us"}


def test_basic():
    assert tdfs("1w") == tdfs("7d")
    assert tdfs("1d") == tdfs("24h")
    assert tdfs("1h") == tdfs("60m")
    assert tdfs("1m") == tdfs("60s")
    assert tdfs("1s") == tdfs("1000ms")
    assert tdfs("1ms") == tdfs("1000us")


def test_spaced():
    assert tdfs("1d   30m 20s") == tdfs("1d30m20s")


def test_fractions():
    assert tdfs("0.5ms") == tdfs("500us")
    assert tdfs("0.5s") == tdfs("500ms")
    assert tdfs("0.5m") == tdfs("30s")
    assert tdfs("0.5h") == tdfs("30m")
    assert tdfs("0.5d") == tdfs("12h")


def test_ordering():
    assert tdfs("1w") > tdfs("1d")
    assert tdfs("1d") > tdfs("1h")
    assert tdfs("1h") > tdfs("1m")
    assert tdfs("1m") > tdfs("1s")
    assert tdfs("1s") > tdfs("1ms")
    assert tdfs("1ms") > tdfs("1us")


@pytest.mark.parametrize("unit", _UNITS - {"us"})
def test_fractional_ordering(unit):
    assert tdfs(f"0.9{unit}") > tdfs(f"0.5{unit}") > tdfs(f"0.01{unit}")


def test_longform():
    assert tdfs("1week") == tdfs("1w")
    assert tdfs("2weeks") == tdfs("2w")
    assert tdfs("1day") == tdfs("1d")
    assert tdfs("2days") == tdfs("2d")
    assert tdfs("1hour") == tdfs("1h")
    assert tdfs("2hours") == tdfs("2h")
    assert tdfs("1minute") == tdfs("1m")
    assert tdfs("2minutes") == tdfs("2m")
    assert tdfs("1second") == tdfs("1s")
    assert tdfs("2seconds") == tdfs("2s")
    assert tdfs("1millisecond") == tdfs("1ms")
    assert tdfs("2milliseconds") == tdfs("2ms")
    assert tdfs("1microsecond") == tdfs("1us")
    assert tdfs("2microseconds") == tdfs("2us")


@pytest.mark.parametrize("bad_format", ["1d1d", "1d30m1d", "1y"])
def test_bad_format(bad_format):
    with pytest.raises(ValueError):
        tdfs(bad_format)


@pytest.mark.parametrize("unit", _UNITS)
def test_unitless(unit):
    assert tdfs("1", unit) == tdfs(f"1{unit}")


def test_bad_unitless():
    with pytest.raises(ValueError):
        tdfs("1h30")
