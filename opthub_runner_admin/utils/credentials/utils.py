"""This module contains the methods for context."""

from pathlib import Path


def get_opthub_runner_dir() -> Path:
    """Get the opthub runner directory."""
    opthub_dir = Path.home() / ".opthub_runner"
    opthub_dir.mkdir(exist_ok=True)  # Create the directory if it doesn't exist
    return opthub_dir
