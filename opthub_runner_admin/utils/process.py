"""Utility functions for process management."""

import logging
import sys
from pathlib import Path

import click
from filelock import FileLock, Timeout

LOGGER = logging.getLogger(__name__)


@click.command(help="Stop OptHub Runner.")
@click.argument("process_name", type=str)
@click.pass_context
def stop(ctx: click.Context, process_name: str) -> None:
    """Stop the process.

    Args:
        ctx (click.Context): The click context.
        process_name (str): The process name.
    """
    flag_file = Path(process_name)
    base_timeout = 2
    retry_num = 3

    if not flag_file.exists():
        click.echo(f"Flag file {process_name} does not exist.")
        sys.exit(1)

    for attempt in range(1, retry_num + 1):
        try:
            timeout = base_timeout**attempt  # exponential backoff
            lock = FileLock(f"{process_name}.lock", timeout=timeout)
            with lock:  # noqa: SIM117
                with flag_file.open("w") as file:
                    file.write("1\n")
        except Timeout:
            if attempt == retry_num:
                click.echo("Failed to stop the process.")
                sys.exit(1)
            else:
                click.echo(f"Failed to stop the process {attempt}/{retry_num}. Retrying...")
        except Exception as e:
            click.echo(f"An unexpected error occurred: {e}")
            sys.exit(1)
        else:
            click.echo("Successfully stopped the process.")
            break


def is_stop_flag_set(process_name: str) -> bool:
    """Check if the stop flag is set.

    Args:
        process_name (str): The process name.

    Returns:
        bool: True if the process should be stopped, False otherwise.
    """
    flag_file = Path(process_name)
    base_timeout = 2
    retry_num = 3

    if not flag_file.exists():
        msg = f"Process {process_name} is running, but flag file {process_name} does not exist."
        LOGGER.exception(msg)
        sys.exit(1)

    for attempt in range(1, retry_num + 1):
        try:
            timeout = base_timeout**attempt  # exponential backoff
            lock = FileLock(f"{process_name}.lock", timeout=timeout)
            with lock:  # noqa: SIM117
                with flag_file.open("r") as file:
                    stop_flag = int(file.read().strip())
        except Timeout:
            if attempt == retry_num:
                msg = f"Failed to read the flag file {process_name}."
                LOGGER.exception(msg)
                sys.exit(1)
            else:
                msg = f"Failed to read the flag file {process_name}."
                LOGGER.exception(msg)
                msg = f"Retry reading the flag file {process_name} {attempt}/{retry_num}."
                LOGGER.info(msg)
        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            LOGGER.exception(msg)
            sys.exit(1)
        else:
            LOGGER.info("Successfully read the flag file.")
            LOGGER.debug("Stop flag: %d", stop_flag)
            break

    return stop_flag == 1


def create_flag_file(process_name: str, force: bool) -> None:
    """Create the flag file when the process starts.

    Args:
        process_name (str): The process name.
        force (bool): True to force the creation of the flag file, False otherwise.
    """
    flag_file = Path(process_name)

    if not flag_file.exists():
        with flag_file.open("w") as file:
            file.write("0\n")
        LOGGER.info("Successfully created the flag file.")

    elif flag_file.exists() and not force:
        msg = f"Flag file {process_name} already exists."
        LOGGER.exception(msg)
        sys.exit(1)

    elif flag_file.exists() and force:
        msg = f"Flag file {process_name} already exists. Forcing the creation of the flag file."
        LOGGER.warning(msg)

        try:
            with flag_file.open("w") as file:
                file.write("0\n")
            LOGGER.info("Successfully created the flag file.")

        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            LOGGER.exception(msg)
            sys.exit(1)
