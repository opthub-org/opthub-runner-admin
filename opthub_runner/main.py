"""Definition of CLI commands."""

import logging
import signal
from types import FrameType

import click

LOGGER = logging.getLogger(__name__)


def signal_handler(sig_num: int, frame: FrameType | None) -> None:  # noqa: ARG001
    """Signal handler."""
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, signal_handler)


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
    # set loglevel
    verbosity = 10 * (kwargs["quiet"] - kwargs["verbose"])
    log_level = 0  # logging.WARNING + verbosity
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
    )
    LOGGER.info("Log level is set to %d", log_level)
    LOGGER.debug("run(%s)", kwargs)

    if kwargs["mode"] == "evaluator":
        from evaluator.main import evaluate

        evaluate(ctx, **kwargs)
    elif kwargs["mode"] == "scorer":
        from scorer.main import calculate_score

        calculate_score(ctx, **kwargs)
    else:
        raise ValueError(f'Illegal mode: {kwargs["mode"]}')


run()
