from loggia.constants import COLORS, PALETTES
from loggia.utils.colorsutils import html_to_triple_dec

# pyright: reportUnusedExpression=false


def test_html_to_triple_dec():
    assert html_to_triple_dec("#FF00FF") == (255, 0, 255)
    assert html_to_triple_dec("#123456") == (18, 52, 86)
    assert html_to_triple_dec("#FFFFFF") == (255, 255, 255)


def test_COLORS():
    assert isinstance(COLORS, dict)
    assert all(len(k) > 0 and len(v) == 7 for k, v in COLORS.items())


def test_PALETTES():
    assert isinstance(PALETTES, dict)
    assert all(isinstance(k, int) for k in PALETTES)
    assert all(len(v) == 4 for v in PALETTES.values())
