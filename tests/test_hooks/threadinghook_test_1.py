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
    sys.stderr.write("TEST FAILURE: LOGGIA HOOK NOT CALLED\n")
    sys.exit(2)


def thread_start():
    raise RuntimeError("thread unhandled exception")


class VerySpecificError(RuntimeError):
    pass


if __name__ == "__main__":
    threading.excepthook = baseline_hook
    lc = LoggerConfiguration()
    lc.set_excepthook(enabled=False)
    lc.set_threading_excepthook(enabled=True)
    initialize(lc)
    t = threading.Thread(target=thread_start)
    t.start()
    t.join()
