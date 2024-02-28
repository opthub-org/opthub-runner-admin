"""
Evaluation関連の操作

"""
import logging

from utils.dynamoDB import DynamoDB

LOGGER = logging.getLogger(__name__)


def save_success_evaluation(match_id, participant_id, trial_no, created_at, started_at, finished_at, objective, constraint, info, dynamodb : DynamoDB):
    """
    評価に成功した場合に，Dynamo DBにEvaluationを保存するための関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial_no : int
        試行回数．
    created_at : str
        Solutionが作られた時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    started_at : str
        解の評価を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        解の評価を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    objective : float or list
        ユーザが送信した解を評価した時の目的関数の値（単目的、多目的で変化）．
    constraint : list?
        ユーザが送信した解を評価した時の制約条件の値．
    info : list?
        ユーザが送信した解を評価した時の付随情報．


    """
    evaluation = {"ID": f"Evaluations#{match_id}#{participant_id}",
                  "Trial": f"Success#{trial_no}",
                  "TrialNo": trial_no,
                  "ResourceType": "Evaluation",
                  "MatchID": match_id,
                  "CreatedAt": created_at,
                  "ParticipantID": participant_id,
                  "StartedAt": started_at,
                  "FinishedAt": finished_at,
                  "Status": "Success",
                  "Objective": objective,
                  "Constraint": constraint,
                  "Info": info
    }

    dynamodb.put_item(evaluation)

