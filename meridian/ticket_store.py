import uuid


class TicketNotFoundError(Exception):
    pass


# In-memory storage: maps ticket ID -> ticket dict
_tickets = {}

REQUIRED_FIELDS = ["severity", "category", "text"]


def save_ticket(ticket: dict) -> str:
    """Save a ticket dict and return its generated ID."""
    if not isinstance(ticket, dict):
        raise TypeError("ticket must be a dict")

    for field in REQUIRED_FIELDS:
        if field not in ticket:
            raise ValueError(f"ticket is missing required field: {field}")

    ticket_id = str(uuid.uuid4())
    _tickets[ticket_id] = dict(ticket)
    return ticket_id


def get_ticket(ticket_id: str) -> dict:
    """Retrieve a ticket by ID. Raises TicketNotFoundError if not found."""
    if ticket_id not in _tickets:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    return dict(_tickets[ticket_id])