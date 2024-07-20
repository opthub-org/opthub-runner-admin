"""This module provides tests for the lib/appsync.py module."""

from opthub_runner_admin.lib.appsync import fetch_match_response_by_match_uuid
from opthub_runner_admin.utils.credentials.credentials import Credentials


def test_fetch_match_response_by_match_uuid() -> None:
    """Test fetch_match_by_match_id function."""
    match_uuid = "5a3fcd7d-3b7e-4a97-bac3-0531cfca538e"

    # "If you run this test, you need to log in as a user participating in the match."
    username = ""
    password = ""

    credentials = Credentials()
    credentials.cognito_login(username, password)

    d = fetch_match_response_by_match_uuid(match_uuid)

    print(d)
