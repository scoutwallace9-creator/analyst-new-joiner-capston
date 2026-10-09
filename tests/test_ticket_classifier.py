from meridian.ticket_classifier import classify_category, classify_severity


def test_classify_severity_is_callable():
    try:
        classify_severity("test")
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_severity_returns_valid_label():
    try:
        result = classify_severity("Something happened with my account")
        assert result in ("low", "medium", "high"), f"Invalid label: {result}"
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_severity_high_keywords():
    tickets = [
        "URGENT: payment page is broken",
        "Critical failure in checkout",
        "Full outage across EU region",
        "The website is down",
        "Possible security breach detected",
        "Customer reported data loss after sync",
        "Production issue affecting all users",
        "Service unavailable since 9am",
        "Raising an incident for the API",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "high", f"Expected 'high' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_medium_keywords():
    tickets = [
        "Getting an error when saving",
        "Small bug in the report filter",
        "Dashboard is slow to load",
        "Export failed last night",
        "Can't log in to my account",
        "Search is not working",
        "Request timeout on the reports page",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "medium", f"Expected 'medium' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_low_for_general_requests():
    tickets = [
        "Can you add a dark mode?",
        "Please update my billing address",
        "Thanks for the help yesterday",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "low", f"Expected 'low' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_empty_and_none_input():
    for value in ("", None):
        try:
            result = classify_severity(value)
            assert result == "low", f"Expected 'low' for {value!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {value!r}: {e}")


def test_classify_severity_is_case_insensitive():
    try:
        assert classify_severity("CRITICAL") == "high"
        assert classify_severity("critical") == "high"
        assert classify_severity("CrItIcAl") == "high"
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_severity_high_wins_over_medium():
    try:
        result = classify_severity("Urgent: login error on production")
        assert result == "high", f"Expected 'high', got {result!r}"
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_severity_ignores_keywords_inside_other_words():
    tickets = [
        "Where can I download the invoice?",
        "Please downgrade my plan",
        "Incidentally, can you add CSV export?",
        "Debug mode toggle request",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "low", f"Expected 'low' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_ignores_harmless_uses_of_vague_words():
    tickets = [
        "How do I change my security question?",
        "How do I update my login email?",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "low", f"Expected 'low' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_handles_negation():
    tickets = [
        "Not urgent, just a question",
        "No outage, just wondering about the maintenance window",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "low", f"Expected 'low' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_catches_serious_tickets_without_old_keywords():
    tickets = [
        "App crashes on startup",
        "Customers cannot pay",
        "We were hacked",
        "All users getting 500s",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "high", f"Expected 'high' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_catches_broken_and_access_problems():
    tickets = [
        "Everything is broken",
        "Cannot access my account",
    ]
    for ticket in tickets:
        try:
            result = classify_severity(ticket)
            assert result == "medium", f"Expected 'medium' for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_severity_returns_label_and_confidence_tuple():
    result = classify_severity("Getting an error when saving")
    assert isinstance(result, tuple) and len(result) == 2
    label, confidence = result
    assert label == "medium"
    assert isinstance(confidence, float)


def test_classify_severity_confidence_is_between_zero_and_one():
    tickets = [
        "",
        None,
        "Thanks for the help yesterday",
        "Getting an error when saving",
        "The website is down",
        # stacks every bonus
        "URGENT critical outage: production is down, data loss, 5000 users affected, everyone hacked",
        # stacks every penalty
        "Maybe something weird, not sure, might possibly be odd, seems strange, perhaps a bug?",
    ]
    for ticket in tickets:
        label, confidence = classify_severity(ticket)
        assert label in ("low", "medium", "high")
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0, f"Out of range for {ticket!r}: {confidence}"


def test_classify_severity_clearly_severe_ticket_has_high_confidence():
    tickets = [
        "production database is down, 500 users affected",
        "URGENT: full outage in production, all users affected",
        "Critical security breach, customer data compromised",
    ]
    for ticket in tickets:
        label, confidence = classify_severity(ticket)
        assert label == "high", f"Expected 'high' for {ticket!r}, got {label!r}"
        assert confidence >= 0.8, f"Expected >= 0.8 for {ticket!r}, got {confidence}"


def test_classify_severity_ambiguous_ticket_has_low_confidence():
    tickets = [
        "Something happened with my account",
        "Not sure if this is urgent, the site might be slow?",
        "Maybe a bug, something looks weird",
        "Is this an outage?",
        "The outage is resolved, thanks",
        "How do I export a list of all users?",
    ]
    for ticket in tickets:
        _, confidence = classify_severity(ticket)
        assert confidence < 0.6, f"Expected < 0.6 for {ticket!r}, got {confidence}"


def test_classify_severity_plain_tickets_are_confident_enough_to_route():
    tickets = [
        "The website is down",
        "Getting an error when saving",
        "Can you add a dark mode?",
        "Please update my billing address",
    ]
    for ticket in tickets:
        _, confidence = classify_severity(ticket)
        assert confidence >= 0.6, f"Expected >= 0.6 for {ticket!r}, got {confidence}"


def test_classify_severity_empty_input_has_zero_confidence():
    for value in ("", None):
        assert classify_severity(value) == ("low", 0.0)


def test_classify_severity_more_evidence_means_more_confidence():
    _, one_signal = classify_severity("The website is down")
    _, two_signals = classify_severity("Urgent: the website is down")
    _, with_impact = classify_severity("Urgent: the website is down for 2,000 customers")
    assert one_signal < two_signals < with_impact


def test_classify_severity_false_statements_are_not_flagged():
    # The ticket says the problem is NOT happening, so it must not be raised.
    tickets = [
        "The site is not down",
        "This is not critical",
        "Not really urgent, just checking in",
        "A non-critical question about exports",
        "There was no data loss",
        "No outages on our side",
        "It isn't a bug",
        "No errors, the export went fine",
        "This was never an incident",
    ]
    for ticket in tickets:
        label, _ = classify_severity(ticket)
        assert label == "low", f"Expected 'low' for {ticket!r}, got {label!r}"


def test_classify_severity_negation_does_not_hide_a_real_problem():
    # A negated keyword must not cancel a different, un-negated one.
    assert classify_severity("Not urgent, but the export failed")[0] == "medium"
    assert classify_severity("No data loss, but the site is down")[0] == "high"


def test_classify_severity_plain_numbers_are_not_http_errors():
    tickets = [
        "I have 500 invoices to upload",
        "We added 520 seats this month",
        "Please raise our limit to 503 contacts",
    ]
    for ticket in tickets:
        label, _ = classify_severity(ticket)
        assert label == "low", f"Expected 'low' for {ticket!r}, got {label!r}"
    for ticket in ("Getting a 500 error on the dashboard", "API returns status 503"):
        label, _ = classify_severity(ticket)
        assert label == "high", f"Expected 'high' for {ticket!r}, got {label!r}"


def test_classify_category_plain_numbers_are_not_bugs():
    _assert_category(["I need a refund of 500 dollars"], "billing")
    _assert_category(["Getting a 500 error on the dashboard"], "bug")


VALID_CATEGORIES = ("bug", "feature_request", "billing", "access_request", "other")


def _assert_category(tickets, expected):
    for ticket in tickets:
        try:
            result = classify_category(ticket)
            assert result == expected, f"Expected {expected!r} for {ticket!r}, got {result!r}"
        except NotImplementedError:
            pass  # expected — scaffold not yet implemented
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Unexpected error for {ticket!r}: {e}")


def test_classify_category_is_callable():
    try:
        classify_category("test")
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_category_returns_valid_label():
    try:
        result = classify_category("Something happened with my account")
        assert result in VALID_CATEGORIES, f"Invalid label: {result}"
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_category_bug():
    _assert_category([
        "The app crashes when I open settings",
        "Getting a 500 error on the dashboard",
        "Export button is not working",
        "Report page stopped loading after the update",
        "The search feature is broken",
    ], "bug")


def test_classify_category_feature_request():
    _assert_category([
        "Can you add a dark mode?",
        "It would be nice to export reports as PDF",
        "Feature request: bulk edit tickets",
        "We would like integration with Slack",
    ], "feature_request")


def test_classify_category_billing():
    _assert_category([
        "I was charged twice this month",
        "Where can I download my invoice?",
        "I need a refund",
        "Please downgrade my plan",
        "My credit card was declined",
    ], "billing")


def test_classify_category_access_request():
    _assert_category([
        "I need access to the finance dashboard",
        "Cannot access my account",
        "I forgot my password",
        "My account is locked",
        "Please add me to the analytics team",
        "Can you give me admin rights?",
    ], "access_request")


def test_classify_category_other():
    _assert_category([
        "Thanks for the help yesterday",
        "What are your support hours?",
        "How do I update my login email?",
    ], "other")


def test_classify_category_empty_and_none_input():
    _assert_category(["", None], "other")


def test_classify_category_is_case_insensitive():
    _assert_category(["I NEED A REFUND", "i need a refund", "I Need A Refund"], "billing")


def test_classify_category_ignores_keywords_inside_other_words():
    # "plan" in "planned", "bug" in "debug", "bill" in "billboard"
    _assert_category([
        "Incidentally, the planned maintenance went fine",
        "Love the new billboard campaign",
    ], "other")
    try:
        result = classify_category("Debug mode toggle request")
        assert result != "bug", f"'debug' should not count as 'bug', got {result!r}"
    except NotImplementedError:
        pass  # expected — scaffold not yet implemented
    except AssertionError:
        raise
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")


def test_classify_category_handles_negation():
    _assert_category(["No errors, just a question about pricing"], "billing")
    _assert_category(["Not a bug, but could you add a filter?"], "feature_request")


def test_classify_category_mixed_signals_pick_the_right_category():
    # Each ticket mentions keywords from two categories.
    _assert_category(["Payment page throws an error"], "bug")
    _assert_category(["Can you add PayPal as a payment option?"], "feature_request")
    _assert_category(["Can you add a new user with admin permissions?"], "access_request")
    _assert_category(["Please add support for SSO"], "feature_request")
