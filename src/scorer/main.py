from datetime import datetime
import signal
import logging
from traceback import format_exc
import json

from utils.runnerSQS import RunnerSQS
from utils.dynamoDB import DynamoDB
from utils.execute_in_docker import execute_in_docker
from model.match import fetch_match_indicator_by_id
from model.evaluation import fetch_evaluation_by_primary_key
from model.score import save_success_score, save_failed_score
from utils.scorer_history import make_history, write
from utils.cache import Cache

LOGGER = logging.getLogger(__name__)


def calculate_score(ctx, **kwargs):
    """
    スコア計算プロセスのコントローラーを行う関数．

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

    # cacheファイルの管理用
    cache = Cache()
    
    n_score = 1

    while n_score < 2:
        n_score += 1
        LOGGER.info("==================== Calculating score: %d ====================", n_score)

        try:
            # Partition KeyのためのMatchID，ParticipantID，TrialNoを取得
            LOGGER.info("Find Evaluation to calculate score...")
            partition_key_data = sqs.get_partition_key_from_queue(kwargs["interval"])
            LOGGER.info("...Found")

            # MatchIDからIndicatorEnvironmentsとIndicatorDockerImageを取得
            LOGGER.info("Fetch indicator data from DB...")
            indicator_data = fetch_match_indicator_by_id(partition_key_data["MatchID"])
            LOGGER.info("...Fetched")

            # Partition Keyを使ってDynamo DBからEvaluationを取得
            LOGGER.info("Fetch Evaluation from DB...")
            evaluation = fetch_evaluation_by_primary_key(partition_key_data["MatchID"],
                                                         partition_key_data["ParticipantID"],
                                                         partition_key_data["Trial"],
                                                         dynamodb)
            LOGGER.info("...Fetched")

            # currentとhistoryを作成（Dockerの入力）
            LOGGER.info("Make history...")
            current = {"Objective": evaluation["Objective"],
                       "Constraint": evaluation["Constraint"],
                       "Info": evaluation["Info"]}
            history = make_history(evaluation["MatchID"],
                                   evaluation["ParticipantID"],
                                   evaluation["TrialNo"] - 1,
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
            started_at = started_at.strftime('%Y-%m-%d-%H:%M:%S')
            LOGGER.info(f"Started at : {started_at}")

            # Docker Imageを使ってScoreを取得
            score_result = execute_in_docker(indicator_data["IndicatorDockerImage"],
                                             indicator_data["IndicatorEnvironments"],
                                             kwargs["command"],
                                             kwargs["timeout"],
                                             kwargs["rm"],
                                             json.dumps(current) + "\n",
                                             json.dumps(history) + "\n")
            
            LOGGER.info("...Calculated")
            # スコア計算終了時刻の記録
            finished_at = datetime.now()
            finished_at = finished_at.strftime('%Y-%m-%d-%H:%M:%S')
            LOGGER.info(f"Finished at : {finished_at}")

            LOGGER.info("Save Score...")
            # cacheにスコアを保存
            write(evaluation["MatchID"],
                  evaluation["ParticipantID"],
                  evaluation["TrialNo"],
                  current["Objective"],
                  current["Constraint"],
                  current["Info"],
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
            finished_at = finished_at.strftime('%Y-%m-%d-%H:%M:%S')
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
            finished_at = finished_at.strftime('%Y-%m-%d-%H:%M:%S')
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
        print(json.dumps(history))
        n_score += 1


    




