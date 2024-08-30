"""Utility functions for datetime."""

from datetime import UTC, datetime


def get_utcnow() -> str:
    """Get the current datetime.

    Returns:
        str: The current datetime.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
