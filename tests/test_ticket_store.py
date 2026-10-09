import uuid

import pytest


def test_save_ticket():
    from meridian.ticket_store import save_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    result = save_ticket(ticket)

    assert isinstance(result, str)
    uuid.UUID(result)  # raises ValueError if result is not a valid UUID

def test_save_ticket_returns_different_uuid():
    from meridian.ticket_store import save_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    result1 = save_ticket(ticket)
    result2 = save_ticket(ticket)
    assert result1 != result2

def test_get_ticket_returns_saved_ticket():
    from meridian.ticket_store import save_ticket, get_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    ticket_id = save_ticket(ticket)

    retrieved_ticket = get_ticket(ticket_id)

    assert retrieved_ticket == ticket

def test_get_ticket_with_unknown_id_raises_ticket_not_found():
    from meridian.ticket_store import get_ticket, TicketNotFoundError

    with pytest.raises(TicketNotFoundError):
        get_ticket("non-existent-id")


# --- Edge case 1: the store keeps its own copy of the ticket ---

def test_changing_original_ticket_after_save_does_not_change_stored_ticket():
    from meridian.ticket_store import save_ticket, get_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    ticket_id = save_ticket(ticket)

    ticket["severity"] = "low"

    assert get_ticket(ticket_id)["severity"] == "high"

def test_changing_retrieved_ticket_does_not_change_stored_ticket():
    from meridian.ticket_store import save_ticket, get_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    ticket_id = save_ticket(ticket)

    retrieved_ticket = get_ticket(ticket_id)
    retrieved_ticket["severity"] = "low"

    assert get_ticket(ticket_id)["severity"] == "high"

def test_saving_same_ticket_twice_stores_independent_copies():
    from meridian.ticket_store import save_ticket, get_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    first_id = save_ticket(ticket)
    second_id = save_ticket(ticket)

    get_ticket(first_id)["severity"] = "low"

    assert get_ticket(second_id)["severity"] == "high"


# --- Edge case 2: bad input to save_ticket ---

def test_save_none_raises_type_error():
    from meridian.ticket_store import save_ticket

    with pytest.raises(TypeError):
        save_ticket(None)

@pytest.mark.parametrize("bad_ticket", ["Server is down", ["high", "bug"], 42])
def test_save_non_dict_raises_type_error(bad_ticket):
    from meridian.ticket_store import save_ticket

    with pytest.raises(TypeError):
        save_ticket(bad_ticket)

def test_save_empty_dict_raises_value_error():
    from meridian.ticket_store import save_ticket

    with pytest.raises(ValueError):
        save_ticket({})

@pytest.mark.parametrize("missing_field", ["severity", "category", "text"])
def test_save_ticket_missing_field_raises_value_error(missing_field):
    from meridian.ticket_store import save_ticket
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    del ticket[missing_field]

    with pytest.raises(ValueError):
        save_ticket(ticket)


# --- Edge case 3: bad input to get_ticket ---

@pytest.mark.parametrize("bad_id", [None, "", "   ", 123])
def test_get_ticket_with_bad_id_raises_ticket_not_found(bad_id):
    from meridian.ticket_store import get_ticket, TicketNotFoundError

    with pytest.raises(TicketNotFoundError):
        get_ticket(bad_id)

def test_get_ticket_with_uppercase_id_raises_ticket_not_found():
    from meridian.ticket_store import save_ticket, get_ticket, TicketNotFoundError
    ticket = {"severity": "high", "category": "bug", "text": "Server is down"}
    ticket_id = save_ticket(ticket)

    with pytest.raises(TicketNotFoundError):
        get_ticket(ticket_id.upper())


# --- Edge case 4: ticket that already contains an "id" key ---

def test_id_inside_ticket_is_not_used_for_lookup():
    from meridian.ticket_store import save_ticket, get_ticket, TicketNotFoundError
    ticket = {"id": "abc", "severity": "high", "category": "bug", "text": "Server is down"}
    ticket_id = save_ticket(ticket)

    assert get_ticket(ticket_id) == ticket
    with pytest.raises(TicketNotFoundError):
        get_ticket("abc")
