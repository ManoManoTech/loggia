from loggia.constants import COLORS


def html_to_triple_dec(html_code: str) -> tuple[int, int, int]:
    """Helper function to convert hexadecimal color codes to decimal RGB color codes."""
    return (int(html_code[1:3], 16), int(html_code[3:5], 16), int(html_code[5:8], 16))


def ansi_fg(name: str) -> str:
    """Helper function to convert hexadecimal color codes to ANSI color codes.

    Args:
        name (str): Name of a color in [COLORS][loggia.constants.COLORS].

    Raises:
        KeyError: If `name` is not a key in [COLORS][loggia.constants.COLORS].

    Returns:
        str: ANSI color code.
    """
    html_code = COLORS[name]
    return "\x1b[38;2;{};{};{}m".format(*html_to_triple_dec(html_code))  # pylint: disable=consider-using-f-string


def ansi_end() -> str:
    """Helper function to reset ANSI color codes."""
    return "\x1b[0m"
