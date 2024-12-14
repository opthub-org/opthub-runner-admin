"""The main module for the score calculation process."""

import json
import logging
import signal
import sys
from traceback import format_exc

from opthub_runner_admin.args import Args
from opthub_runner_admin.lib.docker_executor import execute_in_docker
from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.lib.sqs import ScoreMessage, ScorerSQS
from opthub_runner_admin.models.evaluation import fetch_success_evaluation_by_primary_key
from opthub_runner_admin.models.exception import ContainerRuntimeError, DockerImageNotFoundError
from opthub_runner_admin.models.match import Match, fetch_match_by_id
from opthub_runner_admin.models.score import (
    FailedScoreCreateParams,
    is_score_exists,
    save_failed_score,
    save_success_score,
)
from opthub_runner_admin.scorer.cache import Cache, CacheWriteError
from opthub_runner_admin.scorer.history import make_history
from opthub_runner_admin.utils.time import get_utcnow
from opthub_runner_admin.utils.truncate import truncate_text_center
from opthub_runner_admin.utils.zfill import zfill

LOGGER = logging.getLogger(__name__)


def setup_sqs(args: Args) -> ScorerSQS:
    """Setup scorer SQS.

    Args:
        args (Args): Args

    Returns:
        ScorerSQS: SQS
    """
    # for communication with Amazon SQS
    sqs = ScorerSQS(
        args["interval"],
        {
            "queue_url": args["scorer_queue_url"],
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
        },
    )
    sqs.check_accessible()  # check if the queue is accessible
    sqs.wake_up_visibility_extender()  # wake up the visibility extender
    return sqs


def setup_dynamodb(args: Args) -> DynamoDB:
    """Setup DynamoDB.

    Args:
        args (Args): Args

    Returns:
        DynamoDB: DynamoDB
    """
    # for communication with DynamoDB
    dynamodb = DynamoDB(
        {
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
            "table_name": args["table_name"],
        },
    )
    dynamodb.check_accessible()  # check if the table is accessible
    return dynamodb


def get_message_from_queue(sqs: ScorerSQS) -> ScoreMessage | None:
    """Get message from the queue.

    Args:
        sqs (ScorerSQS): Scorer SQS

    Returns:
        ScoreMessage | None: Scorer Message
    """
    LOGGER.info("Finding Evaluation to calculate score...")
    try:
        message = sqs.get_message_from_queue()
    except KeyboardInterrupt:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        LOGGER.exception("Error occurred while fetching message from SQS.")
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(1)
    except Exception:
        LOGGER.exception("Error occurred while fetching message from SQS.")
        return None
    else:
        LOGGER.debug("Message: %s", message)
        LOGGER.info("...Found")
        return message


def get_match_from_message(message: ScoreMessage) -> Match | None:
    """Get match from message.

    Args:
        message (ScoreMessage): ScoreMessage

    Returns:
        Match: Match
    """
    match_id = "Match#" + message["match_id"]
    LOGGER.info("Fetching indicator data from DB...")
    try:
        match = fetch_match_by_id(match_id)
    except KeyboardInterrupt:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        LOGGER.exception("Error occurred while fetching indicator data from DB.")
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(1)
    except Exception as error:
        LOGGER.exception("Error occurred while fetching indicator data from DB.")
        if isinstance(error, DockerImageNotFoundError):
            sys.exit(1)
        return None
    else:
        LOGGER.debug("Match %s:\n%s", match_id, match)
        LOGGER.info("...Fetched")
        return match


def calculate_score(args: Args) -> None:  # noqa: PLR0915, C901, PLR0912
    """The function that controls the score calculation process.

    Args:
        args (Args): The arguments.
    """
    sqs = setup_sqs(args)
    dynamodb = setup_dynamodb(args)

    # cache for the trials history
    cache = Cache()

    n_score = 0

    while True:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        message = get_message_from_queue(sqs)
        if message is None:
            continue

        match = get_match_from_message(message)
        if match is None:
            continue

        if is_score_exists(dynamodb, message["match_id"], message["participant_id"], message["trial_no"]):
            LOGGER.warning("The score already exists.")
            sqs.delete_message_from_queue()
            continue

        try:
            started_at = None
            finished_at = None
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
                "feasible": evaluation["feasible"],
            }
            LOGGER.debug("Current: %s", current)

            cache.load(match["id"] + "#" + evaluation["participant_id"])  # load cache to make history

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
            started_at = get_utcnow()
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
                msg = "Error occurred while calculating score.\n" + score_result["error"]
                raise ContainerRuntimeError(msg)

            LOGGER.info("...Calculated")
            finished_at = get_utcnow()
            info_msg = "Finished at : " + finished_at
            LOGGER.info(info_msg)

            LOGGER.info("Saving Score...")

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
                    "created_at": get_utcnow(),
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
                    "created_at": get_utcnow(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "score": score_result["score"],
                },
            )
            LOGGER.info("...Saved")

            sqs.delete_message_from_queue()

            try:
                cache.append(
                    {
                        "trial_no": evaluation["trial_no"],
                        "objective": evaluation["objective"],
                        "constraint": evaluation["constraint"],
                        "info": evaluation["info"],
                        "feasible": evaluation["feasible"],
                        "score": score_result["score"],
                    },
                )  # append trial scored in this iteration to the cache
            except CacheWriteError:
                msg = "Failed to write to cache."
                LOGGER.warning(msg)

        except (Exception, KeyboardInterrupt) as error:
            if isinstance(error, KeyboardInterrupt):
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
                signal.signal(signal.SIGINT, signal.SIG_IGN)
            try:
                started_at = started_at if started_at is not None else get_utcnow()
                finished_at = finished_at if finished_at is not None else get_utcnow()
                error_msg = format_exc() if isinstance(error, ContainerRuntimeError) else "Internal Server Error"
                admin_error_msg = format_exc()
                failed_score: FailedScoreCreateParams = {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": get_utcnow(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": truncate_text_center(error_msg, 16384),
                    "admin_error_message": truncate_text_center(admin_error_msg, 16384),
                }
                LOGGER.exception("Error occurred while calculating score.")
                LOGGER.info("Saving Failed Score...")
                LOGGER.debug("Failed Score: %s", failed_score)
                save_failed_score(dynamodb, failed_score)
                LOGGER.info("...Saved")
                sqs.delete_message_from_queue()
            except Exception:
                LOGGER.exception("Error occurred while handling failed score.")
                LOGGER.exception(format_exc())
            if isinstance(error, KeyboardInterrupt):
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                sys.exit(1)
            continue
