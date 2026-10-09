def _normalise(value) -> str:
    """Lowercase and trim a label; anything that is not a string becomes ""."""
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def route_ticket(severity: str, category: str) -> str:
    """
    Route a ticket to the appropriate support team.
    Returns: team name string
    Routing rules:
      - severity "high": always "tier-2-escalation"
      - category "billing": "billing-team"
      - all others: "tier-1-support"
    Matching ignores case and surrounding whitespace. Unknown or non-string
    values never raise; they fall through to "tier-1-support".
    """
    if _normalise(severity) == "high":
        return "tier-2-escalation"
    if _normalise(category) == "billing":
        return "billing-team"
    return "tier-1-support"
