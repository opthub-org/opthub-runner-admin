"""Definition of CLI commands."""

import logging
import signal
from types import FrameType
from typing import TypedDict

import click

LOGGER = logging.getLogger(__name__)


def signal_handler(sig_num: int, frame: FrameType | None) -> None:  # noqa: ARG001
    """Signal handler."""
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, signal_handler)


class Args(TypedDict):
    """The type of arguments for the CLI."""

    interval: int
    timeout: int
    match_id: str
    rm: bool
    mode: str
    command: list[str]


@click.command(help="OptHub Runner.")
@click.option(
    "-i",
    "--interval",
    envvar="OPTHUB_INTERVAL",
    type=click.IntRange(min=1),
    default=2,
    help="Polling interval.",
)
@click.option(
    "-t",
    "--timeout",
    envvar="OPTHUB_TIMEOUT",
    type=click.IntRange(min=0),
    default=600,
    help="Timeout to process a query.",
)
@click.option(
    "--match_id",
    envvar="OPTHUB_MATCH_ID",
    type=str,
    help="MatchId handled un this server.",
)
@click.option("--rm", envvar="OPTHUB_REMOVE", is_flag=True, help="Remove containers after exit.")
@click.argument("mode", type=click.Choice(["evaluator", "scorer"]))
@click.argument("command", envvar="OPTHUB_COMMAND", type=str, nargs=-1)
@click.pass_context
def run(
    ctx: click.Context,
    interval: int,
    timeout: int,
    match_id: str,
    rm: bool,
    mode: str,
    command: list[str],
) -> None:
    """The entrypoint of CLI."""
    args: Args = {
        "interval": interval,
        "timeout": timeout,
        "match_id": match_id,
        "rm": rm,
        "mode": mode,
        "command": command,
    }
    if args["mode"] == "evaluator":
        from evaluator.main import evaluate

        evaluate(ctx, args)
    elif args["mode"] == "scorer":
        from scorer.main import calculate_score

        calculate_score(ctx, args)
    else:
        msg = f"Invalid mode: {args['mode']}"
        raise ValueError(msg)
