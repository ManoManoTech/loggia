import os

from loggia.conf import LoggerConfiguration as LC
from loggia.constants import BASE_DICTCONFIG

# Let's first define the setup and teardown for the tests


def test_log_level_setting():
    conf = LC()
    conf.set_logger_level("numba", "WARNING")
    conf.set_general_level("CRITICAL")
    assert conf._dictconfig["loggers"][""]["level"] == "CRITICAL"
    assert conf._dictconfig["loggers"]["numba"]["level"] == "WARNING"
    assert "numba" not in BASE_DICTCONFIG["loggers"], "deepcopy wasnt done"


def test_log_level_setting_through_env():
    try:
        os.environ["LOGGIA_LEVEL"] = "CRITICAL"
        os.environ["LOGGIA_SUB_LEVEL"] = "numba:WARNING,numpy:DEBUG"
        conf = LC()
        assert conf._dictconfig["loggers"][""]["level"] == "CRITICAL"
        assert conf._dictconfig["loggers"]["numba"]["level"] == "WARNING"
        assert conf._dictconfig["loggers"]["numpy"]["level"] == "DEBUG"
        assert "numba" not in BASE_DICTCONFIG["loggers"], "deepcopy wasnt done"
    finally:
        del os.environ["LOGGIA_LEVEL"]
        del os.environ["LOGGIA_SUB_LEVEL"]
