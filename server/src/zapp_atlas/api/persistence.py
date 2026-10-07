"""Shared persistence helpers for the API services."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_conflict(
    session: Session, detail: str, *, named: dict[str, str] | None = None
) -> None:
    """Commit, turning a unique-grain violation into a 409 instead of a 500.

    The join tables enforce their grain with unique indexes
    (``cabinet_grain``, ``tank_grain``, ``membership_grain``), so a duplicate
    insert raises ``IntegrityError``. Surface that as a clean conflict.

    A table with more than one unique key passes ``named``: a detail to use
    instead when the database's message mentions the given word, so the
    caller is told which key it broke (``{"nickname": "That nickname ..."}``).
    Both SQLite and PostgreSQL name the offending columns or index.
    """
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        message = str(exc.orig)
        for word, specific in (named or {}).items():
            if word in message:
                detail = specific
                break
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc
