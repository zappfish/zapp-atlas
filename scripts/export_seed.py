#!/usr/bin/env python3
"""Export curated studies from the dev DB as ``seed.py`` builder functions.

Usage:

    uv run --directory server python -m scripts.export_seed PMID:22194820 PMID:40359302

Or one publication at a time. The output is printed to stdout in a form
intended to be pasted (and edited) into ``server/seed.py``.

This is a one-way, human-in-the-loop tool: the output isn't meant to be
round-tripped through ``seed.py`` automatically, but to jumpstart the
next seed builder after a curator walks a paper through the forms.
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any, Iterable

from sqlalchemy.orm import Session

from server.db import get_engine, get_session_factory
from zebrafish_toxicology_atlas_schema.datamodel.sqla import (  # type: ignore
    Study,
)


def _slug(publication: str) -> str:
    """``PMID:41812223`` → ``pmid_41812223`` (safe Python identifier)."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", publication).strip("_").lower()
    return slug or "study"


def _py(value: Any) -> str:
    """Render a Python literal for simple scalars / lists."""
    if value is None:
        return "None"
    return repr(value)


def _qv(qv: Any) -> str | None:
    if qv is None:
        return None
    num = getattr(qv, "numeric_value", None)
    unit = getattr(qv, "unit", None)
    if num is None and unit is None:
        return None
    return (
        f"QuantityValue(unit={_py(unit)}, numeric_value={_py(num)})"
    )


def _emit_stressor(s: Any) -> list[str]:
    chem = s.chemical_id
    lines = [
        "        StressorChemical(",
        "            chemical_id=_upsert_chemical(",
        "                session,",
        f"                uri={_py(chem.uri)},",
        f"                chebi_id={_py(chem.chebi_id)},",
        f"                cas_id={_py(chem.cas_id)},",
        f"                chemical_name={_py(chem.chemical_name)},",
        "            ),",
    ]
    conc = _qv(s.concentration)
    if conc:
        lines.append(f"            concentration={conc},")
    if s.manufacturer:
        lines.append(f"            manufacturer={_py(s.manufacturer)},")
    lines.append("        ),")
    return lines


def _emit_phenotype(p: Any) -> list[str]:
    term = p.phenotype_term_id
    lines = ["        Phenotype("]
    if p.stage:
        lines.append(f"            stage={_py(p.stage)},")
    if p.severity:
        lines.append(f"            severity={_py(p.severity)},")
    if term is not None:
        lines.append("            phenotype_term_id=_upsert_phenotype_term(")
        lines.append("                session,")
        lines.append(f"                term_uri={_py(term.term_uri)},")
        lines.append(
            f"                term_label={_py(getattr(term, 'term_label', '') or '')},"
        )
        lines.append("            ),")
    prev = _qv(p.prevalence)
    if prev:
        lines.append(f"            prevalence={prev},")
    lines.append("        ),")
    return lines


def _emit_observation(obs: Any, exposure_var: str) -> list[str]:
    lines = [
        "    obs = PhenotypeObservationSet()",
        f"    {exposure_var}.phenotype_observation.append(obs)",
    ]
    for p in obs.phenotype or []:
        lines.append("    obs.phenotype.append(")
        lines.extend(_emit_phenotype(p))
        lines.append("    )")
    if obs.image:
        lines.append(
            "    # NOTE: seeded images aren't re-uploaded here; upload "
            "manually or extend the seed to re-read from disk."
        )
    return lines


def _emit_exposure(ee: Any) -> list[str]:
    lines = []
    route_line = ""
    if ee.route is not None:
        lines.append("    route = _upsert_exposure_route(")
        lines.append("        session,")
        lines.append(f"        term_uri={_py(ee.route.term_uri)},")
        lines.append(
            f"        term_label={_py(getattr(ee.route, 'term_label', '') or '')},"
        )
        lines.append("    )")
        route_line = "route=route,"
    exp_type_line = ""
    if ee.exposure_type is not None:
        lines.append("    exposure_type = _upsert_exposure_type(")
        lines.append("        session,")
        lines.append(f"        term_uri={_py(ee.exposure_type.term_uri)},")
        lines.append(
            f"        term_label={_py(getattr(ee.exposure_type, 'term_label', '') or '')},"
        )
        lines.append("    )")
        exp_type_line = "exposure_type=exposure_type,"

    lines.append("    exposure = ExposureEvent(")
    if route_line:
        lines.append(f"        {route_line}")
    if ee.exposure_start_stage:
        lines.append(f"        exposure_start_stage={_py(ee.exposure_start_stage)},")
    if ee.exposure_end_stage:
        lines.append(f"        exposure_end_stage={_py(ee.exposure_end_stage)},")
    if exp_type_line:
        lines.append(f"        {exp_type_line}")
    if ee.comment:
        lines.append(f"        comment={_py(ee.comment)},")
    lines.append("    )")
    lines.append("    experiment.exposure_event.append(exposure)")

    for s in ee.stressor or []:
        lines.append("    exposure.stressor.append(")
        lines.extend(_emit_stressor(s))
        lines.append("    )")

    for obs in ee.phenotype_observation or []:
        lines.extend(_emit_observation(obs, "exposure"))

    return lines


def _emit_study(study: Study) -> str:
    slug = _slug(study.publication or f"study_{study.id}")
    header = [
        f"def _build_{slug}_study(session: Session) -> Study:",
        f'    """Auto-generated from the dev DB; edit the docstring to describe the paper."""',
    ]

    exp = (study.experiment or [None])[0]
    if exp is None:
        return "\n".join(header + ["    raise NotImplementedError('no experiments')", ""])

    lines = list(header)
    fish = exp.fish
    if fish is not None:
        lines.append(
            f"    fish = _upsert_fish(session, zfin_id={_py(fish.zfin_id)}, name={_py(fish.name)})"
        )
    lines.append(
        f"    study = Study(publication={_py(study.publication)}, lab={_py(study.lab)}, annotator={_py(list(study.annotator or []))})"
    )
    rearing = exp.standard_rearing_condition
    lines.append(
        f"    experiment = Experiment(standard_rearing_condition={_py(rearing)}, fish={'fish' if fish else 'None'})"
    )
    if exp.rearing_condition_comment:
        lines.append(
            f"    experiment.rearing_condition_comment = {_py(exp.rearing_condition_comment)}"
        )
    lines.append("    study.experiment.append(experiment)")

    for ee in exp.exposure_event or []:
        lines.append("")
        lines.extend(_emit_exposure(ee))

    lines.append("")
    lines.append("    return study")
    lines.append("")
    return "\n".join(lines)


def export(session: Session, publications: Iterable[str]) -> str:
    blocks: list[str] = []
    for pub in publications:
        study = (
            session.query(Study).filter(Study.publication == pub).one_or_none()
        )
        if study is None:
            print(f"# WARN: {pub!r} not found in dev DB", file=sys.stderr)
            continue
        blocks.append(_emit_study(study))
    return "\n\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "publications",
        nargs="+",
        help="Publication identifiers, e.g. PMID:22194820",
    )
    args = parser.parse_args()

    engine = get_engine()
    SessionLocal = get_session_factory(engine)
    with SessionLocal() as session:
        print(export(session, args.publications))


if __name__ == "__main__":
    main()
