import re
from typing import NamedTuple, Optional

# A 5xx HTTP status. A bare number is not enough ("500 users", "500 invoices"),
# so it must read like a status code: "500s", "500 error", "status 503".
_HTTP_5XX = r"5\d\d(?:s| errors?| responses?)|(?:http|status|error|code) 5\d\d"

# Patterns are regex fragments matched as whole words (wrapped in \b...\b),
# so "down" won't match "download" and "bug" won't match "debug".
HIGH_PATTERNS = [
    r"urgent", r"critical", r"outages?", r"breach(?:es|ed)?",
    r"data loss", r"production issues?", r"unavailable", r"incidents?",
    r"(?:is|are|was|were|went|goes|been) down",
    r"crash(?:es|ed|ing)?", r"hacked", r"compromised", r"vulnerabilit(?:y|ies)",
    r"(?:cannot|can't|cant|unable to) pay", r"all users", _HTTP_5XX,
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
# A keyword preceded by one of these words is ignored ("not urgent",
# "not a bug", "not really critical", "non-critical").
_NEGATION_RE = re.compile(
    r"\b(?:(?:not|no|never|isn't|isnt|wasn't|wasnt|aren't|arent|weren't|werent)\s+"
    r"(?:(?:a|an|the|any|really|very|that|too|particularly)\s+)*|non-)$"
)

# Scale-of-impact wording that makes a high-severity ticket more certain.
_IMPACT_RE = re.compile(
    r"\b(?:prod(?:uction)?|everyone|\d[\d,]*\+? (?:users|customers|clients|people|accounts))\b"
)
# Hedged, vague or already-resolved wording that makes any label less certain.
_UNCERTAIN_RE = re.compile(
    r"\b(?:maybe|might|perhaps|possibl[ey]|probably|not sure|unsure|i think|i guess"
    r"|seems?|could be|wondering|something|somehow|weird|strange|odd"
    r"|resolved|fixed now|no longer|back up|working again)\b"
)

_BASE_CONFIDENCE = {"high": 0.7, "medium": 0.65, "low": 0.75}
_EXTRA_MATCH_BONUS = 0.1
_IMPACT_BONUS = 0.1
_UNCERTAIN_PENALTY = 0.2
_QUESTION_PENALTY = 0.2
_NEGATED_KEYWORD_PENALTY = 0.15


class _SeverityFields(NamedTuple):
    label: str
    confidence: float


class SeverityResult(_SeverityFields):
    """
    A (label, confidence) tuple that also compares equal to its bare label,
    so callers written against the old str return value keep working:
    classify_severity(t) == "high" and label, confidence = classify_severity(t).
    """

    def __eq__(self, other):
        if isinstance(other, str):
            return self.label == other
        return tuple.__eq__(self, other)

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    __hash__ = tuple.__hash__


def _scan(pattern: re.Pattern, text: str) -> tuple[int, int]:
    """Returns (matches, negated matches) for pattern in text."""
    matched = negated = 0
    for match in pattern.finditer(text):
        if _NEGATION_RE.search(text[:match.start()]):
            negated += 1
        else:
            matched += 1
    return matched, negated


def _count_matches(pattern: re.Pattern, text: str) -> int:
    return _scan(pattern, text)[0]


def classify_severity(text: Optional[str]) -> SeverityResult:
    """
    Classify the severity of a support ticket.
    Returns: (label, confidence) — label is "low", "medium", or "high";
        confidence is a float between 0.0 and 1.0. Tickets below 0.6 should
        be reviewed by a human rather than routed automatically.
    Raises: nothing — returns ("low", 0.0) for empty/None input
    """
    if not text:
        return SeverityResult("low", 0.0)

    normalized = text.lower()
    high, high_negated = _scan(_HIGH_RE, normalized)
    medium, medium_negated = _scan(_MEDIUM_RE, normalized)

    if high:
        label = "high"
        confidence = _BASE_CONFIDENCE[label] + _EXTRA_MATCH_BONUS * (high - 1)
        confidence += _IMPACT_BONUS * len(_IMPACT_RE.findall(normalized))
    elif medium:
        label = "medium"
        confidence = _BASE_CONFIDENCE[label] + _EXTRA_MATCH_BONUS * (medium - 1)
    else:
        label = "low"
        confidence = _BASE_CONFIDENCE[label]
        # "Not urgent" still mentions urgency, so it is less clear-cut than
        # a ticket with no severity wording at all.
        confidence -= _NEGATED_KEYWORD_PENALTY * (high_negated + medium_negated)

    confidence -= _UNCERTAIN_PENALTY * len(_UNCERTAIN_RE.findall(normalized))
    # A question is normal for a low ticket but undercuts a problem report
    # ("is this an outage?", "how do I list all users?").
    if label != "low" and normalized.rstrip().endswith("?"):
        confidence -= _QUESTION_PENALTY

    return SeverityResult(label, round(min(1.0, max(0.0, confidence)), 2))


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
        r"freez(?:es|ing)", r"frozen", _HTTP_5XX,
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
