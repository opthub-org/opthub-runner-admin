"""The main module for the score calculation process."""

import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner_admin.args import Args
from opthub_runner_admin.lib.docker_executor import execute_in_docker
from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.lib.sqs import ScorerSQS
from opthub_runner_admin.models.evaluation import fetch_success_evaluation_by_primary_key
from opthub_runner_admin.models.match import fetch_match_by_id
from opthub_runner_admin.models.score import save_failed_score, save_success_score
from opthub_runner_admin.scorer.cache import Cache
from opthub_runner_admin.scorer.history import make_history, write_to_cache
from opthub_runner_admin.utils.zfill import zfill

LOGGER = logging.getLogger(__name__)


def calculate_score(ctx: click.Context, args: Args) -> None:
    """The function that controls the score calculation process.

    Args:
        ctx (click.Context): The Click context.
        args (Args): The arguments.
    """
    # for communication with Amazon SQS
    sqs = ScorerSQS(
        args["interval"],
        {
            "queue_name": args["scorer_queue_name"],
            "queue_url": args["scorer_queue_url"],
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
        },
    )

    # for communication with DynamoDB
    dynamodb = DynamoDB(
        {
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
            "table_name": args["table_name"],
        },
    )

    # cache for the history
    cache = Cache()

    n_score = 0

    while True:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        try:
            LOGGER.info("Finding Evaluation to calculate score...")
            message = sqs.get_message_from_queue()
            LOGGER.debug("Message: %s", message)
            LOGGER.info("...Found")

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.exception("Keyboard Interrupt")
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            LOGGER.exception("Exception")
            LOGGER.exception(format_exc())
            continue

        try:
            match_id = "Match#" + message["match_id"]

            LOGGER.info("Fetching indicator data from DB...")
            match = fetch_match_by_id(match_id)
            LOGGER.debug("Match %s:\n%s", match_id, match)
            LOGGER.info("...Fetched")

            LOGGER.info("Fetching Evaluation from DB...")

            evaluation = fetch_success_evaluation_by_primary_key(
                dynamodb,
                match["id"],
                message["participant_id"],
                message["trial_no"],
            )
            LOGGER.debug("Evaluation: %s", evaluation)
            LOGGER.info("...Fetched")

            LOGGER.info("Making history...")
            current = {
                "objective": evaluation["objective"],
                "constraint": evaluation["constraint"],
                "info": evaluation["info"],
            }
            LOGGER.debug("Current: %s", current)
            history = make_history(
                match["id"],
                evaluation["participant_id"],
                zfill(int(evaluation["trial_no"]) - 1, len(evaluation["trial_no"])),
                cache,
                dynamodb,
            )
            LOGGER.debug("History: %s", history)
            LOGGER.info("...Made")

            LOGGER.info("Calculating score...")
            started_at = datetime.now().isoformat()
            info_msg = "Started at : " + started_at
            LOGGER.info(info_msg)

            score_result = execute_in_docker(
                {
                    "image": match["indicator_docker_image"],
                    "environments": match["indicator_environments"],
                    "command": args["command"],
                    "timeout": args["timeout"],
                    "rm": args["rm"],
                },
                [json.dumps(current) + "\n", json.dumps(history) + "\n"],
            )

            LOGGER.debug("Score Result: %s", score_result)

            if "error" in score_result:
                msg = "Error occurred while calculating score:\n" + score_result["error"]
                raise RuntimeError(msg)

            LOGGER.info("...Calculated")
            finished_at = datetime.now().isoformat()
            info_msg = "Finished at : " + finished_at
            LOGGER.info(info_msg)

            LOGGER.info("Saving Score...")
            write_to_cache(
                cache,
                match["id"],
                evaluation["participant_id"],
                {
                    "trial_no": evaluation["trial_no"],
                    "objective": evaluation["objective"],
                    "constraint": evaluation["constraint"],
                    "info": evaluation["info"],
                    "feasible": evaluation["feasible"],
                    "score": score_result["score"],
                },
            )
            LOGGER.debug(
                "Trial written to cache: match_id: %s, participant_id: %s\n%s",
                match["id"],
                evaluation["participant_id"],
                {
                    "trial_no": evaluation["trial_no"],
                    "objective": evaluation["objective"],
                    "constraint": evaluation["constraint"],
                    "info": evaluation["info"],
                    "feasible": evaluation["feasible"],
                    "score": score_result["score"],
                },
            )

            save_success_score(
                dynamodb,
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "score": score_result["score"],
                },
            )

            LOGGER.debug(
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "score": score_result["score"],
                },
            )
            LOGGER.info("...Saved")

            sqs.delete_message_from_queue()

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.exception("Keyboard Interrupt")
            finished_at = datetime.now().isoformat()
            LOGGER.info("Saving Failed Score...")
            save_failed_score(
                dynamodb,
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )
            LOGGER.debug(
                "Failed Score: %s",
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )

            LOGGER.info("...Saved")
            sqs.delete_message_from_queue()
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)
        except Exception:
            finished_at = datetime.now().isoformat()
            LOGGER.exception(format_exc())
            LOGGER.info("Saving Failed Score...")
            LOGGER.debug(
                "Failed Score: %s",
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )
            save_failed_score(
                dynamodb,
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )
            LOGGER.info("...Saved")
            sqs.delete_message_from_queue()

            continue
