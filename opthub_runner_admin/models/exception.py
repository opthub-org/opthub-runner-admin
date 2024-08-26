"""This module contains the custom exceptions for the application."""

import sys
from enum import Enum

import click


class AuthenticationErrorMessage(Enum):
    """Enum class for authentication error types."""

    LOGIN_FAILED = "Login failed. Please check your Username or Password."
    GET_JWKS_PUBLIC_KEY_FAILED = "Failed to get public key. Please try again later."
    LOAD_CREDENTIALS_FAILED = "Not found credentials. Please login with `opt login` command."
    REFRESH_FAILED = "Could not refresh access token. Please login again with `opt login` command."
    DECODE_JWT_TOKEN_FAILED = "Failed to decode JWT token. Please try again later."  # noqa: S105


class ContainerRuntimeError(Exception):
    """Exception raised for errors in the docker execution."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)


class AuthenticationError(Exception):
    """Exception raised for authentication related errors."""

    def __init__(self, error_type: AuthenticationErrorMessage) -> None:
        """Initialize the AuthenticationError class."""
        super().__init__(error_type.value)

    def handler(self) -> None:
        """Handle the GraphQL error."""
        click.echo(str(self))
        sys.exit(1)


class DockerImageNotFoundError(Exception):
    """Exception raised when the Docker image is not found. It may occur if you lack the permissions to access it."""

    def __init__(self) -> None:
        """Initialize the exception."""
        msg = (
            "Cannot access the Docker image. Please check your permissions. "
            "If you're not authenticated using the competition administrator's account, please do so."
        )
        super().__init__(msg)
