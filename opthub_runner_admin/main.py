"""Definition of CLI commands."""

import logging
import signal
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Any, cast

import click
import yaml
from botocore.exceptions import ClientError

from opthub_runner_admin.utils.credentials import Credentials

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
    logging.getLogger("gql").setLevel(gql_loglevel)


def load_config(ctx: click.Context, param: click.Parameter, config_file: str) -> dict[str, Any]:
    """Load the configuration file."""
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config: Args = yaml.safe_load(file)

    ctx.default_map = cast(dict[str, Any], config)

    return cast(dict[str, Any], config)


def auth(username: str, password: str) -> None:
    """Sign in."""
    credentials = Credentials()
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
    except Exception as e:
        # another exception
        click.echo(f"An unexpected error occurred: {e}")


signal.signal(signal.SIGTERM, signal_handler)


@click.command(help="OptHub Runner.")
@click.option("--username", "-u", "username", required=True, prompt=True)
@click.option("--password", "-p", "password", prompt=True, hide_input=True)
@click.option(
    "-i",
    "--interval",
    envvar="OPTHUB_INTERVAL",
    type=click.IntRange(min=1),
    default=None,
    help="Polling interval.",
)
@click.option(
    "-t",
    "--timeout",
    envvar="OPTHUB_TIMEOUT",
    type=click.IntRange(min=0),
    default=None,
    help="Timeout to process a query.",
)
@click.option("--rm", envvar="OPTHUB_REMOVE", default=None, is_flag=True, help="Remove containers after exit.")
@click.option(
    "--log_level",
    envvar="OPTHUB_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default=None,
    help="Log level.",
)
@click.option(
    "-c",
    "--config",
    envvar="OPTHUB_RUNNER_CONFIG",
    type=click.Path(dir_okay=False),
    default="config.yml",
    callback=load_config,
    help="Configuration file.",
)
@click.argument("mode", type=click.Choice(["evaluator", "scorer"]))
@click.argument("command", envvar="OPTHUB_COMMAND", type=str, nargs=-1)
@click.pass_context
def run(
    ctx: click.Context,
    username: str,
    password: str,
    interval: int,
    timeout: int,
    rm: bool,
    log_level: str,
    config: str,
    mode: str,
    command: list[str],
) -> None:
    """The entrypoint of CLI."""
    if ctx.default_map is None:
        msg = "Configuration file is not loaded."
        raise ValueError(msg)
    args: Args = {
        "interval": interval if interval is not None else ctx.default_map["interval"],
        "timeout": timeout if timeout is not None else ctx.default_map["timeout"],
        "rm": rm if rm is not None else ctx.default_map["rm"],
        "evaluator_queue_name": ctx.default_map["evaluator_queue_name"],
        "evaluator_queue_url": ctx.default_map["evaluator_queue_url"],
        "scorer_queue_name": ctx.default_map["scorer_queue_name"],
        "scorer_queue_url": ctx.default_map["scorer_queue_url"],
        "access_key_id": ctx.default_map["access_key_id"],
        "secret_access_key": ctx.default_map["secret_access_key"],
        "region_name": ctx.default_map["region_name"],
        "table_name": ctx.default_map["table_name"],
        "mode": mode,
        "command": command,
    }

    auth(username, password)

    log_level = log_level if log_level is not None else ctx.default_map["log_level"]

    set_log_level(log_level)

    if args["mode"] == "evaluator":
        from opthub_runner_admin.evaluator.main import evaluate

        evaluate(ctx, args)
    elif args["mode"] == "scorer":
        from opthub_runner_admin.scorer.main import calculate_score

        calculate_score(ctx, args)
    else:
        msg = f"Invalid mode: {args['mode']}"
        raise ValueError(msg)
