"""Text utils, unused."""

import re

_snake_case_re = re.compile(r"(?<!^)(?=[A-Z])")
_clean_alphanumerical_and_separator_re = re.compile(r"[^0-9a-zA-Z\-\_\.\ ]+")


# TODO Fix string in parenthesis
def to_snake_case(s: str) -> str:
    return _snake_case_re.sub("_", s).lower()


def clean_string(s: str, replacement: str = " ") -> str:
    """
    Return a string with only alphanumerical characters, dashes, underscores and dots (`-, _, .`).
    It does NOT remove whitespace and is NOT case sensitive.
    Non-conforming characters are replaced by `replacement`, expect for "&" which are replaced by "and".
    """
    return _clean_alphanumerical_and_separator_re.sub(replacement, s.replace("&", "and"))


def to_kebab_case(s: str, separator: str = " ") -> str:
    return clean_string(s).replace(separator, "-").lower().rstrip("-").replace(" ", "")


def to_snake_case_bis(s: str, separator: str = " ") -> str:
    return clean_string(s).replace(separator, "_").lower().rstrip("_").replace(" ", "")


def to_camel_case(s: str, separator: str = "_") -> str:
    components = clean_string(s, separator).split(separator)
    return (components[0] + "".join(x.title() for x in components[1:])).replace(" ", "")
