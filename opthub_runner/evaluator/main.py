import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.lib.keys import ACCESS_KEY_ID, QUEUE_NAME, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.runner_sqs import EvaluatorSQS
from opthub_runner.main import Args
from opthub_runner.models.evaluation import save_failed_evaluation, save_success_evaluation
from opthub_runner.models.match import fetch_match_problem_by_id
from opthub_runner.models.solution import fetch_solution_by_primary_key

LOGGER = logging.getLogger(__name__)


def evaluate(ctx: click.Context, args: Args) -> None:
    """
    評価プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = EvaluatorSQS(QUEUE_NAME, 2.0)

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
            partition_key_data = sqs.get_partition_key_from_queue()
            LOGGER.info("...Found")

            # MatchIDからProblemEnvironmentsとProblemDockerImageを取得
            LOGGER.info("Fetch problem data from DB...")
            problem_data = fetch_match_problem_by_id(args["match_id"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからSolutionを取得
            LOGGER.info("Fetch Solution from DB...")
            solution = fetch_solution_by_primary_key(
                args["match_id"], partition_key_data["ParticipantID"], partition_key_data["Trial"], dynamodb
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
                    "image": problem_data["docker_image"],
                    "environments": problem_data["environments"],
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
                    "match_id": args["match_id"],
                    "participant_id": partition_key_data["ParticipantID"],
                    "trial_no": partition_key_data["Trial"],
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

            sqs.delete_partition_key_from_queue()

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now().isoformat()
            save_failed_evaluation(
                dynamodb,
                {
                    "match_id": args["match_id"],
                    "participant_id": partition_key_data["ParticipantID"],
                    "trial_no": partition_key_data["Trial"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )
            sqs.delete_partition_key_from_queue()
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            ctx.exit(0)
        except Exception:
            finished_at = datetime.now().isoformat()
            save_failed_evaluation(
                dynamodb,
                {
                    "match_id": args["match_id"],
                    "participant_id": partition_key_data["ParticipantID"],
                    "trial_no": partition_key_data["Trial"],
                    "created_at": datetime.now().isoformat(),
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "error_message": format_exc(),
                },
            )
            sqs.delete_partition_key_from_queue()
            LOGGER.error(format_exc())

            continue
