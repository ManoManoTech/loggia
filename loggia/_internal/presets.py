from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from loggia._internal.bootstrap_logger import BootstrapLogger as logger
from loggia.base_preset import BasePreset
from loggia.utils.loaderutils import import_all_files

if TYPE_CHECKING:
    from collections.abc import Iterable


class Presets:
    """Internal utilities to manage a herd of preset types.

    Notably in scope:
    - Dynamic loading/importing of presets by package path or FQN
    - Slots resolution
    - deal with LOGIA_PRESETS
    """
    available: list[type[BasePreset]]

    def __init__(self, preset_preferences: Iterable[str] | None = None):
        if not preset_preferences:
            # We default to production presets.
            preset_preferences = {"prod"}
        else:
            preset_preferences = {e.lower() for e in preset_preferences}

        all_builtins = self._load_builtins()

        # Index all presets by their slots if possible
        unslotted_presets: list[type[BasePreset]] = []
        slotted_presets: dict[str, list[type[BasePreset]]] = defaultdict(list)
        for preset in all_builtins:
            slots = preset.slots()
            if len(slots) == 0:
                unslotted_presets.append(preset)
            else:
                for slot in slots:
                    slotted_presets[slot].append(preset)

        # For each slot with more than one preset, attempt to resolve the single
        # preset we will present to the rest of the system
        selected_slotted_presets: dict[str, type[BasePreset]] = {}
        for slot, presets in slotted_presets.items():
            if len(presets) < 2:  # noqa: PLR2004
                continue

            indexed_presets = {preset.__name__.lower(): preset for preset in presets}
            indexed_preset_keys = set(indexed_presets.keys())
            solutions = indexed_preset_keys.intersection(preset_preferences)

            if len(solutions) == 0:
                solution = sorted(indexed_preset_keys)[0]
                logger.warn(f"Preset slot '{slot}' has several presets available "
                            f"({', '.join(indexed_preset_keys)}) but no preference is set. "
                            "Use LOGGIA_PRESETS to force one over the others. We "
                            f"are defaulting to the '{solution}' preset.")
            elif len(solutions) > 1:
                solution = sorted(solutions)[0]
                logger.warn(f"Preset slot '{slot}' has several presets available "
                            f"({', '.join(indexed_preset_keys)}) and preferences ("
                            f"{', '.join(solutions)}) are themselves ambiguous. "
                            "Use LOGGIA_PRESETS to force one over the others. We "
                            f"are defaulting to the '{solution}' one.")
            else:
                solution = solutions.pop()
            selected_slotted_presets[slot] = indexed_presets[solution]

        # Record this
        unslotted_presets.extend(selected_slotted_presets.values())
        self.available = unslotted_presets


    def _load_builtins(self) -> list[type[BasePreset]]:
        base_dir = (Path(__file__).parent / "../..").resolve()
        all_preset_modules = import_all_files("loggia/presets", base_dir=base_dir)
        results: list[type[BasePreset]] = []
        for mod in all_preset_modules:
            for thing_name in dir(mod):
                thing = getattr(mod, thing_name)
                if isinstance(thing, type) and \
                   issubclass(thing, BasePreset) and \
                   thing is not BasePreset:
                    results.append(thing)
        return results
