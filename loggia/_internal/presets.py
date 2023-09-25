from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from loggia._internal.bootstrap_logger import bootstrap_logger as logger
from loggia.base_preset import BasePreset
from loggia.utils.loaderutils import import_all_files, import_fqn

if TYPE_CHECKING:
    from collections.abc import Iterable

# Subclasses of BasePreset
_PresetT_co = TypeVar("_PresetT_co", bound=BasePreset, covariant=True)


class Presets:
    """Internal utilities to manage a herd of preset types.

    Notably in scope:
    - Dynamic loading/importing of presets by package path or FQN
    - Slots resolution
    - deal with LOGIA_PRESETS
    """

    available: list[type[BasePreset]]

    def __init__(self, preset_preferences: Iterable[str] | None = None):
        # We default to production presets.
        self.preset_preferences = {e.lower() for e in preset_preferences} if preset_preferences else {"prod"}
        builtin_presets = self._load_builtins()
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
                        logger.error(f"Preset preference {prepre} matches no builtin  and cannot be imported either: {e}")

        # For each slot with more than one preset, attempt to resolve the single
        # preset we will present to the rest of the system
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

        # Record this
        self.available_presets = self.unslotted_presets + list(selected_slotted_presets.values())

    def _register_preset(self, preset: type[BasePreset]) -> None:
        slots = preset.slots()
        if len(slots) == 0:
            self.unslotted_presets.append(preset)
        else:
            for slot in slots:
                self.slotted_presets[slot].append(preset)

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
