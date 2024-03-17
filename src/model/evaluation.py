"""
Evaluation関連の操作

"""

from utils.dynamodb import DynamoDB
from utils.converter import number_to_decimal, decimal_to_float, decimal_to_int



def save_success_evaluation(match_id, participant_id, trial_no, created_at, started_at, finished_at, objective, constraint, info, feasible, dynamodb : DynamoDB):
    """
    評価に成功した場合に，Dynamo DBにEvaluationを保存するための関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial_no : str
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
    feasible : bool
        ユーザが送信した解が実行可能かどうか．

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
                  "Objective": number_to_decimal(objective),
                  "Constraint": number_to_decimal(constraint),
                  "Info": number_to_decimal(info),
                  "Feasible": feasible
    }

    dynamodb.put_item(evaluation)


def save_failed_evaluation(match_id, participant_id, trial_no, created_at, started_at, finished_at, error_message, dynamodb : DynamoDB):
    """
    評価に失敗した場合に，Dynamo DBにEvaluationを保存するための関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial_no : str
        試行回数．
    created_at : str
        Solutionが作られた時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    started_at : str
        解の評価を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        解の評価を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    error_message : str
        エラーメッセージ．

    """
    evaluation = {"ID": f"Evaluations#{match_id}#{participant_id}",
                  "Trial": f"Failed#{trial_no}",
                  "TrialNo": trial_no,
                  "ResourceType": "Evaluation",
                  "MatchID": match_id,
                  "CreatedAt": created_at,
                  "ParticipantID": participant_id,
                  "StartedAt": started_at,
                  "FinishedAt": finished_at,
                  "Status": "Failed",
                  "ErrorMessage": error_message
    }

    dynamodb.put_item(evaluation)


def fetch_evaluation_by_primary_key(match_id, participant_id, trial, dynamodb : DynamoDB):
    """
    Primary Keyを使ってDynamo DBからEvaluationを取ってくる関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial_no : str
        "Success/Failed#" + 試行番号．
    dynamodb : DynamoDB
        dynamo DBと通信するためのラッパークラスのオブジェクト．
    
    Return
    ------
    evaluation : dict
        取ってきたEvaluation．
    """
    primary_key = {"ID" : f"Evaluations#{match_id}#{participant_id}",
                   "Trial" : trial}
    evaluation = dynamodb.get_item(primary_key)

    # decimalのままだとScoreの計算に使いにくい属性をfloatに変換
    if evaluation["Status"] == "Success":
        evaluation["Objective"] = decimal_to_float(evaluation["Objective"])
        evaluation["Constraint"] = decimal_to_float(evaluation["Constraint"])
        evaluation["Info"] = decimal_to_float(evaluation["Info"])

    return evaluation


def main():
    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    save_success_evaluation("Match#1", "Team#1", "1", "2020-2-20-09:00:00",
                            "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                            [1.1, 2.2], None, None, None, dynamodb)
    save_success_evaluation("Match#1", "Team#1", "2", "2020-2-21-09:00:00",
                            "2020-2-26-09:00:00", "2020-2-26-12:00:00",
                            [2.2, 4.7], None, None, None, dynamodb)
    save_success_evaluation("Match#1", "Team#2", "1", "2020-2-20-09:00:00",
                            "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                            [2.5, 3.1], None, None, None, dynamodb)
    save_failed_evaluation("Match#1", "Team#1", "1", "2020-2-20-09:00:00",
                            "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                            "Error Message", dynamodb)
    save_failed_evaluation("Match#1", "Team#1", "1", "2020-2-20-13:00:00",
                            "2020-2-25-14:00:00", "2020-2-25-15:00:00",
                            "Error Message", dynamodb)
    save_failed_evaluation("Match#1", "Team#1", "1", "2020-2-20-16:00:00",
                            "2020-2-25-17:00:00", "2020-2-25-18:00:00",
                            "Error Message", dynamodb)
    
    print("----- fetch evaluations by primary key -----")
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#1", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#2", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#3", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#4", dynamodb))

if __name__ == "__main__":
    main()
