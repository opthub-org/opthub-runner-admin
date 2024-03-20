from datetime import datetime
import signal
import logging
from traceback import format_exc
import json

from utils.runnersqs import RunnerSQS
from utils.dynamodb import DynamoDB
from utils.docker_executor import execute_in_docker
from model.match import fetch_match_indicator_by_id
from model.evaluation import fetch_evaluation_by_primary_key
from model.score import save_success_score, save_failed_score
from utils.scorer_history import make_history, write_to_cache
from utils.cache import Cache
from utils.zfill import zfill

LOGGER = logging.getLogger(__name__)


def calculate_score(ctx, **kwargs):
    """
    スコア計算プロセスのコントローラーを行う関数．

    """

    # Amazon SQSとのやり取り用
    sqs = RunnerSQS(kwargs["queue_name"], kwargs["interval"])

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

    # cacheファイルの管理用
    cache = Cache()
    
    n_score = 0

    while True:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        try:
            # Partition KeyのためのMatchID，ParticipantID，TrialNoを取得
            LOGGER.info("Find Evaluation to calculate score...")
            partition_key_data = sqs.get_partition_key_from_queue()
            LOGGER.info("...Found")

            # MatchIDからIndicatorEnvironmentsとIndicatorDockerImageを取得
            LOGGER.info("Fetch indicator data from DB...")
            indicator_data = fetch_match_indicator_by_id(kwargs["match_id"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからEvaluationを取得
            LOGGER.info("Fetch Evaluation from DB...")
            evaluation = fetch_evaluation_by_primary_key(kwargs["match_id"],
                                                         partition_key_data["ParticipantID"],
                                                         partition_key_data["Trial"],
                                                         dynamodb)
            LOGGER.info("...Fetched")

            # currentとhistoryを作成（Dockerの入力）
            LOGGER.info("Make history...")
            current = {"objective": evaluation["Objective"],
                       "constraint": evaluation["Constraint"],
                       "info": evaluation["Info"]}
            history = make_history(evaluation["MatchID"],
                                   evaluation["ParticipantID"],
                                   zfill(int(evaluation["TrialNo"]) - 1, len(evaluation["TrialNo"])),
                                   cache,
                                   dynamodb)
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
            score_result = execute_in_docker(indicator_data["IndicatorDockerImage"],
                                             indicator_data["IndicatorEnvironments"],
                                             kwargs["command"],
                                             kwargs["timeout"],
                                             kwargs["rm"],
                                             json.dumps(current) + "\n",
                                             json.dumps(history) + "\n")
            
            if "error" in score_result:
                raise Exception("Error occurred while calculating score:\n" + score_result["error"])
            
            LOGGER.info("...Calculated")
            # スコア計算終了時刻の記録
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            LOGGER.info(f"Finished at : {finished_at}")


            LOGGER.info("Save Score...")
            # cacheにスコアを保存
            write_to_cache(evaluation["MatchID"],
                           evaluation["ParticipantID"],
                           evaluation["TrialNo"],
                           current["objective"],
                           current["constraint"],
                           current["info"],
                           score_result["score"],
                           cache)
            
            # 成功試行をDynamo DBに保存
            save_success_score(evaluation["MatchID"],
                               evaluation["ParticipantID"],
                               evaluation["TrialNo"],
                               evaluation["CreatedAt"],
                               started_at,
                               finished_at,
                               score_result["score"],
                               dynamodb)
            LOGGER.info("...Saved")
            
        except KeyboardInterrupt:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            LOGGER.error("Keyboard Interrupt")
            finished_at = datetime.now()
            finished_at = finished_at.isoformat()
            save_failed_score(evaluation["MatchID"],
                              evaluation["ParticipantID"],
                              evaluation["TrialNo"],
                              evaluation["CreatedAt"],
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
            save_failed_score(evaluation["MatchID"],
                              evaluation["ParticipantID"],
                              evaluation["TrialNo"],
                              evaluation["CreatedAt"],
                              started_at,
                              finished_at,
                              format_exc(),
                              dynamodb)
            LOGGER.error(format_exc())
            continue