"""
Definition of CLI commands.

"""
import logging
import signal
from os import path

import click
import yaml
from click.types import StringParamType
from evaluator import evaluator
from scorer import scorer

LOGGER = logging.getLogger(__name__)


class AliasedGroup(click.Group):
    """
    A Click group with short subcommands.

    Example
    -------
    >>> @click.command(cls=AliasedGroup)
    >>> def long_name_command():
    ...     pass
    """

    def get_command(
        self, ctx, cmd_name
    ):  # pylint: disable=inconsistent-return-statements
        cmd = click.Group.get_command(self, ctx, cmd_name)
        if cmd is not None:
            return cmd
        matches = [cmd for cmd in self.list_commands(ctx) if cmd.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail("Too many matches: %s" % ", ".join(sorted(matches)))


class StrLength(StringParamType):
    """A Click option type of string with length validation.

    This is basically the same as `str`, except for additional
    functionalities of length validation.
    
    """

    def __init__(
        self, min=None, max=None, clamp=False
    ):  # pylint: disable=redefined-builtin
        self.min = min
        self.max = max
        self.clamp = clamp

    def convert(self, value, param, ctx):
        ret = StringParamType.convert(self, value, param, ctx)
        len_ret = len(ret)
        if self.clamp:
            if self.min is not None and len_ret < self.min:
                return ret + " " * (self.min - len_ret)
            if self.max is not None and len_ret > self.max:
                return ret[: self.max]
        if (
            self.min is not None
            and len_ret < self.min
            or self.max is not None
            and len_ret > self.max
        ):
            if self.min is None:
                self.fail(
                    "Length %d is longer than the maximum valid length %d."
                    % (len_ret, self.max),
                    param,
                    ctx,
                )
            elif self.max is None:
                self.fail(
                    "Length %d is shorter than the minimum valid length %d."
                    % (len_ret, self.min),
                    param,
                    ctx,
                )
            else:
                self.fail(
                    "Length %d is not in the valid range of %d to %d."
                    % (len_ret, self.min, self.max),
                    param,
                    ctx,
                )
        return ret

    def __repr__(self):
        return "StrLength(%d, %d)" % (self.min, self.max)

def load_config(ctx, self, value):  # pylint:disable=unused-argument
    """
    Load `ctx.default_map` from a file.

    """

    if not path.exists(value):
        return {}
    with open(value, encoding="utf-8") as file:
        ctx.default_map = yaml.safe_load(file)
    return ctx.default_map


def save_config(ctx, value):
    """
    Save `ctx.default_map` to a file.

    :param ctx: Click context
    :param value: File name
    :return dict: Saved config
    """

    with open(value, "w", encoding="utf-8") as file:
        yaml.dump(ctx.default_map, file)
    return ctx.default_map


def signal_handler(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, signal_handler)


@click.command(help="OptHub Evaluator.")
@click.option(
    "-u",
    "--url",
    envvar="OPTHUB_URL",
    type=str,
    default="https://opthub-api.herokuapp.com/v1/graphql",
    help="URL to OptHub.",
)
@click.option(
    "-a", "--apikey", envvar="OPTHUB_APIKEY", type=StrLength(max=64), help="ApiKey."
)
@click.option(
    "-i",
    "--interval",
    envvar="OPTHUB_INTERVAL",
    type=click.IntRange(min=1),
    default=2,
    help="Polling interval.",
)
@click.option(
    "--verify/--no-verify",
    envvar="OPTHUB_VERIFY",
    default=True,
    help="Verify SSL certificate.",
)
@click.option(
    "-r",
    "--retries",
    envvar="OPTHUB_RETRIES",
    type=click.IntRange(min=0),
    default=3,
    help="Retries to establish HTTPS connection.",
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
    "--rm", envvar="OPTHUB_REMOVE", is_flag=True, help="Remove containers after exit."
)
@click.option(
    "-b",
    "--backend",
    envvar="OPTHUB_BACKEND",
    type=click.Choice(["docker", "singularity"]),
    default="docker",
    help="Container backend.",
)
@click.option("-q", "--quiet", count=True, help="Be quieter.")
@click.option("-v", "--verbose", count=True, help="Be more verbose.")
@click.option(
    "-c",
    "--config",
    envvar="OPTHUB_EVALUATOR_CONFIG",
    type=click.Path(dir_okay=False),
    default="opthub-evaluator.yml",
    is_eager=True,
    callback=load_config,
    help="Configuration file.",
)
@click.version_option()
@click.argument("mode", type=click.Choice(["evaluator", "scorer"]))
@click.argument("command", envvar="OPTHUB_COMMAND", type=str, nargs=-1)
@click.pass_context
def run(ctx, **kwargs):
    """
    The entrypoint of CLI.

    """
    if kwargs["backend"] == "docker":
        run_docker(ctx, **kwargs)
    elif kwargs["backend"] == "singularity":
        raise NotImplementedError("Singularity is not implemented.")
    else:
        raise ValueError(f'Illegal backend: {kwargs["backend"]}')
    
def run_docker(ctx, **kwargs):
    # set loglevel
    verbosity = 10 * (kwargs["quiet"] - kwargs["verbose"])
    log_level = 0#logging.WARNING + verbosity
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
    )
    LOGGER.info("Log level is set to %d", log_level)
    LOGGER.debug("run(%s)", kwargs)

    if kwargs["mode"] == "evaluator":
        evaluator(ctx, **kwargs)
    elif kwargs["mode"] == "scorer":
        scorer(ctx, **kwargs)
    else:
        raise ValueError(f'Illegal mode: {kwargs["mode"]}')


run()