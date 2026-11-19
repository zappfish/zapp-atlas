"""Example request bodies, and whether the server accepts each one.

The client checks a body against the LinkML JSON Schema before sending it. The
server checks it against the generated Pydantic models and the schema's
class-level rules. Those are two generators' renderings of one schema, so only
a test can say the client will not turn away a body the server would take.

The test is split so that each side needs only its own tools. This module
writes the examples, and the server's answer to each, to a file in the client:

    python tests/request_examples.py ../client/tests/fixtures/request-examples.json

``test_request_examples.py`` fails when that file is stale. The client's own
test, ``client/tests/request-examples.test.ts``, requires its validators to
pass every example the server accepts.
"""

import copy
import json
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from support import LABELS_FIXTURE, body, built

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.api.layout import LEVELS, SlotKind, layout
from zapp_atlas.api.tree import build
from zapp_atlas.db import init_db
from zapp_atlas.labels import Labels
from zapp_atlas.schema import pydantic_crud as models
from zapp_atlas.zfin import Zfin

CLIENT_COPY = (
    Path(__file__).resolve().parents[2] / "client" / "tests" / "fixtures" / "request-examples.json"
)


def _bodies() -> dict[str, tuple[str, dict]]:
    """Bodies to try, by name: each level's fullest and barest, then variations."""
    cases: dict[str, tuple[str, dict]] = {}
    for level in LEVELS:
        full = body(level, 1)
        cases[f"{level}: every slot"] = (level, full)
        cases[f"{level}: required slots only"] = (level, body(level, 1, full=False))
        cases[f"{level}: an unknown field"] = (level, full | {"colour": 1})
        cases[f"{level}: an id"] = (level, full | {"id": 1})
        for slot in layout().slots(level):
            if slot.kind is SlotKind.LEVEL:
                cases[f"{level}: the level beneath it"] = (level, full | {slot.name: []})

    def varied(name: str, level: str, change: Callable[[dict], object]) -> None:
        made = copy.deepcopy(body(level, 1))
        change(made)
        cases[name] = (level, made)

    def stressor(made: dict) -> dict:
        return made["stressor"][0]

    def phenotype(made: dict) -> dict:
        return made["phenotype"][0]

    # Class-level rules.
    varied(
        "an unpublished study with no nickname",
        "Study",
        lambda b: [b.pop("publication"), b.pop("nickname")],
    )
    varied(
        "an unpublished study with a blank nickname",
        "Study",
        lambda b: b.update(publication=None, nickname="  "),
    )
    varied("a published study with no nickname", "Study", lambda b: b.pop("nickname"))
    varied(
        "a stressor with no identity",
        "ExposureEvent",
        lambda b: [stressor(b).pop("chemical_id"), stressor(b).pop("unrecognized_chemical_name")],
    )
    varied(
        "a stressor known only by name", "ExposureEvent", lambda b: stressor(b).pop("chemical_id")
    )
    varied(
        "an unnamed other manufacturer",
        "ExposureEvent",
        lambda b: [
            stressor(b).update(manufacturer="other_not_listed"),
            stressor(b).pop("unrecognized_manufacturer_name"),
        ],
    )
    varied(
        "an unnamed other vehicle",
        "ExposureEvent",
        lambda b: [
            b["vehicle"][0].update(vehicle_type="other_not_listed"),
            b["vehicle"][0].pop("unrecognized_chemical_name"),
        ],
    )
    # Patterns, enums, types and ranges.
    varied("a nickname that is too long", "Study", lambda b: b.update(nickname="x" * 201))
    varied("a status that does not exist", "Study", lambda b: b.update(status="finished"))
    varied("a publication that is neither kind", "Study", lambda b: b.update(publication="soon"))
    varied("a route that does not exist", "ExposureEvent", lambda b: b.update(route="osmosis"))
    varied(
        "a concentration below zero",
        "ExposureEvent",
        lambda b: stressor(b)["concentration"].update(numeric_value=-1),
    )
    varied(
        "a severity that does not exist",
        "PhenotypeObservationSet",
        lambda b: phenotype(b).update(severity="awful"),
    )
    varied(
        "a prevalence over a hundred",
        "PhenotypeObservationSet",
        lambda b: phenotype(b).update(prevalence=120),
    )
    varied(
        "text where a flag belongs",
        "Experiment",
        lambda b: b.update(standard_rearing_condition="maybe"),
    )
    # What only the server may set.
    varied(
        "a study that names its annotator",
        "Study",
        lambda b: b.update(annotator=["ORCID:0000-0002-1825-0097"]),
    )
    varied("an id on an owned part", "ExposureEvent", lambda b: stressor(b).update(id=7))
    # Optional slots sent as null, as a form that clears a field may send them.
    varied("a null optional enum", "ExposureEvent", lambda b: stressor(b).update(manufacturer=None))
    varied("a null optional object", "ExposureEvent", lambda b: b.update(regimen=None))
    varied("a null optional list", "ExposureEvent", lambda b: b.update(vehicle=None))
    varied("a null optional text", "Experiment", lambda b: b.update(rearing_condition_comment=None))
    return cases


def _accepted(session: Session, level: str, made: dict) -> bool:
    try:
        build(session, level, getattr(models, f"{level}Input").model_validate(made))
    except (ValidationError, SchemaRuleViolation):
        return False
    finally:
        session.rollback()
    return True


def request_examples() -> list[dict[str, object]]:
    """Every body tried, with the level it is for and whether the server accepts it."""
    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
    init_db(engine)
    with tempfile.TemporaryDirectory() as bundle, Session(engine) as session:
        # As the app's sessions carry them: no ZFIN data, so no fish is
        # matched, and the labels of the terms the tests name.
        session.info["zfin"] = Zfin(Path("no-bundle") / "zfin.db")
        labels = built("labels_db.py", Path(bundle) / "labels.db", str(LABELS_FIXTURE))
        session.info["labels"] = Labels(labels)
        return [
            {
                "name": name,
                "level": level,
                "body": made,
                "accepted": _accepted(session, level, made),
            }
            for name, (level, made) in _bodies().items()
        ]


def request_examples_document() -> str:
    return json.dumps(request_examples(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(request_examples_document())
