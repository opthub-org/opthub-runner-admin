"""
Evaluate solutions.

"""
import logging
import signal
import docker
import json
import sys
import math
from time import time
from traceback import format_exc

from model import EvaluationTrial


LOGGER = logging.getLogger(__name__)

def evaluator(ctx, **kwargs):

    LOGGER.info("Connect to docker daemon...")
    client = docker.from_env()
    LOGGER.info("...Connected")

    model = EvaluationTrial()

    n_evaluation = 1
    LOGGER.info("==================== Evaluation: %d ====================", n_evaluation)
    while True:
        # start to fetch solutions
        try:
            LOGGER.info("Find solution to evaluate...")
            model.fetch_solution(kwargs["interval"])
            LOGGER.info("...Found")

        except KeyboardInterrupt:
            # KeyboardInterrupt while fetching solutions
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            # Exception while fetching solutions
            LOGGER.error(format_exc())
            continue

        # start to evaluate solution
        started_at = time()
        try:
            # run container to evaluate solution
            LOGGER.info("Start container...")
            client.images.pull(model.image) # imageをpull
            LOGGER.debug(model.image)
            container = client.containers.run(
                image=model.image,
                command=kwargs["command"],
                environment={
                    v["key"]: v["value"] for v in model.environment
                },
                stdin_open=True,
                detach=True,
            )
            LOGGER.info("...Started: %s", container.name)

            LOGGER.info("Send variable...")
            socket = container.attach_socket(
                params={"stdin": 1, "stream": 1, "stdout": 1, "stderr": 1}
            )
            socket._sock.sendall(
                model.variable.encode("utf-8")
            )  # pylint: disable=protected-access
            LOGGER.info("...Send")

            LOGGER.info("Wait for Evaluation...")
            container.wait(timeout=kwargs["timeout"])
            LOGGER.info("...Evaluated")

            LOGGER.info("Receive stdout...")
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
            LOGGER.debug(stdout)
            LOGGER.info("...Received")

            if kwargs["rm"]:
                LOGGER.info("Remove container...")
                container.remove()
                LOGGER.info("...Removed")

            LOGGER.info("Parse stdout...")
            out = parse_stdout(stdout)
            LOGGER.debug(out)
            LOGGER.info("...Parsed")

            LOGGER.info("Push evaluation...")

            # succeeded in evaluating solution
            finished_at = time()
            model.save_succeeded_evaluation(started_at, finished_at, to_json_float(out.get("objective")), to_json_float(out.get("constraint")))
            LOGGER.info("...Pushed")

        except KeyboardInterrupt:
            # KeyboardInterrupt while evaluating solutions
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = time()
            model.save_failed_evaluation(started_at, finished_at, format_exc())
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            # Exception while evaluating solutions
            LOGGER.error(format_exc())
            LOGGER.info("Finish evaluation...")
            finished_at = time()
            model.save_failed_evaluation(started_at, finished_at, format_exc())
            LOGGER.info("...Finished")
            continue

        n_evaluation += 1
        LOGGER.info(
            "==================== Evaluation: %d ====================", n_evaluation
        )
        if n_evaluation == 5:
            break

def parse_stdout(stdout: str):
    lines = stdout.split("\n")
    lines.reverse()
    for line in lines:
        if line:
            return json.loads(line)

def to_json_float(value):
    """Convert a float value to a JSON float value.

    :param value: float value
    :return float: JSON float value
    """
    if isinstance(value, list):
        return [to_json_float(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json_float(v) for k, v in value.items()}
    if not isinstance(value, float):
        return value
    if value == math.inf:
        LOGGER.warning("math.inf is converted to sys.float_info.max")
        return sys.float_info.max
    if value == -math.inf:
        LOGGER.warning("-math.inf is converted to -sys.float_info.max")
        return -sys.float_info.max
    if math.isnan(value):
        LOGGER.warning("math.nan is converted to None")
        return None
    return value