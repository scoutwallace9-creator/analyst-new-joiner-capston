HIGH_SEVERITY_WORDS = ["outage", "down", "data loss", "security", "breach"]
MEDIUM_SEVERITY_WORDS = ["error", "broken", "slow", "fails"]


def classify_severity(text: str) -> str:
    """
    Classify the severity of a support ticket.
    Returns: "low", "medium", or "high"
    Raises: nothing — returns "low" for empty/None input
    """
    if not text:
        print("Warning: empty ticket text, defaulting to low severity")
        return "low"

    for word in HIGH_SEVERITY_WORDS:
        if word in text:
            return "high"

    for word in MEDIUM_SEVERITY_WORDS:
        if word in text:
            return "medium"

    return "low"


def classify_category(text: str) -> str:
    """
    Classify the category of a support ticket.
    Returns: "bug", "feature_request", "billing", "access_request", or "other"
    """
    raise NotImplementedError
