"""Utility functions for process management."""

import json
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
    flag_file = process_name + ".json"
    base_timeout = 2
    retry_num = 3

    if not Path(flag_file).exists():
        click.echo(f"Flag file {process_name + '.json'} does not exist.")
        sys.exit(1)

    for attempt in range(1, retry_num + 1):
        try:
            timeout = base_timeout**attempt  # exponential backoff
            lock = FileLock(f"{flag_file}.lock", timeout=timeout)
            with lock:  # noqa: SIM117
                with Path(flag_file).open("w") as file:
                    json.dump({"stop_flag": True}, file)
        except Timeout:
            if attempt == retry_num:
                click.echo(f"Failed to stop {process_name}. Try again later.")
                sys.exit(1)
            else:
                click.echo(f"Failed to stop {process_name}. Retrying...")
        except Exception as e:
            click.echo(f"An unexpected error occurred: {e}")
            sys.exit(1)
        else:
            click.echo(f"Successfully stopped {process_name}.")
            break


def is_stop_flag_set(process_name: str) -> bool:
    """Check if the stop flag is set.

    Args:
        process_name (str): The process name.

    Returns:
        bool: True if the process should be stopped, False otherwise.
    """
    flag_file = process_name + ".json"
    base_timeout = 2
    retry_num = 3

    if not Path(flag_file).exists():
        msg = f"Process {process_name} is running, but flag file {flag_file} does not exist."
        raise FileNotFoundError(msg)

    for attempt in range(1, retry_num + 1):
        try:
            timeout = base_timeout**attempt  # exponential backoff
            lock = FileLock(f"{flag_file}.lock", timeout=timeout)

            with lock:  # noqa: SIM117
                with Path(flag_file).open("r") as file:
                    stop_flag: bool = json.load(file)["stop_flag"]
                    from time import sleep

                    sleep(30)
        except Timeout as e:
            if attempt == retry_num:
                msg = f"Failed to read {flag_file}."
                raise Timeout(msg) from e

            msg = f"Failed to read {flag_file}. Retrying..."
            LOGGER.info(msg)

        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            raise Exception(msg) from e

        else:
            msg = f"Successfully read {flag_file}."
            LOGGER.info(msg)
            LOGGER.debug("Stop flag: %d", stop_flag)
            break

    return stop_flag


def create_flag_file(process_name: str, force: bool) -> None:
    """Create the flag file when the process starts.

    Args:
        process_name (str): The process name.
        force (bool): True to force the creation of the flag file, False otherwise.
    """
    flag_file = process_name + ".json"

    if not Path(flag_file).exists():
        with Path(flag_file).open("w") as file:
            json.dump({"stop_flag": False}, file)
        msg = f"Successfully created {flag_file}."
        LOGGER.info(msg)
        from time import sleep

        sleep(10)

    elif Path(flag_file).exists() and not force:
        msg = f"Flag file {flag_file} already exists. Use --force to overwrite."
        raise FileExistsError(msg)

    elif Path(flag_file).exists() and force:
        msg = f"Flag file {flag_file} already exists. Overwriting..."
        LOGGER.warning(msg)

        try:
            with Path(flag_file).open("w") as file:
                json.dump({"stop_flag": False}, file)
            msg = f"Successfully created {flag_file}."
            LOGGER.info(msg)

        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            raise Exception(msg) from e


def delete_flag_file(process_name: str) -> None:
    """Delete the flag file when the process stops.

    Args:
        process_name (str): The process name.
    """
    flag_file = process_name + ".json"
    base_timeout = 2
    retry_num = 3

    for attempt in range(1, retry_num + 1):
        try:
            timeout = base_timeout**attempt  # exponential backoff
            lock = FileLock(f"{flag_file}.lock", timeout=timeout)

            with lock:
                with Path(flag_file).open("r") as file:
                    stop_flag: bool = json.load(file)["stop_flag"]
                if not stop_flag:
                    msg = f"Flag file {flag_file} attempted to be deleted, but the stop flag is set to {stop_flag}."
                    raise Exception(msg)
                Path(flag_file).unlink()
            msg = f"Successfully deleted {flag_file}."
            LOGGER.info(msg)
            break
        except Timeout as e:
            if attempt == retry_num:
                msg = f"Failed to delete {flag_file}."
                raise Timeout(msg) from e

            msg = f"Failed to delete the flag file: {flag_file} ({attempt}/{retry_num}). Retrying..."
            LOGGER.info(msg)

        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            raise Exception(msg) from e
