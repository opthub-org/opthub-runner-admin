import json
import logging
import signal
from datetime import datetime
from traceback import format_exc

import click

from opthub_runner.lib.docker_executor import execute_in_docker
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.lib.keys import ACCESS_KEY_ID, QUEUE_NAME, QUEUE_URL, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.sqs import ScorerSQS
from opthub_runner.lib.zfill import zfill
from opthub_runner.main import Args
from opthub_runner.models.evaluation import fetch_success_evaluation_by_primary_key
from opthub_runner.models.match import fetch_match_by_alias
from opthub_runner.models.score import save_failed_score, save_success_score
from opthub_runner.scorer.cache import Cache
from opthub_runner.scorer.history import make_history, write_to_cache

LOGGER = logging.getLogger(__name__)


def calculate_score(ctx: click.Context, args: Args) -> None:
    """
    スコア計算プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = ScorerSQS(
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

    # cacheファイルの管理用
    cache = Cache()

    n_score = 0

    while True:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        try:
            # Partition KeyのためのMatchID，ParticipantID，TrialNoを取得
            LOGGER.info("Find Evaluation to calculate score...")
            message = sqs.get_message_from_queue()
            LOGGER.info("...Found")

            # 競技をエイリアスから取得
            LOGGER.info("Fetch indicator data from DB...")
            match = fetch_match_by_alias(args["match_alias"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからEvaluationを取得
            LOGGER.info("Fetch Evaluation from DB...")
            evaluation = fetch_success_evaluation_by_primary_key(
                dynamodb,
                match["id"],
                message["participant_id"],
                message["trial"],
            )
            LOGGER.info("...Fetched")

            # currentとhistoryを作成（Dockerの入力）
            LOGGER.info("Make history...")
            current = {
                "objective": evaluation["objective"],
                "constraint": evaluation["constraint"],
                "info": evaluation["info"],
            }
            history = make_history(
                match["id"],
                evaluation["participant_id"],
                zfill(int(evaluation["trial_no"]) - 1, len(evaluation["trial_no"])),
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
            started_at = datetime.now().isoformat()
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってScoreを取得
            score_result = execute_in_docker(
                {
                    "image": match["indicator_docker_image"],
                    "environments": match["indicator_environments"],
                    "command": args["command"],
                    "timeout": args["timeout"],
                    "rm": args["rm"],
                },
                json.dumps(current) + "\n",
                json.dumps(history) + "\n",
            )

            if "error" in score_result:
                msg = "Error occurred while calculating score:\n" + score_result["error"]
                raise RuntimeError(msg)

            LOGGER.info("...Calculated")
            # スコア計算終了時刻の記録
            finished_at = datetime.now().isoformat()
            LOGGER.info(f"Finished at : {finished_at}")

            LOGGER.info("Save Score...")
            # cacheにスコアを保存
            write_to_cache(
                cache,
                match["id"],
                evaluation["participant_id"],
                {
                    "TrialNo": evaluation["trial_no"],
                    "Objective": evaluation["objective"],
                    "Constraint": evaluation["constraint"],
                    "Info": evaluation["info"],
                    "Feasible": evaluation["feasible"],
                    "Score": score_result["score"],
                },
            )

            # 成功試行をDynamo DBに保存
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
            LOGGER.info("...Saved")

            sqs.delete_message_from_queue()

        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now().isoformat()
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
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            ctx.exit(0)
        except Exception:
            finished_at = datetime.now().isoformat()
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
            LOGGER.error(format_exc())

            sqs.delete_message_from_queue()

            continue
