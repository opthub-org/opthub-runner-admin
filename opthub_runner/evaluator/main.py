"""This module is the main module for the evaluator process."""

import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner.args import Args
from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.lib.sqs import EvaluatorSQS
from opthub_runner.models.evaluation import save_failed_evaluation, save_success_evaluation
from opthub_runner.models.match import fetch_match_by_alias
from opthub_runner.models.solution import fetch_solution_by_primary_key

LOGGER = logging.getLogger(__name__)


def evaluate(ctx: click.Context, args: Args) -> None:
    """The function that controls the evaluation process."""
    # communication with Amazon SQS
    sqs = EvaluatorSQS(
        args["interval"],
        {
            "queue_name": args["evaluator_queue_name"],
            "queue_url": args["evaluator_queue_url"],
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
        },
    )

    # communication with DynamoDB
    dynamodb = DynamoDB(
        {
            "region_name": args["region_name"],
            "aws_access_key_id": args["access_key_id"],
            "aws_secret_access_key": args["secret_access_key"],
            "table_name": args["table_name"],
        },
    )

    n_evaluation = 0

    while True:
        n_evaluation += 1
        LOGGER.info("==================== Evaluation: %d ====================", n_evaluation)

        try:
            LOGGER.info("Find Solution to evaluate...")
            message = sqs.get_message_from_queue()
            LOGGER.info("...Found")

            LOGGER.info("Fetch problem data from DB...")
            match = fetch_match_by_alias(args["match_alias"])
            LOGGER.info("...Fetched")

            LOGGER.info("Fetch Solution from DB...")
            solution = fetch_solution_by_primary_key(
                dynamodb,
                match["id"],
                message["participant_id"],
                message["trial"],
            )
            LOGGER.info("...Fetched")

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
            LOGGER.info("Start to evaluate...")
            started_at = datetime.now().isoformat()
            info_msg = "Started at : " + started_at
            LOGGER.info(info_msg)

            evaluation_result = execute_in_docker(
                {
                    "image": match["problem_docker_image"],
                    "environments": match["problem_environments"],
                    "command": args["command"],
                    "timeout": args["timeout"],
                    "rm": args["rm"],
                },
                [json.dumps(solution["variable"]) + "\n"],
            )

            if "error" in evaluation_result:
                msg = "Error occurred while evaluating solution:\n" + evaluation_result["error"]
                raise RuntimeError(msg)
            if "feasible" not in evaluation_result:
                evaluation_result["feasible"] = None
            if "constraint" not in evaluation_result:
                evaluation_result["constraint"] = None
            if "info" not in evaluation_result:
                evaluation_result["info"] = {}

            LOGGER.info("...Evaluated")
            finished_at = datetime.now().isoformat()
            info_msg = "Finished at : " + finished_at
            LOGGER.info(info_msg)

            LOGGER.info("Save Evaluation...")
            save_success_evaluation(
                dynamodb,
                {
                    "match_id": match["id"],
                    "participant_id": message["participant_id"],
                    "trial_no": message["trial_no"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "objective": evaluation_result["objective"],
                    "constraint": evaluation_result["constraint"],
                    "info": evaluation_result["info"],
                    "feasible": evaluation_result["feasible"],
                },
            )
            LOGGER.info("...Saved")

            sqs.delete_message_from_queue()

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.exception("Keyboard Interrupt")
            finished_at = datetime.now().isoformat()
            save_failed_evaluation(
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
            sqs.delete_message_from_queue()
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            ctx.exit(0)
        except Exception:
            finished_at = datetime.now().isoformat()
            save_failed_evaluation(
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
            sqs.delete_message_from_queue()
            LOGGER.exception(format_exc())

            continue
