import docker
import json
from utils.converter import float_to_json_float
import logging

LOGGER = logging.getLogger(__name__)


def execute_in_docker(image, environment, command, timeout, rm, *std_in):

    LOGGER.info("Connect to docker daemon...")
    client = docker.from_env()
    LOGGER.info("...Connected")

    LOGGER.info("Pull image...")
    client.images.pull(image) # pull image
    LOGGER.debug(image)
    LOGGER.info("...Pulled")
    # run container
    LOGGER.info("Start container...")
    container = client.containers.run(
        image=image,
        command=command,
        environment=environment,
        stdin_open=True,
        detach=True,
    )
    LOGGER.info("...Started: %s", container.name)

    LOGGER.info("Send variable...")
    socket = container.attach_socket(
        params={"stdin": 1, "stream": 1, "stdout": 1, "stderr": 1}
    )
    for line in std_in:
        socket._sock.sendall(
            line.encode("utf-8")
        )  # pylint: disable=protected-access
    LOGGER.info("...Send")

    LOGGER.info("Wait for execution...")
    container.wait(timeout=timeout)
    LOGGER.info("...Executed")

    LOGGER.info("Receive stdout...")
    stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
    LOGGER.debug(stdout)
    LOGGER.info("...Received")

    if rm:
        LOGGER.info("Remove container...")
        container.remove()
        LOGGER.info("...Removed")

    LOGGER.info("Parse stdout...")
    out = parse_stdout(stdout)
    
    LOGGER.debug(out)
    LOGGER.info("...Parsed")

    return float_to_json_float(out)


def parse_stdout(stdout: str):
    lines = stdout.split("\n")
    lines.reverse()
    for line in lines:
        if line:
            return json.loads(line)

