"""Reading the signed-in identity off the request.

Any page that needs to know who is signed in — the login page, a header
indicator, the submission portal — should depend on `get_current_identity`
rather than reaching for the cookie itself.
"""

from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from zapp_atlas.api.deps import get_session
from zapp_atlas.auth.models import OrcidIdentity
from zapp_atlas.auth.services import ORCID_AUTH_COOKIE, get_orcid_identity


def get_current_identity(
    session: Annotated[Session, Depends(get_session)],
    identity_id: Annotated[str | None, Cookie(alias=ORCID_AUTH_COOKIE)] = None,
) -> OrcidIdentity | None:
    """The signed-in identity, or None when signed out.

    A cookie naming an identity that no longer exists is treated as signed
    out; it is stale rather than meaningful.
    """
    if identity_id is None:
        return None
    return get_orcid_identity(session, identity_id)


CurrentIdentity = Annotated[OrcidIdentity | None, Depends(get_current_identity)]
