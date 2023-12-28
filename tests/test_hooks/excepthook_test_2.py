"""
This is meant to be called from tests as a subprocess ... this is the cleanest
way to dodge the several layers of pytest who prevent us from testing the various
exception hooks.
"""

import sys

from loggia.logger import initialize
from loggia.conf import LoggerConfiguration


def baseline_hook(*_args, **_kwargs):
    sys.stderr.write("boom\n")
    sys.exit(10)


class VerySpecificError(RuntimeError):
    pass


if __name__ == "__main__":
    sys.excepthook = baseline_hook
    lc = LoggerConfiguration()
    lc.set_excepthook(enabled=False)
    initialize(lc)
    try:
        raise RuntimeError("test unhandled exception")
    except VerySpecificError:
        pass

