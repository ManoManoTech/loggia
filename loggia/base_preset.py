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
        """The defining part of what the preset does by mutating conf as appropriate."""
        raise NotImplementedError

    @classmethod
    def slots(cls) -> list[str]:
        """Override the slots method to indicate mutually incompatible presets.

        Mutually incompatible presets should have at least one slot in common.
        Slots have otherwise no use inside Loggia, but should roughly map to a
        single concern.
        """
        return []

    @classmethod
    def required_presets(cls) -> list[str | list[str]]:
        """Provides a mechanism for preset->preset dependencies.

        This is the primary mechanism to make a preset tied to the 'dev' or 'prod'
        presets without introducing a new slot.

        The returned value is interpreted using the following rules:
            - Single strings point to another's prefix name or preference key
            - Sub-lists are also made of another's prefix name or preference key
            - Sub-lists elements are implicit AND
            - Main-list elements are implicit OR

        Examples:
            - ["dev", "prod"]  # 'dev' OR 'prod' preset is activating
            - [["prod", "datadog"]]  # 'prod' AND 'datadog' is activating
            - ["dev", ["prod", "datadog"]]  # 'dev' OR ('prod' AND 'datadog') are activating

        Presets disabling themselves because the clause doesn't match will result
        in a log at TRACE level in the bootstrap logger.

        NB: Requirements resolution happens after slot-selection and not before,
        unlike most dependency management solutions. This makes things simpler but
        less powerful.
        """
        return []

    @classmethod
    def env_loader(cls) -> EnvironmentLoader | None:
        return None

    @classmethod
    def preference_key(cls) -> str:
        return to_snake_case(cls.__name__)
