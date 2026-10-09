import re
from typing import Optional

# Patterns are regex fragments matched as whole words (wrapped in \b...\b),
# so "down" won't match "download" and "bug" won't match "debug".
HIGH_PATTERNS = [
    r"urgent", r"critical", r"outages?", r"breach(?:es|ed)?",
    r"data loss", r"production issues?", r"unavailable", r"incidents?",
    r"(?:is|are|was|were|went|goes|been) down",
    r"crash(?:es|ed|ing)?", r"hacked", r"compromised", r"vulnerabilit(?:y|ies)",
    r"(?:cannot|can't|cant|unable to) pay", r"all users", r"5\d\d(?:s| errors?)?",
]
MEDIUM_PATTERNS = [
    r"errors?", r"issues?", r"bugs?", r"slow", r"warnings?", r"failed",
    r"failing", r"degraded", r"not working", r"delay(?:s|ed)?",
    r"timeouts?", r"timed out", r"broken",
    r"(?:cannot|can't|cant|unable to) (?:access|log ?in|sign ?in)",
    r"(?:login|log in|sign in) (?:failed|failing|error|issue)s?",
]

_HIGH_RE = re.compile(r"\b(?:" + "|".join(HIGH_PATTERNS) + r")\b")
_MEDIUM_RE = re.compile(r"\b(?:" + "|".join(MEDIUM_PATTERNS) + r")\b")
# A keyword directly preceded by one of these words is ignored ("not urgent",
# "not a bug").
_NEGATION_RE = re.compile(r"\b(?:not|no|never|isn't|wasn't)\s+(?:(?:a|an|the)\s+)?$")


def _count_matches(pattern: re.Pattern, text: str) -> int:
    return sum(
        1 for match in pattern.finditer(text)
        if not _NEGATION_RE.search(text[:match.start()])
    )


def _has_match(pattern: re.Pattern, text: str) -> bool:
    return _count_matches(pattern, text) > 0


def classify_severity(text: Optional[str]) -> str:
    """
    Classify the severity of a support ticket.
    Returns: "low", "medium", or "high"
    Raises: nothing — returns "low" for empty/None input
    """
    if not text:
        return "low"

    normalized = text.lower()
    if _has_match(_HIGH_RE, normalized):
        return "high"
    if _has_match(_MEDIUM_RE, normalized):
        return "medium"
    return "low"


# Ordered by tie-break priority: when two categories score equally, the
# earlier one wins (e.g. "payment page throws an error" is a bug, and
# "can you add PayPal as a payment option" is a feature request).
CATEGORY_PATTERNS = {
    "access_request": [
        r"access to", r"(?:request|need|grant|give me|remove|revoke) access",
        r"(?:cannot|can't|cant|unable to) (?:access|log ?in|sign ?in)",
        r"permissions?", r"admin rights", r"roles?", r"locked out",
        r"account (?:is )?locked", r"(?:reset|forgot|change) (?:my )?password",
        r"add (?:me|them|him|her|users?|[a-z]+@[a-z.]+) to", r"invite",
        r"2fa", r"mfa", r"sso",
    ],
    "bug": [
        r"bugs?", r"errors?", r"exceptions?", r"crash(?:es|ed|ing)?",
        r"broken", r"glitch(?:es|y)?", r"not working", r"not loading",
        r"(?:doesn't|does not|isn't|won't|stopped) (?:work|working|load|loading)",
        r"fail(?:s|ed|ing)?", r"timeouts?", r"timed out",
        r"freez(?:es|ing)", r"frozen", r"5\d\d(?:s| errors?)?",
    ],
    "feature_request": [
        r"features?", r"feature requests?", r"enhancements?",
        r"(?:can|could|would) you (?:please )?add", r"please add",
        r"would (?:like|love)", r"it would be (?:nice|great|helpful|useful)",
        r"suggest(?:ion|ions)?", r"support for", r"ability to", r"option to",
        r"integrat(?:e|ion) with",
    ],
    "billing": [
        r"bill(?:s|ed|ing)?", r"invoices?", r"charge(?:s|d)?", r"overcharged",
        r"payments?", r"refunds?", r"subscriptions?", r"pricing", r"prices?",
        r"receipts?", r"credit card", r"plans?",
        r"(?:cannot|can't|cant|unable to) pay",
    ],
}

_CATEGORY_RES = {
    category: re.compile(r"\b(?:" + "|".join(patterns) + r")\b")
    for category, patterns in CATEGORY_PATTERNS.items()
}


def classify_category(text: Optional[str]) -> str:
    """
    Classify the category of a support ticket.
    Returns: "bug", "feature_request", "billing", "access_request", or "other"
    Raises: nothing — returns "other" for empty/None input
    """
    if not text:
        return "other"

    normalized = text.lower()
    best_category, best_score = "other", 0
    for category, pattern in _CATEGORY_RES.items():
        score = _count_matches(pattern, normalized)
        if score > best_score:  # strict ">" keeps the earlier category on ties
            best_category, best_score = category, score
    return best_category
