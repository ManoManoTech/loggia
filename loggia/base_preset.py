from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loggia._internal.conf import EnvironmentLoader
    from loggia.conf import LoggerConfiguration


class BasePreset(ABC):
    """Base class for Loggia Presets.

    Loggia presets are a very thin abstraction that allow bundling of settings
    that address a similar concern.
    """
    @abstractmethod
    def apply(self, conf: LoggerConfiguration) -> None:
        ...

    def slots(self) -> list[str]:
        """Override the slots method to indicate mutually incompatible presets.

        Mutually incompatible presets should have at least one slot in common.
        Slots have otherwise no use inside Loggia, but should roughly map to a
        single concern.
        """
        return []

    @classmethod
    def env_loader(cls) -> EnvironmentLoader | None:
        return None
