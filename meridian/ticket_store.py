import copy
import uuid

_tickets: dict[str, dict] = {}


class TicketNotFoundError(Exception):
    pass


def save_ticket(ticket: dict) -> str:
    """Save a ticket dict and return its generated ID."""
    ticket_id = str(uuid.uuid4())
    # Store a copy so later changes to the caller's dict do not alter saved state.
    _tickets[ticket_id] = copy.deepcopy(ticket)
    return ticket_id


def get_ticket(ticket_id: str) -> dict:
    """Retrieve a ticket by ID. Raises TicketNotFoundError if not found."""
    if not isinstance(ticket_id, str) or ticket_id not in _tickets:
        raise TicketNotFoundError(f"No ticket found with ID {ticket_id!r}")
    return copy.deepcopy(_tickets[ticket_id])
