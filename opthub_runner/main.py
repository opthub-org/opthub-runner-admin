"""Definition of CLI commands."""

import logging
import signal
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Any, cast

import click
import yaml

if TYPE_CHECKING:
    from opthub_runner.args import Args

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def signal_handler(sig_num: int, frame: FrameType | None) -> None:  # noqa: ARG001
    """Signal handler."""
    raise KeyboardInterrupt


def load_config(ctx: click.Context, param: click.Parameter, config_file: str) -> dict[str, Any]:
    """Load the configuration file."""
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config: Args = yaml.safe_load(file)

    ctx.default_map = cast(dict[str, Any], config)

    return cast(dict[str, Any], config)


signal.signal(signal.SIGTERM, signal_handler)


@click.command(help="OptHub Runner.")
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
@click.option(
    "--match",
    envvar="OPTHUB_MATCH_ID",
    type=str,
    default=None,
    help="MatchId handled un this server.",
)
@click.option("--rm", envvar="OPTHUB_REMOVE", default=None, is_flag=True, help="Remove containers after exit.")
@click.option(
    "-c",
    "--config",
    envvar="OPTHUB_RUNNER_CONFIG",
    type=click.Path(dir_okay=False),
    default="opthub_runner/opthub-runner.yml",
    callback=load_config,
    help="Configuration file.",
)
@click.argument("mode", type=click.Choice(["evaluator", "scorer"]))
@click.argument("command", envvar="OPTHUB_COMMAND", type=str, nargs=-1)
@click.pass_context
def run(
    ctx: click.Context,
    interval: int,
    timeout: int,
    match: str,
    rm: bool,
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
        "match_alias": match if match is not None else ctx.default_map["match"],
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
    if args["mode"] == "evaluator":
        from opthub_runner.evaluator.main import evaluate

        evaluate(ctx, args)
    elif args["mode"] == "scorer":
        from opthub_runner.scorer.main import calculate_score

        calculate_score(ctx, args)
    else:
        msg = f"Invalid mode: {args['mode']}"
        raise ValueError(msg)
