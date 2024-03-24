import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.keys import ACCESS_KEY_ID, QUEUE_NAME, QUEUE_URL, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.sqs import EvaluatorSQS
from opthub_runner.main import Args
from opthub_runner.models.evaluation import save_failed_evaluation, save_success_evaluation
from opthub_runner.models.match import fetch_match_by_alias
from opthub_runner.models.solution import fetch_solution_by_primary_key

LOGGER = logging.getLogger(__name__)


def evaluate(ctx: click.Context, args: Args) -> None:
    """
    評価プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = EvaluatorSQS(
        args["interval"],
        {
            "queue_name": QUEUE_NAME,
            "queue_url": QUEUE_URL,
            "region_name": REGION_NAME,
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
        },
    )

    # Dynamo DBとのやり取り用
    dynamodb = DynamoDB(
        {
            "region_name": REGION_NAME,
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "table_name": TABLE_NAME,
        },
    )

    n_evaluation = 0

    while True:
        n_evaluation += 1
        LOGGER.info("==================== Evaluation: %d ====================", n_evaluation)

        try:
            # Partition KeyのためのParticipantID，Trialを取得
            LOGGER.info("Find Solution to evaluate...")
            message = sqs.get_message_from_queue()
            LOGGER.info("...Found")

            # 競技をエイリアスから取得
            LOGGER.info("Fetch problem data from DB...")
            match = fetch_match_by_alias(args["match_alias"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからSolutionを取得
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
            LOGGER.error("Keyboard Interrupt")
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)

        except Exception:
            LOGGER.error("Exception")
            LOGGER.error(format_exc())
            continue

        try:
            LOGGER.info("Start to evaluate...")
            # 評価開始時刻の記録
            started_at = datetime.now().isoformat()
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってObjective，Constraint，Infoを取得
            evaluation_result = execute_in_docker(
                {
                    "image": match["problem_docker_image"],
                    "environments": match["problem_environments"],
                    "command": args["command"],
                    "timeout": args["timeout"],
                    "rm": args["rm"],
                },
                json.dumps(solution["variable"]) + "\n",
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
            # 評価終了時刻の記録
            finished_at = datetime.now().isoformat()
            LOGGER.info(f"Finished at : {finished_at}")

            LOGGER.info("Save Evaluation...")
            # 成功試行をDynamo DBに保存
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
            LOGGER.error("Keyboard Interrupt")
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
            LOGGER.error(format_exc())

            continue
