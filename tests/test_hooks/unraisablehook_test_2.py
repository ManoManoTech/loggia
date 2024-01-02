"""
This is meant to be called from tests as a subprocess ... this is the cleanest
way to dodge the several layers of pytest who prevent us from testing the various
exception hooks.
"""
import sys

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize


def baseline_hook(*_args, **_kwargs):
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


class BrokenDel:
    def __del__(self):
        raise ValueError("del is broken")


if __name__ == "__main__":
    sys.unraisablehook = baseline_hook
    lc = LoggerConfiguration(presets=["dev"])
    lc.set_excepthook(enabled=False)
    lc.set_unraisablehook(enabled=False)
    initialize(lc)

    # Unraisable sample courtesy Victor Stinner
    # https://vstinner.github.io/sys-unraisablehook-python38.html
    obj = BrokenDel()
    del obj
