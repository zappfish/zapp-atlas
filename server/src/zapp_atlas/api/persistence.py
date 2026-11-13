"""Shared persistence helpers for the API services."""

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@contextmanager
def conflicts_as_409(
    session: Session, detail: str, *, named: dict[str, str] | None = None
) -> Iterator[None]:
    """Turn a unique-key violation inside the block into a 409 instead of a 500.

    The tables enforce their grain with unique indexes (``cabinet_grain``,
    ``tank_grain``, ``membership_grain``, ``study_nickname_grain``), so a
    duplicate insert raises ``IntegrityError``. Surface that as a clean conflict.

    A table with more than one unique key passes ``named``: a detail to use
    instead when the database's message mentions the given word, so the
    caller is told which key it broke (``{"nickname": "That nickname ..."}``).
    Both SQLite and PostgreSQL name the offending columns or index.
    """
    try:
        yield
    except IntegrityError as exc:
        session.rollback()
        message = str(exc.orig)
        for word, specific in (named or {}).items():
            if word in message:
                detail = specific
                break
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc


def commit_or_conflict(
    session: Session, detail: str, *, named: dict[str, str] | None = None
) -> None:
    """Commit, answering 409 if that breaks a unique key."""
    with conflicts_as_409(session, detail, named=named):
        session.commit()
