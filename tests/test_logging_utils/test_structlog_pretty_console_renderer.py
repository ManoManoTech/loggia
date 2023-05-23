import re
from unittest.mock import MagicMock

import pytest

from mm_utils.logging_utils.structlog_utils.pretty_console_renderer import COLORS, PALETTES, PrettyConsoleRenderer, html_to_triple_dec


def remove_color_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)


def test_html_to_triple_dec():
    assert html_to_triple_dec("#FF00FF") == [255, 0, 255]
    assert html_to_triple_dec("#123456") == [18, 52, 86]
    assert html_to_triple_dec("#FFFFFF") == [255, 255, 255]


def test_COLORS():
    assert isinstance(COLORS, dict)
    assert all(len(k) > 0 and len(v) == 7 for k, v in COLORS.items())


def test_PALETTES():
    assert isinstance(PALETTES, dict)
    assert all(isinstance(k, int) for k in PALETTES.keys())
    assert all(len(v) == 4 for v in PALETTES.values())


@pytest.fixture
def renderer():
    return PrettyConsoleRenderer()


@pytest.fixture
def event_dict():
    return {
        "event": "test_event",
        "logger": "test_logger",
        "level": "info",
        "timestamp": "2023-04-22T12:00:00",
    }


class TestPrettyConsoleRenderer:
    def test_pretty_console_renderer(self, renderer, event_dict):
        rendered = renderer(None, None, event_dict)
        rendered_no_color = remove_color_codes(rendered)
        assert "test_event" in rendered_no_color
        assert "test_logger" in rendered_no_color
        assert "2023-04-22T12:00:00" in rendered_no_color
        assert "INFO" in rendered_no_color

    def test_pretty_console_renderer_exc_info(self, renderer, event_dict):
        try:
            1 / 0
        except ZeroDivisionError:
            event_dict["exc_info"] = True
            rendered = renderer(None, None, event_dict)
            rendered_no_color = remove_color_codes(rendered)
            assert "ZeroDivisionError" in rendered_no_color
            assert "Traceback" in rendered_no_color
            assert "1 / 0" in rendered_no_color

    # def test_pretty_console_renderer_custom_level_styles(renderer, event_dict):
    #     level_styles = _PlainStyles()
    #     level_styles.level_info = "CUSTOM_STYLE"
    #     renderer = PrettyConsoleRenderer(level_styles=level_styles)
    #     rendered = renderer(None, None, event_dict)
    #     rendered_no_color = remove_color_codes(rendered)
    #     assert "CUSTOM_STYLE" in rendered_no_color
    #     assert "INFO" in rendered_no_color

    def test_pretty_console_renderer_basic(self, renderer, event_dict):
        logger = MagicMock()
        event_dict["event"] = "Hello, World!"
        name = "test"

        result = renderer(logger, name, event_dict)

        assert "2023-04-22T12:00:00" in result
        assert "INFO" in result
        assert "test" in result
        assert "Hello, World!" in result

    def test_pretty_console_renderer_with_custom_event_key(self):
        renderer = PrettyConsoleRenderer(event_key="custom_event")

        event_dict = {
            "timestamp": "2023-04-22T12:00:00",
            "level": "info",
            "logger": "test_logger",
            "custom_event": "Hello, World!",
        }

        logger = MagicMock()
        name = "test"

        result = renderer(logger, name, event_dict)

        assert "2023-04-22T12:00:00" in result
        assert "INFO" in result
        assert "test_logger" in result
        assert "Hello, World!" in result

    def test_pretty_console_renderer_with_key_values(self, renderer, event_dict):
        logger = MagicMock()
        name = "test"
        event_dict = {**event_dict, "key1": "value1", "key2": "value2", "event": "Hello, World!"}

        result = renderer(logger, name, event_dict)
        result_no_color = remove_color_codes(result)

        assert "2023-04-22T12:00:00" in result
        assert "INFO" in result
        assert "test_logger" in result
        assert "Hello, World!" in result
        assert "key1=value1" in result_no_color
        assert "key2=value2" in result_no_color

    # def test_pretty_console_renderer_with_exception():
    #     renderer = PrettyConsoleRenderer()

    #     exc_info = None
    #     try:
    #         1 / 0
    #     except ZeroDivisionError as exc:
    #         exc_info = sys.exc_info()

    #     event_dict = {
    #         "timestamp": "2023-04-22T10:00:00",
    #         "level": "error",
    #         "logger": "test",
    #         "event": "An exception occurred",
    #         "exc_info": exc_info,
    #     }

    #     logger = MagicMock()
    #     name = "test"

    #     result = renderer(logger, name, event_dict)

    #     assert "2023-04-22T10:00:00" in result
    #     assert "ERROR" in result
    #     assert "test" in result
    #     assert "An exception occurred" in result
    #     assert "ZeroDivisionError" in result
    #     assert "1 / 0" in result

    def test_pretty_console_renderer_no_colors(self, renderer, event_dict):
        renderer = PrettyConsoleRenderer(colors=False)
        rendered = renderer(None, None, event_dict)
        assert "test_event" in rendered
        assert "test_logger" in rendered
        assert "2023-04-22T12:00:00" in rendered
        assert "INFO" in rendered
        assert not any(color_code in rendered for color_code in COLORS.values())
