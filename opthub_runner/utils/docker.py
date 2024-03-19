import json
import logging

import docker

from opthub_runner.utils.converter import float_to_json_float

LOGGER = logging.getLogger(__name__)


def execute_in_docker(image, environment, command, timeout, rm, *std_in):
    """
    Solutionの評価とEvaluationのScore計算をDocker Imageを使って行う関数．

    Parameters
    ----------
    image : str
        Docker Imageの名前．
    environment : dict
        環境変数のdict．ProblemEnvironmentやIndicatorEnvironmentを表す．
    command : str
        Dockerで実行するコマンド．
    timeout : int
        Dockerの実行の制限時間．
    rm : bool
        Dockerコンテナを削除するかどうか．Trueなら削除．
    std_in : list[str]
        Dockerへの標準入力のリスト．各列に改行文字をつけることに注意．

    """

    LOGGER.info("Connect to docker daemon...")
    client = docker.from_env()
    LOGGER.info("...Connected")

    LOGGER.info("Pull image...")
    client.images.pull(image)  # pull image
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
    socket = container.attach_socket(params={"stdin": 1, "stream": 1, "stdout": 1, "stderr": 1})

    for line in std_in:
        socket._sock.sendall(line.encode("utf-8"))  # pylint: disable=protected-access
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


def main():
    std_out = execute_in_docker(
        "opthub/sphere:latest", {"SPHERE_OPTIMA": "[[1, 2, 3], [4, 5, 6]]"}, [], 100, True, "[1, 1, 1]\n"
    )

    print(std_out)

    std_out = execute_in_docker(
        "opthub/hypervolume:latest",
        {"HV_REF_POINT": "[1, 1]"},
        [],
        100,
        True,
        '{"objective": [0.11999999999999994, 0.2700000000000001], "constraint": null}\n[]\n',
    )
    print(std_out)


if __name__ == "__main__":
    main()
