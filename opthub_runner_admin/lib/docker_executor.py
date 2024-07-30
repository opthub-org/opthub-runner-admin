"""Docker Execution Module."""

import json
import logging
from typing import Any, TypedDict, cast

import docker
from docker.errors import APIError

from opthub_runner_admin.utils.converter import float_to_json_float

LOGGER = logging.getLogger(__name__)


class DockerConfig(TypedDict):
    """A type for docker execution configuration."""

    image: str
    environments: dict[str, str]
    command: list[str]
    timeout: float
    rm: bool


def execute_in_docker(
    config: DockerConfig,
    std_in: list[str],
) -> dict[str, Any]:
    """Execute command in docker container.

    Args:
        config (DockerConfig): docker image name
        std_in (list[str]): standard input

    Returns:
        dict[str, Any]: parsed standard output
    """
    LOGGER.info("Connect to docker daemon...")
    client = docker.from_env()
    LOGGER.info("...Connected")

    LOGGER.info("Pull image...")
    try:
        client.images.pull(config["image"])  # pull image
    except APIError:
        client.images.get(config["image"])  # If image in local, get it

    LOGGER.debug(config["image"])
    LOGGER.info("...Pulled")
    # run container
    LOGGER.info("Start container...")

    container = client.containers.run(
        image=config["image"],
        command=config["command"],
        environment=config["environments"],
        stdin_open=True,
        detach=True,
    )
    LOGGER.info("...Started: %s", container.name)

    LOGGER.info("Send variable...")
    socket = container.attach_socket(params={"stdin": 1, "stream": 1, "stdout": 1, "stderr": 1})

    for line in std_in:
        socket._sock.sendall(line.encode("utf-8"))  # noqa: SLF001
    LOGGER.info("...Send")

    LOGGER.info("Wait for execution...")
    container.wait(timeout=config["timeout"])
    LOGGER.info("...Executed")

    LOGGER.info("Receive stdout...")
    stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
    LOGGER.debug(stdout)
    LOGGER.info("...Received")

    if config["rm"]:
        LOGGER.info("Remove container...")
        container.remove()
        LOGGER.info("...Removed")

    LOGGER.info("Parse stdout...")
    out: dict[str, Any] | None = parse_stdout(stdout)

    if out is None:
        msg = "Failed to parse stdout."
        raise RuntimeError(msg)

    LOGGER.debug(out)
    LOGGER.info("...Parsed")

    return cast(dict[str, Any], float_to_json_float(out))


def parse_stdout(stdout: str) -> dict[str, Any] | None:
    """Parse stdout.

    Args:
        stdout (str): stdout

    Returns:
        dict[str, Any] | None: parsed stdout
    """
    lines = stdout.split("\n")
    lines.reverse()
    for line in lines:
        if line:
            line_dict: dict[str, Any] = json.loads(line)
            return line_dict
    return None
