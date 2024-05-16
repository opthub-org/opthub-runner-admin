"""This module provides tests for the models/match.py module."""

from opthub_runner.models.match import fetch_match_by_id
from opthub_runner.utils.credentials import Credentials


def test_fetch_match_by_id() -> None:
    """Test the fetch_match_by_match_id function."""
    # "If you run this test, you need to log in as a user participating in the match."
    username = ""
    password = ""

    credentials = Credentials()
    credentials.cognito_login(username, password)
    match = fetch_match_by_id("Match#5a3fcd7d-3b7e-4a97-bac3-0531cfca538e")
    print(match)
