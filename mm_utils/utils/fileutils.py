import sys
from collections.abc import Generator
from contextlib import contextmanager
from io import TextIOWrapper
from typing import AnyStr, TextIO


@contextmanager
def smart_open(filename: AnyStr | None = None, encoding: str = "utf-8") -> Generator[TextIO | TextIOWrapper, None, None]:
    """
    Open a file, and close it when done.
    Can write to [stdout][sys.stdout] if filename is `-` or None.

    Args:
        filename (AnyStr, optional): Filename or `-` for [sys.stdout][]. Defaults to None.
        encoding (str, optional): Defaults to "utf-8".
    """
    if filename and filename != "-":
        fh = open(filename, "w", encoding=encoding)
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()
