import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner.lib.cache import Cache
from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.lib.runner_sqs import RunnerSQS
from opthub_runner.lib.scorer_history import make_history, write_to_cache
from opthub_runner.lib.zfill import zfill
from opthub_runner.main import Args
from opthub_runner.model.evaluation import fetch_evaluation_by_primary_key
from opthub_runner.model.match import fetch_match_indicator_by_id
from opthub_runner.model.score import save_failed_score, save_success_score

LOGGER = logging.getLogger(__name__)


def calculate_score(ctx: click.Context, args: Args) -> None:
    """
    スコア計算プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = RunnerSQS("tmp_name")
    # sqs = RunnerSQS(args["queue_name"])

    # Dynamo DBとのやり取り用
    dynamodb = DynamoDB("http://localhost:8000", "localhost", "aaa", "aaa", "opthub-dynamodb-participant-trials-dev")
    # dynamodb = DynamoDB(args["endpoint_url"],
    #                     args["region_name"],
    #                     args["aws_access_key_id"],
    #                     args["aws_secret_access_key_id"],
    #                     args["table_name"])

    # cacheファイルの管理用
    cache = Cache()

    n_score = 0

    while True:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        try:
            # Partition KeyのためのMatchID，ParticipantID，TrialNoを取得
            LOGGER.info("Find Evaluation to calculate score...")
            partition_key_data = sqs.get_partition_key_from_queue(args["interval"])
            LOGGER.info("...Found")

            # MatchIDからIndicatorEnvironmentsとIndicatorDockerImageを取得
            LOGGER.info("Fetch indicator data from DB...")
            indicator_data = fetch_match_indicator_by_id(args["match_id"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからEvaluationを取得
            LOGGER.info("Fetch Evaluation from DB...")
            evaluation = fetch_evaluation_by_primary_key(
                args["match_id"], partition_key_data["ParticipantID"], partition_key_data["Trial"], dynamodb
            )
            LOGGER.info("...Fetched")

            # currentとhistoryを作成（Dockerの入力）
            LOGGER.info("Make history...")
            current = {
                "objective": evaluation["Objective"],
                "constraint": evaluation["Constraint"],
                "info": evaluation["Info"],
            }
            history = make_history(
                evaluation["MatchID"],
                evaluation["ParticipantID"],
                zfill(int(evaluation["TrialNo"]) - 1, len(evaluation["TrialNo"])),
                cache,
                dynamodb,
            )
            LOGGER.info("...Made")

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
            LOGGER.info("Start to calculate score...")
            # スコア計算開始時刻の記録
            started_at = datetime.now()
            started_at = started_at.isoformat()
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってScoreを取得
            score_result = execute_in_docker(
                indicator_data["IndicatorDockerImage"],
                indicator_data["IndicatorEnvironments"],
                args["command"],
                args["timeout"],
                args["rm"],
                json.dumps(current) + "\n",
                json.dumps(history) + "\n",
            )

            if "error" in score_result:
                raise Exception("Error occurred while calculating score:\n" + score_result["error"])

            LOGGER.info("...Calculated")
            # スコア計算終了時刻の記録
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            LOGGER.info(f"Finished at : {finished_at}")

            LOGGER.info("Save Score...")
            # cacheにスコアを保存
            write_to_cache(
                evaluation["MatchID"],
                evaluation["ParticipantID"],
                evaluation["TrialNo"],
                current["objective"],
                current["constraint"],
                current["info"],
                score_result["score"],
                cache,
            )

            # 成功試行をDynamo DBに保存
            save_success_score(
                evaluation["MatchID"],
                evaluation["ParticipantID"],
                evaluation["TrialNo"],
                evaluation["CreatedAt"],
                started_at,
                finished_at,
                score_result["score"],
                dynamodb,
            )
            LOGGER.info("...Saved")

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_score(
                evaluation["MatchID"],
                evaluation["ParticipantID"],
                evaluation["TrialNo"],
                evaluation["CreatedAt"],
                started_at,
                finished_at,
                format_exc(),
                dynamodb,
            )
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)
        except Exception:
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_score(
                evaluation["MatchID"],
                evaluation["ParticipantID"],
                evaluation["TrialNo"],
                evaluation["CreatedAt"],
                started_at,
                finished_at,
                format_exc(),
                dynamodb,
            )
            LOGGER.error(format_exc())
            continue
