"""
Calculate score.

"""
from time import time
from traceback import format_exc
import logging
import signal
from src.utils.execute_in_docker import execute_in_docker


from scorer.model import ScoreTrial


LOGGER = logging.getLogger(__name__)


def calculate_score(ctx, **kwargs):
    """
    Fetch evaluations and calculate score.

    """
    model = ScoreTrial()

    n_score = 1
    LOGGER.info("==================== Calculating score: %d ====================", n_score)
    while True:
        try:
            # fetch evaluation
            LOGGER.info("Find evaluation...")
            model.fetch_evaluation(kwargs["interval"])
            LOGGER.info("...Found")

        except KeyboardInterrupt:
            # KeyboardInterrupt while fetching evaluations
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            # Exception while fetching evaluations
            LOGGER.error(format_exc())
            continue

        started_at = time()
        try:
            # calculate score with docker image
            std_out = execute_in_docker(model.image,
                                            {v["key"]: v["value"] for v in model.environment},
                                            kwargs["command"], kwargs["timeout"], kwargs["rm"],
                                            model.current, model.history)
            score = std_out
            LOGGER.info("Push score...")

            # succeeded in evaluating solution
            finished_at = time()
            model.save_succeeded_score(started_at, finished_at, score)
            LOGGER.info("...Pushed")

        except KeyboardInterrupt:
            # KeyboardInterrupt while evaluating solutions
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = time()
            model.save_failed_score(started_at, finished_at, format_exc())
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            # Exception while evaluating solutions
            LOGGER.error(format_exc())
            LOGGER.info("Finish evaluation...")
            finished_at = time()
            model.save_failed_score(started_at, finished_at, format_exc())
            LOGGER.info("...Finished")
            break
            continue

        n_score += 1
        LOGGER.info(
            "==================== Calculating score: %d ====================", n_score
        )
        if n_score == 1:
            break

def make_history(eval, score):
    pass