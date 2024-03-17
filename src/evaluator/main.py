from datetime import datetime
import signal
import logging
from traceback import format_exc
import json

from utils.runnersqs import RunnerSQS
from utils.dynamodb import DynamoDB
from utils.docker_executor import execute_in_docker
from model.match import fetch_match_problem_by_id
from model.solution import fetch_solution_by_primary_key
from model.evaluation import save_success_evaluation, save_failed_evaluation


LOGGER = logging.getLogger(__name__)


def evaluate(ctx, **kwargs):
    """
    評価プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = RunnerSQS("tmp_name")
    #sqs = RunnerSQS(kwargs["queue_name"])

    # Dynamo DBとのやり取り用
    dynamodb = DynamoDB("http://localhost:8000",
                        "localhost",
                        "aaa",
                        "aaa",
                        "opthub-dynamodb-participant-trials-dev")
    # dynamodb = DynamoDB(kwargs["endpoint_url"],
    #                     kwargs["region_name"],
    #                     kwargs["aws_access_key_id"],
    #                     kwargs["aws_secret_access_key_id"],
    #                     kwargs["table_name"])
    
    n_evaluation = 0

    while True:
        n_evaluation += 1
        LOGGER.info("==================== Evaluation: %d ====================", n_evaluation)

        try:
            # Partition KeyのためのParticipantID，Trialを取得
            LOGGER.info("Find Solution to evaluate...")
            partition_key_data = sqs.get_partition_key_from_queue(kwargs["interval"])
            LOGGER.info("...Found")

            # MatchIDからProblemEnvironmentsとProblemDockerImageを取得
            LOGGER.info("Fetch problem data from DB...")
            problem_data = fetch_match_problem_by_id(kwargs["match_id"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからSolutionを取得
            LOGGER.info("Fetch Solution from DB...")
            solution = fetch_solution_by_primary_key(kwargs["match_id"],
                                                    partition_key_data["ParticipantID"],
                                                    partition_key_data["Trial"],
                                                    dynamodb)
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
            started_at = datetime.now()
            started_at = started_at.isoformat()
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってObjective，Constraint，Infoを取得
            evaluation_result = execute_in_docker(problem_data["ProblemDockerImage"],
                                                  problem_data["ProblemEnvironments"],
                                                  kwargs["command"],
                                                  kwargs["timeout"],
                                                  kwargs["rm"],
                                                  json.dumps(solution["Variable"]) + "\n")

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
            save_success_evaluation(solution["MatchID"],
                                    solution["ParticipantID"],
                                    solution["TrialNo"],
                                    solution["CreatedAt"],
                                    started_at,
                                    finished_at,
                                    evaluation_result["objective"],
                                    evaluation_result["constraint"],
                                    evaluation_result["info"],
                                    evaluation_result["feasible"],
                                    dynamodb)
            LOGGER.info("...Saved")
            
        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_evaluation(solution["MatchID"],
                                   solution["ParticipantID"],
                                   solution["TrialNo"],
                                   solution["CreatedAt"],
                                   started_at,
                                   finished_at,
                                   format_exc(),
                                   dynamodb)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)
        except Exception:
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_evaluation(solution["MatchID"],
                                   solution["ParticipantID"],
                                   solution["TrialNo"],
                                   solution["CreatedAt"],
                                   started_at,
                                   finished_at,
                                   format_exc(),
                                   dynamodb)
            LOGGER.error(format_exc())
            continue