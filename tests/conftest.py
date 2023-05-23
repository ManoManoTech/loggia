import logging
import os

import pytest
from _pytest.logging import caplog  # pylint: disable=unused-import

# from mm_utils.logging_utils.loguru_conf import loguru_extra_levels

# from click.testing import CliRunner


STUB_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "radiologist-stubs")


os.environ["ENV"] = "test"
