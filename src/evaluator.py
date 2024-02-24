"""
Evaluate solution.

"""
import logging
import signal
from time import time
from traceback import format_exc

from model import EvaluationTrial
from utils.docker import calculate_with_docker


LOGGER = logging.getLogger(__name__)


def evaluator(ctx, **kwargs):
    """
    Fetch solution and evaluate it.

    """

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

        started_at = time()
        try:
            # evaluate solution by using docker image
            std_out = calculate_with_docker(model.image,
                                            {v["key"]: v["value"] for v in model.environment},
                                            kwargs["command"], kwargs["timeout"], kwargs["rm"],
                                            model.variable)
            
            objective = std_out["objective"]
            constraint = std_out["constraints"] if "constraints" in std_out else None

            LOGGER.info("Push evaluation...")
            # succeeded in evaluating solution
            finished_at = time()
            model.save_succeeded_evaluation(started_at, finished_at, objective, constraint)
            LOGGER.info("...Pushed")

        except KeyboardInterrupt:
            # KeyboardInterrupt while evaluating solution
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = time()
            model.save_failed_evaluation(started_at, finished_at, format_exc())
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            # Exception while evaluating solution
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
