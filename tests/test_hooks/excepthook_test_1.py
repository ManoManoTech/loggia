"""
This is meant to be called from tests as a subprocess ... this is the cleanest
way to dodge the several layers of pytest who prevent us from testing the various
exception hooks.
"""

import sys

from loggia.conf import LoggerConfiguration
from loggia.logger import initialize


def baseline_hook(*args, **kwargs):
    sys.stderr.write("TEST FAILURE: LOGGIA HOOK NOT CALLED\n")
    sys.exit(2)


class VerySpecificError(RuntimeError):
    pass


if __name__ == "__main__":
    sys.excepthook = baseline_hook
    lc = LoggerConfiguration()
    lc.set_excepthook(enabled=True)
    initialize(lc)
    try:
        raise RuntimeError("test unhandled exception")
    except VerySpecificError:
        pass
