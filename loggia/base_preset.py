from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loggia.utils.strutils import to_snake_case

if TYPE_CHECKING:
    from loggia._internal.conf import EnvironmentLoader
    from loggia.conf import LoggerConfiguration


class BasePreset(ABC):
    """Base class for Loggia Presets.

    Loggia presets are a very thin abstraction that allows bundling of settings
    that address a similar concern.
    """

    @abstractmethod
    def apply(self, conf: LoggerConfiguration) -> None:
        ...

    @classmethod
    def slots(cls) -> list[str]:
        """Override the slots method to indicate mutually incompatible presets.

        Mutually incompatible presets should have at least one slot in common.
        Slots have otherwise no use inside Loggia, but should roughly map to a
        single concern.
        """
        return []

    @classmethod
    def env_loader(cls) -> EnvironmentLoader | None:
        return None

    @classmethod
    def preference_key(cls) -> str:
        return to_snake_case(cls.__name__)
