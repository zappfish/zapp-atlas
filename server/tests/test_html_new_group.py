from __future__ import annotations

from fastapi.testclient import TestClient

from zapp_atlas.schema.sqla import ResearchGroup, ResearchGroupMember


def _sign_in(client: TestClient, orcid_id: str = "0000-0002-1825-0097") -> None:
    client.app.state.settings.dev_auth = True
    client.post("/auth/dev/login", data={"name": "Ada Lovelace", "orcid_id": orcid_id})


def test_create_group_requires_sign_in(client: TestClient) -> None:
    res = client.post(
        "/research-groups", data={"name": "Neurotox Lab"}, follow_redirects=False
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/login"


def test_create_group_persists_and_enrolls_the_creator_as_admin(
    client: TestClient,
) -> None:
    _sign_in(client, orcid_id="0000-0002-1825-0097")

    res = client.post(
        "/research-groups", data={"name": "Neurotox Lab"}, follow_redirects=False
    )

    assert res.status_code == 303
    with client.app.state.session_factory() as session:
        group = session.query(ResearchGroup).filter_by(name="Neurotox Lab").one()
        assert res.headers["location"] == f"/research-groups/{group.id}"
        member = (
            session.query(ResearchGroupMember)
            .filter_by(research_group=group.id)
            .one()
        )
        assert member.member == "ORCID:0000-0002-1825-0097"
        assert member.role == "admin"


def test_create_group_over_htmx_signals_a_full_page_redirect(
    client: TestClient,
) -> None:
    _sign_in(client)

    res = client.post(
        "/research-groups",
        data={"name": "HTMX Lab"},
        headers={"HX-Request": "true"},
        follow_redirects=False,
    )

    assert res.status_code == 204
    assert res.headers["HX-Redirect"].startswith("/research-groups/")
