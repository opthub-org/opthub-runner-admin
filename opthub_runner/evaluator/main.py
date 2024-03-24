import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

from opthub_runner.models.evaluation import save_failed_evaluation, save_success_evaluation
from opthub_runner.models.match import fetch_match_problem_by_id
from opthub_runner.models.solution import fetch_solution_by_primary_key
from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.lib.keys import ACCESS_KEY_ID, QUEUE_NAME, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.runner_sqs import EvaluatorSQS

def main():
    # Amazon SQSとのやり取り用
    sqs = RunnerSQS("tmp_name")
    # sqs = RunnerSQS(kwargs["queue_name"])

    # Dynamo DBとのやり取り用
    dynamodb = DynamoDB("http://localhost:8000", "localhost", "aaa", "aaa", "opthub-dynamodb-participant-trials-dev")
    # dynamodb = DynamoDB(kwargs["endpoint_url"],
    #                     kwargs["region_name"],
    #                     kwargs["aws_access_key_id"],
    #                      kwargs["aws_secret_access_key_id"],
    #                     kwargs["table_name"])
    sqs = EvaluatorSQS(QUEUE_NAME, 2.0)
    # sqs = RunnerSQS(kwargs["queue_  REGION_NAME, ACCESS_KEY_ID, SECRET_ACCESS_KEY, TABLE_NAME)
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
            partition_key_data = sqs.get_partition_key_from_queue()
            continue

        try:
            LOGGER.info("Start to evaluate...")
            # 評価開始時刻の記録
            started_at = datetime.now()
            started_at = started_at.isoformat()
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってObjective，Constraint，In
                foを取得   dynamodb

                kwargs["command"],
                kwargs["timeout"],
                kwargs["rm"],
                json.dumps(solution["Variable"]) + "\n",
            )

            if "error" in evaluation_result:
                raise Exception("Error occurred while evaluating solution:\n" + evaluation_result["error"])
            if "feasible" not in evaluation_result:
                evaluation_result["feasible"] = None
            if "constraint" not in evaluation_result:
                evaluation_result["constraint"] = None
            if "info" not in evaluation_result:
                evaluation_result["info"] = {}

            LOGGER.info("...Evaluated")
            # 評価終了時刻の記録
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            LOGGER.info(f"Finished at : {finished_at}")

            LOGGER.info("Save Evaluation...")
            # 成功試行をDynamo DBに保存
            save_success_evaluation(

],
antID"],
],
t"],
,

                finished_at,
                evaluation_result["objective"],
                evaluation_result["constraint"],
                evaluation_result["info"],
                evaluation_result["feasible"],
                dynamodb,
            )
            LOGGER.info("...Saved")

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_evaluation(
                solution["MatchID"],
                solution["ParticipantID"],
                solution["TrialNo"],

tion["CreatedAt"],
           start
finished_at,
    format_exc()
         dynamod

gnal.signal(signTERM, signal.SIG_DFL)
   signal.signalINT, signal.SIG_DFL)
            ctx.
        except Edynamodb,
xception:
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_evaluation(
    solution["MatchID"],
                solution["ParticipantID"],
            sqs.delete_partition_key_from_queue()

                dynamodb,
            )
            LOGGER.error(format_exc())
            continue

dynamodb,

                dynamodb,
