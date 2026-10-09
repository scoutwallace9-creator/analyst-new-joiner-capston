import pytest

from meridian.ticket_router import route_ticket

CATEGORIES = ("bug", "feature_request", "billing", "access_request", "other")


@pytest.mark.parametrize("category", CATEGORIES)
def test_high_severity_always_escalates(category):
    # Includes "billing": severity is checked before category.
    assert route_ticket("high", category) == "tier-2-escalation"


@pytest.mark.parametrize("severity", ["low", "medium"])
def test_billing_goes_to_billing_team_when_not_high(severity):
    assert route_ticket(severity, "billing") == "billing-team"


@pytest.mark.parametrize("severity", ["low", "medium"])
@pytest.mark.parametrize("category", ["bug", "feature_request", "access_request", "other"])
def test_everything_else_goes_to_tier_1(severity, category):
    assert route_ticket(severity, category) == "tier-1-support"


@pytest.mark.parametrize("severity", ["critical", "", "   ", None])
def test_unknown_severity_routes_to_tier_1(severity):
    assert route_ticket(severity, "bug") == "tier-1-support"


@pytest.mark.parametrize("category", ["hardware", "", "   ", None])
def test_unknown_category_routes_to_tier_1(category):
    assert route_ticket("low", category) == "tier-1-support"


def test_unknown_severity_still_respects_billing_category():
    # An unrecognised severity is just "not high", so the billing rule still applies.
    assert route_ticket("critical", "billing") == "billing-team"


def test_unknown_category_still_escalates_when_high():
    assert route_ticket("high", "hardware") == "tier-2-escalation"


@pytest.mark.parametrize("severity", ["HIGH", "High", "hIgH"])
def test_severity_is_case_insensitive(severity):
    assert route_ticket(severity, "bug") == "tier-2-escalation"


@pytest.mark.parametrize("category", ["BILLING", "Billing", "bIlLiNg"])
def test_category_is_case_insensitive(category):
    assert route_ticket("low", category) == "billing-team"


@pytest.mark.parametrize("severity", ["  high  ", "\thigh\n"])
def test_severity_ignores_surrounding_whitespace(severity):
    assert route_ticket(severity, "bug") == "tier-2-escalation"


@pytest.mark.parametrize("category", ["  billing  ", "\tbilling\n"])
def test_category_ignores_surrounding_whitespace(category):
    assert route_ticket("low", category) == "billing-team"


@pytest.mark.parametrize("severity", ["highest", "not high", "hi gh"])
def test_severity_must_match_whole_value(severity):
    # Only the exact label escalates; near-misses are unknown values.
    assert route_ticket(severity, "bug") == "tier-1-support"


@pytest.mark.parametrize("category", ["billing_dispute", "non-billing", "bill"])
def test_category_must_match_whole_value(category):
    assert route_ticket("low", category) == "tier-1-support"


@pytest.mark.parametrize("value", [42, True, ["high"], b"billing"])
def test_non_string_inputs_do_not_raise(value):
    assert route_ticket(value, "bug") == "tier-1-support"
    assert route_ticket("low", value) == "tier-1-support"
