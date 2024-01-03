from typing import ClassVar

from loggia.base_preset import BasePreset
from loggia.conf import LoggerConfiguration


class TestPreset(BasePreset):
    APPLICATIONS: ClassVar[set[str]] = set()

    def apply(self, conf: LoggerConfiguration) -> None:
        TestPreset.APPLICATIONS.add(self.__class__.__name__.replace("Test", ""))
