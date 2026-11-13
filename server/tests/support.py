"""Helpers shared by the API tests."""

from fastapi.testclient import TestClient
from sampling import sample

from zapp_atlas.api.layout import LEVELS, layout

CURATOR = "0000-0002-1825-0097"
OUTSIDER = "0000-0003-3333-4444"

# The levels created from a JSON body. An image is created by uploading a file.
JSON_LEVELS = LEVELS[:-1]

# The path segment each level's routes live under.
SEGMENTS = {
    "Study": "studies",
    "Experiment": "experiments",
    "ExposureEvent": "exposures",
    "PhenotypeObservationSet": "observations",
    "Image": "images",
}


def signin(client: TestClient, orcid_id: str) -> None:
    client.app.state.settings.dev_auth = True
    res = client.post(
        "/auth/dev/login", data={"orcid_id": orcid_id, "name": "Test User"}, follow_redirects=False
    )
    assert res.status_code in (303, 307)


def signout(client: TestClient) -> None:
    client.cookies.clear()


def make_group(client: TestClient, name: str) -> int:
    """Create a research group as whoever is signed in, who becomes its admin."""
    res = client.post("/api/research-groups", json={"name": name})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def item_url(level: str, row_id: int) -> str:
    return f"/api/{SEGMENTS[level]}/{row_id}"


def collection_url(level: str, parent_id: int | None) -> str:
    """Where a new row of a level is posted: beneath its parent, if it has one."""
    parent = layout().levels[level].parent
    if parent is None:
        return f"/api/{SEGMENTS[level]}"
    return f"{item_url(parent.name, parent_id)}/{SEGMENTS[level]}"


def body(
    level: str, group: int, *, full: bool = True, status: str = "published"
) -> dict[str, object]:
    """A request body for a level, built from the schema."""
    made = sample(level, full=full)
    if level == "Study":
        # A study names its group, and the rule that an unpublished study
        # carries a nickname is the one thing required slots alone do not meet.
        made |= {
            "research_group": group,
            "status": status,
            "nickname": made.get("nickname", "a working name"),
        }
    return made


def study_fields(group: int) -> dict[str, object]:
    """What every study body must say, whatever else a test puts in it."""
    return {
        key: value for key, value in body("Study", group, full=False).items() if key != "nickname"
    }


def comparable(value: object) -> object:
    """Drop generated ids, and treat an empty list and an absent one alike."""
    if isinstance(value, dict):
        return {key: comparable(item) for key, item in value.items() if key != "id"}
    if isinstance(value, list):
        return [comparable(item) for item in value] or None
    return value


def carried(level: str, read: dict[str, object]) -> dict[str, object]:
    """A response cut down to the slots a request body for the level carries."""
    return {slot.name: comparable(read[slot.name]) for slot in layout().body_slots(level)}


def make_tree(client: TestClient, group: int, *, status: str = "published") -> dict[str, dict]:
    """Create one row of every JSON level, each inside the one before."""
    made: dict[str, dict] = {}
    parent_id = None
    for level in JSON_LEVELS:
        res = client.post(collection_url(level, parent_id), json=body(level, group, status=status))
        assert res.status_code == 201, res.text
        made[level] = res.json()
        parent_id = made[level]["id"]
    return made
