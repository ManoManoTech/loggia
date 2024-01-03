from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Callable, TypeVar

from loggia._internal.bootstrap_logger import bootstrap_logger as logger
from loggia.base_preset import BasePreset
from loggia.utils.loaderutils import import_all_files, import_fqn

if TYPE_CHECKING:
    from collections.abc import Iterable

# Subclasses of BasePreset
_PresetT_co = TypeVar("_PresetT_co", bound=BasePreset, covariant=True)

# Static cache of requirement acceptors
_PresetRequirementAcceptor = Callable[[set[type[BasePreset]]], bool]
_PRESET_REQUIREMENT_ACCEPTORS: dict[type[BasePreset], _PresetRequirementAcceptor] = {}


def _constantly_true(_available_presets: set[type[BasePreset]]) -> bool:
    return True


def _make_preset_requirement_acceptor(preset: type[BasePreset]) -> None:
    requirements = preset.required_presets()

    def _requirements_acceptor(available_presets: set[type[BasePreset]]) -> bool:
        available_strs = {t.__name__ for t in available_presets} | {t.preference_key() for t in available_presets}
        for req in requirements:
            if isinstance(req, str) and req in available_strs:
                return True
            if isinstance(req, (list, set, tuple)) and all(subreq in available_strs for subreq in req):
                return True
        return False

    if len(requirements) == 0:
        _PRESET_REQUIREMENT_ACCEPTORS[preset] = _constantly_true
    else:
        _PRESET_REQUIREMENT_ACCEPTORS[preset] = _requirements_acceptor


def _meets_requirements(preset: type[BasePreset], available_presets: set[type[BasePreset]]) -> bool:
    if preset not in _PRESET_REQUIREMENT_ACCEPTORS:
        _make_preset_requirement_acceptor(preset)
    return _PRESET_REQUIREMENT_ACCEPTORS[preset](available_presets)


class Presets:
    """Internal utilities to manage a herd of preset types.

    Notably in scope:
    - Dynamic loading/importing of presets by package path or FQN
    - Slots resolution
    - deal with LOGIA_PRESETS
    """

    available_presets: set[type[BasePreset]]
    _skip_builtins: bool = False  # used for tests only, not part of external interface

    def __init__(self, preset_preferences: Iterable[str] | None = None):
        # We default to production presets.
        self.preset_preferences = {e.lower() for e in preset_preferences} if preset_preferences else {"prod"}
        builtin_presets = [] if self._skip_builtins else self._load_builtins()
        builtin_preset_names = {preset.__name__.lower() for preset in builtin_presets}

        self.unslotted_presets: list[type[BasePreset]] = []
        self.slotted_presets: dict[str, list[type[BasePreset]]] = defaultdict(list)

        # Index all built-in presets by their slots if possible
        # This allows us to discover the built-in slots
        for preset in builtin_presets:
            self._register_preset(preset)

        # Dynamically load non-builtin presets
        for prepre in preset_preferences or []:
            if prepre not in builtin_preset_names:
                if "." not in prepre:
                    logger.error(f"Preset preference {prepre} matches no builtin and is not a fully qualified name")
                else:
                    try:
                        preset = self._load_preset_fqn(prepre)
                        self._register_preset(preset)
                        self.preset_preferences.add(preset.preference_key())
                    except ImportError as e:
                        logger.error(f"Preset preference {prepre} matches no builtin and cannot be imported either: {e}")

        # Narrow down presets in the same slot
        selected_slotted_presets = self._select_slotted_presets()

        # Further narrow down presets by removing the ones with missing dependencies
        available_presets = set(self.unslotted_presets + list(selected_slotted_presets.values()))
        self._trim_presets(available_presets)

        # Expose the result as a set of preset types
        self.available_presets = available_presets

    def _register_preset(self, preset: type[BasePreset]) -> None:
        slots = preset.slots()
        if len(slots) == 0:
            self.unslotted_presets.append(preset)
        else:
            for slot in slots:
                self.slotted_presets[slot].append(preset)

    def _select_slotted_presets(self) -> dict[str, type[BasePreset]]:
        """Make sure only one preset is applied for a given slot."""
        selected_slotted_presets: dict[str, type[BasePreset]] = {}
        for slot, presets in self.slotted_presets.items():
            if len(presets) == 1:
                selected_slotted_presets[slot] = presets[0]
                continue

            indexed_presets = {preset.preference_key(): preset for preset in presets}
            indexed_preset_keys = set(indexed_presets.keys())
            solutions = indexed_preset_keys.intersection(self.preset_preferences)

            if len(solutions) == 0:
                solution = sorted(indexed_preset_keys)[0]
                logger.warn(
                    f"Preset slot '{slot}' has several presets available "
                    f"({', '.join(indexed_preset_keys)}) but no preference is set. "
                    "Use LOGGIA_PRESETS to force one over the others. We "
                    f"are defaulting to the '{solution}' preset.",
                )
            elif len(solutions) > 1:
                solution = sorted(solutions)[0]
                logger.warn(
                    f"Preset slot '{slot}' has several presets available "
                    f"({', '.join(indexed_preset_keys)}) and preferences ("
                    f"{', '.join(solutions)}) are themselves ambiguous. "
                    "Use LOGGIA_PRESETS to force one over the others. We "
                    f"are defaulting to the '{solution}' one.",
                )
            else:
                solution = solutions.pop()
            selected_slotted_presets[slot] = indexed_presets[solution]
        return selected_slotted_presets

    def _trim_presets(self, available_presets: set[type[BasePreset]]) -> None:
        """Removes presets with missing requirements from the list of available presets.

        This is done in a loop to allow for unlucky cascades to happen.

        TODO: A topological sort is more appropriate, but would forbid cycles, which we
              might want to forbid anyway.
        """
        deleted_something = True
        while deleted_something:
            to_delete = [p for p in available_presets if not _meets_requirements(p, available_presets)]
            for preset in to_delete:
                # XXX bootstrap logger trace log as per preset specification
                available_presets.remove(preset)
            deleted_something = len(to_delete) > 0

    def _load_builtins(self) -> list[type[BasePreset]]:
        base_dir = (Path(__file__).parent / "../..").resolve()
        all_preset_modules = import_all_files("loggia/presets", base_dir=base_dir)
        results: list[type[BasePreset]] = []
        for mod in all_preset_modules:
            for thing_name in dir(mod):
                thing = getattr(mod, thing_name)
                if isinstance(thing, type) and issubclass(thing, BasePreset) and thing is not BasePreset:
                    results.append(thing)
        return results

    def _load_preset_fqn(self, fqn: str) -> type[_PresetT_co]:  # pyright: ignore[reportInvalidTypeVarUse]
        # XXX(dugab): We may be able to type that in 3.12 with Generic Functions
        return import_fqn(fqn, ensure_subclass_of=BasePreset)  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
