import pytest

from meridian.ticket_classifier import classify_severity


def test_empty_string_returns_low():
    assert classify_severity("") == "low"


def test_none_returns_low():
    assert classify_severity(None) == "low"


def test_empty_string_prints_warning(capsys):
    classify_severity("")

    captured = capsys.readouterr()
    assert "Warning" in captured.out


def test_same_input_returns_same_label():
    first = classify_severity("The login page is broken")
    second = classify_severity("The login page is broken")

    assert first == second


@pytest.mark.parametrize("text", [
    "We have a full outage in production",
    "The whole site is down",
    "Customer reports data loss after the update",
    "Possible security issue with the login form",
    "We think there was a breach last night",
])
def test_high_severity_words_return_high(text):
    assert classify_severity(text) == "high"


@pytest.mark.parametrize("text", [
    "I get an error when saving my profile",
    "The export button is broken",
    "The dashboard is very slow today",
    "Uploading a file fails every time",
])
def test_medium_severity_words_return_medium(text):
    assert classify_severity(text) == "medium"
