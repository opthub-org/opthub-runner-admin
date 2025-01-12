"""Definition of CLI commands."""

import logging
import signal
import sys
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Any, cast

import click
import yaml
from botocore.exceptions import ClientError

from opthub_runner_admin.utils.credentials.credentials import Credentials
from opthub_runner_admin.utils.docker import check_docker
from opthub_runner_admin.utils.process import create_flag_file

if TYPE_CHECKING:
    from opthub_runner_admin.args import Args


def signal_handler(sig_num: int, frame: FrameType | None) -> None:  # noqa: ARG001
    """Signal handler."""
    raise KeyboardInterrupt


def set_log_level(log_level: str) -> None:
    """Set log level.

    Args:
        log_level (str): Log level. One of "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
    """
    log_level = log_level.upper()
    level_num = getattr(logging, log_level, None)

    if level_num is None:
        msg = f"Invalid log level: {log_level}"
        raise ValueError(msg)

    logging.basicConfig(level=level_num)
    gql_loglevel = max(level_num, logging.WARNING)
    botocore_loglevel = max(level_num, logging.INFO)
    urllib3_loglevel = max(level_num, logging.INFO)
    boto3_loglevel = max(level_num, logging.INFO)

    logging.getLogger("botocore").setLevel(botocore_loglevel)
    logging.getLogger("urllib3").setLevel(urllib3_loglevel)
    logging.getLogger("gql").setLevel(gql_loglevel)
    logging.getLogger("boto3").setLevel(boto3_loglevel)


def load_config(config_file: str) -> dict[str, Any]:
    """Load the configuration file.

    Args:
        config_file (str): The configuration file.

    Returns:
        dict[str, Any]: The configuration.
    """
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return cast(dict[str, Any], config)


def auth(process_name: str, username: str, password: str, dev: bool) -> None:
    """Sign in.

    Args:
        process_name (str): The process name.
        username (str): The username.
        password (str): The password.
        dev (bool): Whether to use the development environment.
    """
    credentials = Credentials(process_name, dev)
    try:
        credentials.cognito_login(username, password)
        click.echo("Successfully signed in.")
    except ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "NotAuthorizedException":
            # user not exist or incorrect password
            click.echo("Authentication failed. Please verify that your username and password are correct.")
        elif error_code == "TooManyRequestsException":
            click.echo("Too many requests. Please try again later.")
        else:
            click.echo(f"An error occurred: {error_code}")
        sys.exit(1)
    except Exception as e:
        # another exception
        click.echo(f"An unexpected error occurred: {e}")
        sys.exit(1)


signal.signal(signal.SIGTERM, signal_handler)


@click.command(help="Start OptHub Runner.")
@click.option(
    "-d",
    "--dev",
    is_flag=True,
    help="Use the development environment.",
)
@click.option(
    "-c",
    "--config",
    type=str,
    help="Configuration file.",
)
@click.argument("mode", type=click.Choice(["evaluator", "scorer"]))
@click.argument("command", envvar="OPTHUB_COMMAND", type=str, nargs=-1)
@click.pass_context
def run(
    ctx: click.Context,
    dev: bool,
    config: str | None,
    mode: str,
    command: list[str],
) -> None:
    """The entrypoint of CLI."""
    process_name = click.prompt("Process Name", type=str)
    # Show the message to the user and ask for the username and password
    click.echo(
        click.style("Note: Make sure to authenticate using the competition administrator's account.", fg="yellow"),
    )
    username = click.prompt("Username", type=str)
    password = click.prompt("Password", type=str, hide_input=True)

    if config is None:
        config = "config.yml" if not dev else "config.dev.yml"

    config_params = load_config(config)

    args: Args = {
        "interval": config_params["interval"],
        "timeout": config_params["timeout"],
        "num": config_params["num"],
        "rm": config_params["rm"],
        "evaluator_queue_url": config_params["evaluator_queue_url"],
        "scorer_queue_url": config_params["scorer_queue_url"],
        "access_key_id": config_params["access_key_id"],
        "secret_access_key": config_params["secret_access_key"],
        "region_name": config_params["region_name"],
        "table_name": config_params["table_name"],
        "mode": mode,
        "command": command,
        "dev": dev,
    }

    check_docker()

    auth(process_name, username, password, dev)

    set_log_level(config_params["log_level"])

    create_flag_file(process_name, config_params["force"])

    if args["mode"] == "evaluator":
        from opthub_runner_admin.evaluator.main import evaluate

        evaluate(process_name, args)
    elif args["mode"] == "scorer":
        from opthub_runner_admin.scorer.main import calculate_score

        calculate_score(process_name, args)
    else:
        msg = f"Invalid mode: {args['mode']}"
        raise ValueError(msg)
