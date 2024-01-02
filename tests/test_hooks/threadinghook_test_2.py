"""
This is meant to be called from tests as a subprocess ... this is the cleanest
way to dodge the several layers of pytest who prevent us from testing the various
exception hooks.
"""

import sys
import threading

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize


def baseline_hook(*args, **kwargs):
    sys.stderr.write("boom\n")
    # sys.exit() doesn't work here
    import ctypes

    system = sys.platform
    if system == "win32":
        libc = ctypes.CDLL("msvcrt.dll")
    elif system == "darwin":
        libc = ctypes.CDLL("libc.dylib")
    else:
        libc = ctypes.CDLL("libc.so.6")

    libc.exit(10)


def thread_start():
    raise RuntimeError("thread unhandled exception")


class VerySpecificError(RuntimeError):
    pass


if __name__ == "__main__":
    threading.excepthook = baseline_hook
    lc = LoggerConfiguration()
    lc.set_excepthook(enabled=False)
    lc.set_threading_excepthook(enabled=False)
    initialize(lc)
    t = threading.Thread(target=thread_start)
    t.start()
    t.join()
