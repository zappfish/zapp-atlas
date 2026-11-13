"""How the API cuts the data model into resources.

The model nests: a study contains experiments, an experiment contains exposure
events, and so on down. The API saves each of those *levels* as a unit. A
level's request body carries the level's own fields and everything it owns
beneath it, and stops at the next level down, which is a resource of its own.

This module declares structure only: which classes are levels, and which stand
alone with routes of their own. Everything else -- what a level owns, what it
merely refers to, where it stops -- is read from the LinkML schema.
``tests/test_api_layout.py`` fails when the two disagree, so a class added to
the schema has to be placed here before the suite passes again.
"""

from dataclasses import dataclass
from enum import Enum
from functools import cache, cached_property

from linkml_runtime import SchemaView

from zapp_atlas.schema.view import is_reference, schema_view

# Outermost first. Each is nested in the one before through a single slot.
LEVELS = (
    "Study",
    "Experiment",
    "ExposureEvent",
    "PhenotypeObservationSet",
    # An image's row keys its stored file, so it cannot be replaced along with
    # the rest of an observation the way a phenotype can.
    "Image",
)

# Classes outside the study tree, served by routes of their own.
STANDALONE = (
    "ResearchGroup",
    "ResearchGroupMember",
    "ChemicalCabinetEntry",
    "FishTankEntry",
)


class SlotKind(Enum):
    VALUE = "value"
    """A scalar, a list of scalars, or the id of a row that lives elsewhere."""

    OWNED = "owned"
    """An inlined object that exists only as part of this one."""

    REFERENCE = "reference"
    """An inlined object standing for a shared row, found by its identifier."""

    LEVEL = "level"
    """The next level down: a resource of its own, not part of this body."""


@dataclass(frozen=True)
class Slot:
    name: str
    kind: SlotKind
    range: str
    multivalued: bool


@dataclass(frozen=True)
class Level:
    name: str
    parent: "Level | None"
    slot_in_parent: str | None


@dataclass(frozen=True)
class Layout:
    view: SchemaView

    def slots(self, class_name: str) -> tuple[Slot, ...]:
        """Every slot of a class except its generated ``id``."""
        return tuple(
            self._slot(class_name, slot_name)
            for slot_name in self.view.class_slots(class_name)
            if slot_name != "id"
        )

    def _slot(self, class_name: str, slot_name: str) -> Slot:
        slot = self.view.induced_slot(slot_name, class_name)
        return Slot(
            name=slot_name,
            kind=self._kind(slot.range, inlined=bool(slot.inlined)),
            range=slot.range,
            multivalued=bool(slot.multivalued),
        )

    def _kind(self, range_name: str, *, inlined: bool) -> SlotKind:
        if not inlined or range_name not in self.view.all_classes():
            return SlotKind.VALUE
        if range_name in LEVELS:
            return SlotKind.LEVEL
        if self.is_shared(range_name):
            return SlotKind.REFERENCE
        return SlotKind.OWNED

    def is_shared(self, class_name: str) -> bool:
        """Is this a class of shared reference rows, found by a natural identifier?"""
        return is_reference(self.view, class_name)

    @cached_property
    def levels(self) -> dict[str, Level]:
        levels: dict[str, Level] = {}
        for name in LEVELS:
            parents = [
                (levels[parent], slot.name)
                for parent in levels
                for slot in self.slots(parent)
                if slot.kind is SlotKind.LEVEL and slot.range == name
            ]
            [(parent, slot_name)] = parents or [(None, None)]
            levels[name] = Level(name=name, parent=parent, slot_in_parent=slot_name)
        return levels

    def body_slots(self, class_name: str) -> tuple[Slot, ...]:
        """The slots a request body for this class carries: all but the next level."""
        return tuple(slot for slot in self.slots(class_name) if slot.kind is not SlotKind.LEVEL)

    def within(self, level_name: str) -> frozenset[str]:
        """The classes a level's body reaches: what it owns and what it refers to."""
        found: set[str] = set()
        pending = [level_name]
        while pending:
            for slot in self.body_slots(pending.pop()):
                if slot.kind is not SlotKind.VALUE and slot.range not in found:
                    found.add(slot.range)
                    pending.append(slot.range)
        return frozenset(found)


@cache
def layout() -> Layout:
    return Layout(schema_view())
