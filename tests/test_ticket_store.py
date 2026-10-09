import uuid

import pytest

from meridian import ticket_store
from meridian.ticket_store import TicketNotFoundError, get_ticket, save_ticket

TICKET = {"title": "Cannot log in", "severity": "high", "category": "access_request"}
OTHER_TICKET = {"title": "Wrong invoice total", "severity": "low", "category": "billing"}


@pytest.fixture(autouse=True)
def empty_store():
    # The store is module-level memory, so reset it to keep tests independent.
    ticket_store._tickets.clear()
    yield
    ticket_store._tickets.clear()


# --- save_ticket ---------------------------------------------------------


def test_save_ticket_returns_a_uuid_string():
    ticket_id = save_ticket(TICKET)
    assert isinstance(ticket_id, str)
    # Round-trips through uuid.UUID only if it is a canonical UUID string.
    assert str(uuid.UUID(ticket_id)) == ticket_id


def test_two_different_tickets_get_different_ids():
    assert save_ticket(TICKET) != save_ticket(OTHER_TICKET)


def test_saving_the_same_ticket_twice_gets_different_ids():
    # IDs are generated per save, not derived from the ticket's content.
    assert save_ticket(TICKET) != save_ticket(TICKET)


def test_many_saves_produce_unique_ids():
    ids = [save_ticket({"n": n}) for n in range(200)]
    assert len(set(ids)) == len(ids)


def test_save_ticket_does_not_modify_the_ticket():
    ticket = dict(TICKET)
    save_ticket(ticket)
    # No ID or other field is injected into the caller's dict.
    assert ticket == TICKET


# --- get_ticket: pass cases ----------------------------------------------


def test_get_ticket_returns_the_saved_dict():
    ticket_id = save_ticket(TICKET)
    assert get_ticket(ticket_id) == TICKET


def test_each_id_returns_its_own_ticket():
    first_id = save_ticket(TICKET)
    second_id = save_ticket(OTHER_TICKET)
    assert get_ticket(first_id) == TICKET
    assert get_ticket(second_id) == OTHER_TICKET
    assert get_ticket(first_id) != get_ticket(second_id)


def test_ticket_can_be_retrieved_repeatedly():
    ticket_id = save_ticket(TICKET)
    assert get_ticket(ticket_id) == get_ticket(ticket_id) == TICKET


def test_saving_another_ticket_does_not_overwrite_an_earlier_one():
    first_id = save_ticket(TICKET)
    save_ticket(OTHER_TICKET)
    assert get_ticket(first_id) == TICKET


@pytest.mark.parametrize(
    "ticket",
    [
        {},
        {"title": "", "severity": None},
        {"tags": ["vpn", "urgent"], "reporter": {"name": "Sam", "id": 7}},
    ],
)
def test_round_trip_preserves_any_dict_content(ticket):
    assert get_ticket(save_ticket(ticket)) == ticket


def test_changing_the_original_dict_after_saving_does_not_change_the_stored_ticket():
    ticket = {"title": "Cannot log in", "tags": ["vpn"]}
    ticket_id = save_ticket(ticket)
    ticket["title"] = "changed"
    ticket["tags"].append("changed")
    assert get_ticket(ticket_id) == {"title": "Cannot log in", "tags": ["vpn"]}


def test_changing_a_retrieved_dict_does_not_change_the_stored_ticket():
    ticket_id = save_ticket({"title": "Cannot log in", "tags": ["vpn"]})
    retrieved = get_ticket(ticket_id)
    retrieved["title"] = "changed"
    retrieved["tags"].append("changed")
    assert get_ticket(ticket_id) == {"title": "Cannot log in", "tags": ["vpn"]}


# --- get_ticket: failure cases -------------------------------------------


def test_unknown_id_raises_ticket_not_found():
    with pytest.raises(TicketNotFoundError):
        get_ticket("does-not-exist")


def test_unknown_id_raises_when_store_has_other_tickets():
    save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket("does-not-exist")


def test_well_formed_but_unsaved_uuid_raises_ticket_not_found():
    # Looking valid is not enough; the ID must have been issued by save_ticket.
    save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket(str(uuid.uuid4()))


@pytest.mark.parametrize("ticket_id", ["", "   "])
def test_blank_id_raises_ticket_not_found(ticket_id):
    save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket(ticket_id)


@pytest.mark.parametrize(
    "mangle",
    [str.upper, lambda i: f" {i} ", lambda i: i[:-1], lambda i: i.replace("-", "")],
    ids=["uppercased", "padded", "truncated", "no-dashes"],
)
def test_id_must_match_exactly(mangle):
    ticket_id = save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket(mangle(ticket_id))


@pytest.mark.parametrize("ticket_id", [None, 42, 3.5, ["abc"], {"id": "abc"}])
def test_non_string_id_raises_ticket_not_found(ticket_id):
    # Unhashable values must not leak a TypeError from the underlying dict.
    save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket(ticket_id)


def test_uuid_object_is_not_accepted_in_place_of_the_string_id():
    ticket_id = save_ticket(TICKET)
    with pytest.raises(TicketNotFoundError):
        get_ticket(uuid.UUID(ticket_id))  # type: ignore[arg-type]


def test_ticket_not_found_is_not_a_key_error():
    # Callers catching KeyError must not accidentally swallow a missing ticket,
    # and a raw KeyError must not escape from the store.
    assert not issubclass(TicketNotFoundError, KeyError)
    with pytest.raises(TicketNotFoundError):
        get_ticket("does-not-exist")


def test_failed_lookup_does_not_create_a_ticket():
    with pytest.raises(TicketNotFoundError):
        get_ticket("does-not-exist")
    with pytest.raises(TicketNotFoundError):
        get_ticket("does-not-exist")
    assert ticket_store._tickets == {}
