"""
This is meant to be called from tests as a subprocess ... this is the cleanest
way to dodge the several layers of pytest who prevent us from testing the various
exception hooks.
"""
import sys

from loggia.logger import initialize
from loggia.conf import LoggerConfiguration


def baseline_hook(*args, **kwargs):
    sys.stderr.write("TEST FAILURE: LOGGIA HOOK NOT CALLED\n")
    sys.exit(2)


class BrokenDel:
    def __del__(self):
        raise ValueError("del is broken")


if __name__ == "__main__":
    sys.unraisablehook = baseline_hook
    lc = LoggerConfiguration()
    lc.set_excepthook(enabled=False)
    lc.set_unraisablehook(enabled=True)
    initialize(lc)

    # Unraisable sample courtesy Victor Stinner
    # https://vstinner.github.io/sys-unraisablehook-python38.html
    obj = BrokenDel()
    del obj
