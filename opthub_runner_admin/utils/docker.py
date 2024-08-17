"""This module provides utility functions for Docker."""

import sys

import click
import docker
from docker.errors import DockerException


def check_docker() -> None:
    """Check if Docker is running and accessible."""
    try:
        client = docker.from_env()
        client.ping()
    except DockerException as error:
        click.echo(
            f"Error: Unable to communicate with Docker. Please ensure Docker is running and accessible. ({error!s})",
        )
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
        sys.exit(1)
