"""This module contains test cases for the custom exceptions."""

from opthub_runner_admin.models.exception import ContainerRuntimeError


def test_container_runtime_error() -> None:
    """Test for ContainerRuntimeError."""
    try:
        msg = "TestMessage"
        raise ContainerRuntimeError(msg)
    except ContainerRuntimeError as e:
        expected_msg = msg
        if str(e) != expected_msg:
            msg = f"The exception message {e!s} is not equal to the expected message {expected_msg}."
            raise ValueError(msg) from e
