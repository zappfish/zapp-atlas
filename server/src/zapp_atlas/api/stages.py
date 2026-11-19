"""What the schema cannot say about an exposure's stages.

Each stage slot holds one of ZFIN's stages, which ``api.terms`` checks. That
an exposure does not end at a stage before the one it started at is a rule
about two slots, which LinkML has no way to state, so it is checked here once
both are stored.

Unlike the rest of ``api`` this names slots, since the rule is about these
two in particular.
"""

from sqlalchemy.orm import Session

from zapp_atlas.api.errors import SchemaRuleViolation
from zapp_atlas.schema.sqla import ExposureEvent
from zapp_atlas.zfin import Zfin


def check_stage_order(session: Session, exposure: ExposureEvent) -> None:
    if exposure.exposure_start_stage is None or exposure.exposure_end_stage is None:
        return
    zfin: Zfin = session.info["zfin"]
    start = zfin.stage(exposure.exposure_start_stage)
    end = zfin.stage(exposure.exposure_end_stage)
    # Both are stages the labels have, or they would not have been stored. A
    # stage the labels have and this table lacks is "Unknown", which has no
    # place in the order.
    if start is not None and end is not None and end.start_hours < start.start_hours:
        raise SchemaRuleViolation(
            f"ExposureEvent: exposure_end_stage ({end.name}) is before "
            f"exposure_start_stage ({start.name})."
        )
