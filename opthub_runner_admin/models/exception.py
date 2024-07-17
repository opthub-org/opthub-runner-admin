"""This module contains the custom exceptions for the application."""


class DockerError(Exception):
    """Exception raised for errors in the docker execution."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
