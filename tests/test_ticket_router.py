from meridian.ticket_router import route_ticket


def test_high_severity_goes_to_tier_2_escalation():
    assert route_ticket("high", "bug") == "tier-2-escalation"


def test_billing_category_goes_to_billing_team():
    assert route_ticket("low", "billing") == "billing-team"


def test_other_tickets_go_to_tier_1_support():
    assert route_ticket("low", "bug") == "tier-1-support"


def test_medium_billing_ticket_goes_to_billing_team():
    assert route_ticket("medium", "billing") == "billing-team"


def test_medium_bug_ticket_goes_to_tier_1_support():
    assert route_ticket("medium", "bug") == "tier-1-support"


def test_high_severity_beats_billing_category():
    assert route_ticket("high", "billing") == "tier-2-escalation"


def test_unknown_severity_goes_to_tier_1_support():
    assert route_ticket("critical", "bug") == "tier-1-support"


def test_unknown_category_goes_to_tier_1_support():
    assert route_ticket("low", "spaceship") == "tier-1-support"


def test_high_severity_with_unknown_category_goes_to_tier_2_escalation():
    assert route_ticket("high", "spaceship") == "tier-2-escalation"


def test_none_severity_does_not_raise():
    assert route_ticket(None, "bug") == "tier-1-support"


def test_none_category_does_not_raise():
    assert route_ticket("low", None) == "tier-1-support"


def test_empty_strings_go_to_tier_1_support():
    assert route_ticket("", "") == "tier-1-support"
