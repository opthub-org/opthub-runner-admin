"""This module contains test cases for the custom exceptions."""

from opthub_runner_admin.models.exception import DockerError


def test_docker_error() -> None:
    """Test for DockerError."""
    try:
        msg = "TestMessage"
        raise DockerError(msg)
    except DockerError as e:
        expected_msg = msg
        if str(e) != expected_msg:
            msg = f"The exception message {e!s} is not equal to the expected message {expected_msg}."
            raise ValueError(msg) from e
