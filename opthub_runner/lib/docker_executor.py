"""Docker Execution Module."""

import json
import logging
from typing import TypedDict

import docker

from opthub_runner.lib.converter import float_to_json_float

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
    *std_in: str,
) -> object | None:
    """Execute command in docker container.

    Args:
        config (DockerConfig): docker image name
        std_in (str): standard input

    Returns:
        object | None: parsed standard output
    """
    LOGGER.info("Connect to docker daemon...")
    client = docker.from_env()
    LOGGER.info("...Connected")

    LOGGER.info("Pull image...")
    client.images.pull(config["image"])  # pull image
    LOGGER.debug(config["image"])
    LOGGER.info("...Pulled")
    # run container
    LOGGER.info("Start container...")

    container = client.containers.run(
        image=config["image"],
        command=config["command"],
        environment=config["environments"],
        std_in_open=True,
        detach=True,
    )
    LOGGER.info("...Started: %s", container.name)

    LOGGER.info("Send variable...")
    socket = container.attach_socket(params={"std_in": 1, "stream": 1, "stdout": 1, "stderr": 1})

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
    out: object = parse_stdout(stdout)

    LOGGER.debug(out)
    LOGGER.info("...Parsed")

    return float_to_json_float(out)


def parse_stdout(stdout: str) -> object | None:
    """Parse stdout.

    Args:
        stdout (str): stdout

    Returns:
        object | None: parsed stdout
    """
    lines = stdout.split("\n")
    lines.reverse()
    for line in lines:
        if line:
            line_object: object = json.loads(line)
            return line_object
    return None
