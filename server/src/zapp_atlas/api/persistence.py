"""Shared persistence helpers for the API services."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_conflict(session: Session, detail: str) -> None:
    """Commit, turning a unique-grain violation into a 409 instead of a 500.

    The join tables enforce their grain with unique indexes
    (``cabinet_grain``, ``tank_grain``, ``membership_grain``), so a duplicate
    insert raises ``IntegrityError``. Surface that as a clean conflict.
    """
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=detail
        ) from exc
