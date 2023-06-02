"""
Helpers that make development with *structlog* more pleasant.

See also the narrative documentation in `development`.
"""
from __future__ import annotations

import logging
import warnings
from collections.abc import Iterable
from io import StringIO
from typing import TYPE_CHECKING

from structlog.dev import _EVENT_WIDTH, ConsoleRenderer, Styles, _has_colors, _pad, default_exception_formatter, plain_traceback
from structlog.processors import _figure_out_exc_info

from mm_utils.logging_utils.colors import PALETTES, ansi_fg

if TYPE_CHECKING:
    from structlog.typing import EventDict, ExceptionRenderer, WrappedLogger

_ansi_fg = ansi_fg


try:
    import colorama
except ImportError:
    colorama = None

try:
    import rich
except ImportError:
    rich = None  # type: ignore[assignment]


if colorama is not None:
    RESET_ALL = colorama.Style.RESET_ALL
    BRIGHT = colorama.Style.BRIGHT
    DIM = colorama.Style.DIM
    RED = colorama.Fore.RED
    BLUE = colorama.Fore.BLUE
    CYAN = colorama.Fore.CYAN
    MAGENTA = colorama.Fore.MAGENTA
    YELLOW = colorama.Fore.YELLOW
    GREEN = colorama.Fore.GREEN
    RED_BACK = colorama.Back.RED
else:
    # These are the same values as the Colorama color codes. Redefining them
    # here allows users to specify that they want color without having to
    # install Colorama, which is only supposed to be necessary in Windows.
    RESET_ALL = "\033[0m"
    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    RED_BACK = "\033[41m"


class PrettyConsoleRenderer(ConsoleRenderer):
    """
    Adapted from structlog.dev.ConsoleRenderer.

    Render ``event_dict`` nicely aligned, possibly in colors, and ordered.

    If ``event_dict`` contains a true-ish ``exc_info`` key, it will be
    rendered *after* the log line. If Rich_ or better-exceptions_ are present,
    in colors and with extra context.

    :param pad_event: Pad the event to this many characters.
    :param colors: Use colors for a nicer output. `True` by default. On
        Windows only if Colorama_ is installed.
    :param force_colors: Force colors even for non-tty destinations.
        Use this option if your logs are stored in a file that is meant
        to be streamed to the console. Only meaningful on Windows.
    :param repr_native_str: When `True`, `repr` is also applied
        to native strings (i.e. unicode on Python 3 and bytes on Python 2).
        Setting this to `False` is useful if you want to have human-readable
        non-ASCII output on Python 2.  The ``event`` key is *never*
        `repr` -ed.
    :param level_styles: When present, use these styles for colors. This
        must be a dict from level names (strings) to Colorama styles. The
        default can be obtained by calling
        `ConsoleRenderer.get_default_level_styles`
    :param exception_formatter: A callable to render ``exc_infos``. If rich_
        or better-exceptions_ are installed, they are used for pretty-printing
        by default (rich_ taking precedence). You can also manually set it to
        `plain_traceback`, `better_traceback`, `rich_traceback`, or implement
        your own.
    :param sort_keys: Whether to sort keys when formatting. `True` by default.
    :param event_key: The key to look for the main log message. Needed when
        you rename it e.g. using `structlog.processors.EventRenamer`.

    Requires the Colorama_ package if *colors* is `True` **on Windows**.

    .. _Colorama: https://pypi.org/project/colorama/
    .. _better-exceptions: https://pypi.org/project/better-exceptions/
    .. _Rich: https://pypi.org/project/rich/
    """

    def __init__(
        self,
        pad_event: int = _EVENT_WIDTH,
        colors: bool = _has_colors,
        force_colors: bool = False,
        repr_native_str: bool = False,
        level_styles: Styles | None = None,
        exception_formatter: ExceptionRenderer = default_exception_formatter,
        sort_keys: bool = True,
        event_key: str = "event",
    ):
        super().__init__(pad_event, colors, force_colors, repr_native_str, level_styles, exception_formatter, sort_keys, event_key)

        self.palettes: dict[int, list[str]] = {}
        for pal_level, pal_colors in PALETTES.items():
            self.palettes[pal_level] = [_ansi_fg(color) for color in pal_colors]

    def __call__(self, logger: WrappedLogger, name: str, event_dict: EventDict) -> str:
        sio = StringIO()

        log_level_number: int = event_dict.pop("level_number", logging.getLevelName(event_dict.get("level", "notset").upper()))
        palette = self.palettes.get(log_level_number, self.palettes[logging.NOTSET])

        ts = event_dict.pop("timestamp", None)
        if ts is not None:
            sio.write(
                # can be a number if timestamp is UNIXy
                palette[0]
                + str(ts)
                + self._styles.reset
                + " "
            )
        level = event_dict.pop("level", None)
        if level is not None:
            sio.write(palette[1] + _pad(level.upper(), self._longest_level) + self._styles.reset + " ")

        logger_name = event_dict.pop("logger", None)
        if logger_name is None:
            logger_name = event_dict.pop("logger_name", None)

        if logger_name is not None:
            sio.write(palette[2] + self._styles.bright + logger_name + self._styles.reset)
        lineno = event_dict.pop("lineno", None)
        if lineno is not None:
            sio.write(palette[2] + self._styles.bright + ":" + str(lineno) + self._styles.reset + " ")
        else:
            sio.write(" ")

        # force event to str for compatibility with standard library
        event = event_dict.pop(self._event_key, None)
        if not isinstance(event, str):
            event = str(event)

        if event_dict:
            event = _pad(event, self._pad_event) + self._styles.reset + " "
        else:
            event += self._styles.reset
        sio.write(palette[3] + event)

        stack = event_dict.pop("stack", None)
        exc = event_dict.pop("exception", None)
        exc_info = event_dict.pop("exc_info", None)

        event_dict_keys: Iterable[str] = event_dict.keys()
        if self._sort_keys:
            event_dict_keys = sorted(event_dict_keys)
        if event_dict_keys:
            sio.write(
                "\n  "
                + "\n  ".join(
                    palette[2] + key + self._styles.reset + "=" + palette[3] + self._repr(event_dict[key]) + self._styles.reset
                    for key in event_dict_keys
                )
            )

        if stack is not None:
            sio.write("\n" + stack)
            if exc_info or exc is not None:
                sio.write("\n\n" + "=" * 79 + "\n")

        if exc_info:
            exc_info = _figure_out_exc_info(exc_info)

            self._exception_formatter(sio, exc_info)
        elif exc is not None:
            if self._exception_formatter is not plain_traceback:
                warnings.warn(
                    "Remove `format_exc_info` from your processor chain " "if you want pretty exceptions.",
                    stacklevel=2,
                )
            sio.write("\n" + exc)

        return sio.getvalue()
