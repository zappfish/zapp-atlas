"""The client's copy of the request examples must be what the server would write today."""

from request_examples import CLIENT_COPY, request_examples, request_examples_document

from zapp_atlas.api.layout import LEVELS


def test_the_clients_copy_of_the_request_examples_is_current() -> None:
    """The client tests its validators against this file.

    If it is stale, the client is being held to answers the server no longer
    gives. Regenerate it with ``just api-types``.
    """
    assert CLIENT_COPY.read_text() == request_examples_document(), (
        "client/tests/fixtures/request-examples.json is out of date; run `just api-types`"
    )


def test_every_level_has_an_example_the_server_accepts() -> None:
    """The client is only held to the accepted examples, so each level needs some."""
    accepted = {example["level"] for example in request_examples() if example["accepted"]}
    assert accepted == set(LEVELS)


def test_some_examples_are_rejected() -> None:
    """A set of examples the server accepted without exception would say little about it."""
    assert not all(example["accepted"] for example in request_examples())
