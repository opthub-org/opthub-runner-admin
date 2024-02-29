"""
Score関連の操作

"""
from utils.dynamoDB import DynamoDB
from utils.converter import decimal_to_float, number_to_decimal



def save_success_score(match_id, participant_id, trial_no, created_at, started_at, finished_at, score, dynamodb : DynamoDB):
    """
    スコアの計算に成功した場合に，Dynamo DBにScoreを保存するための関数．

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
        Scoreの計算を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        Scoreの計算を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    score : float
        trial_noまでの解の評価系列をスコアリングした結果．

    """

    score = {"ID": f"Scores#{match_id}#{participant_id}",
             "Trial": f"Success#{trial_no}",
             "TrialNo": trial_no,
             "ResourceType": "Score",
             "MatchID": match_id,
             "CreatedAt": created_at,
             "ParticipantID": participant_id,
             "StartedAt": started_at,
             "FinishedAt": finished_at,
             "Status": "Success",
             "Score": number_to_decimal(score)
    }

    dynamodb.put_item(score)


def save_failed_score(match_id, participant_id, trial_no, created_at, started_at, finished_at, error_message, dynamodb : DynamoDB):
    """
    Scoreの計算に失敗した場合に，Dynamo DBにScoreを保存するための関数．

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
        Scoreの計算を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        Scoreの計算を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    error_message : str
        エラーメッセージ．

    """

    failed_count = dynamodb.count_items_with_sort_key_prefix({"ID": f"Scores#{match_id}#{participant_id}"},
                                                              {"Trial": f"Failed#{trial_no}"}) + 1

    score = {"ID": f"Scores#{match_id}#{participant_id}",
             "Trial": f"Failed#{trial_no}#{failed_count}",
             "TrialNo": trial_no,
             "ResourceType": "Score",
             "MatchID": match_id,
             "CreatedAt": created_at,
             "ParticipantID": participant_id,
             "StartedAt": started_at,
             "FinishedAt": finished_at,
             "Status": "Failed",
             "ErrorMessage": error_message
    }

    dynamodb.put_item(score)


def fetch_scores_by_batch(primary_keys, dynamodb : DynamoDB):
    """
    Primary Keyの配列を使って，Dynamo DBから各Primary Keyに対応するScoreを取ってくる関数．

    Parameters
    ----------
    primary_keys : list
        Primary Keyのlist．Primary Keyは{"ID": "Scores#{match_id}#{participant_id}", "Trial" : "Success#{trial_no}"}の形式のdict．
    dynamodb : DynamoDB
        dynamo DBと通信するためのラッパークラスのオブジェクト．

    Return
    ------
    scores : list
        {"ID", "Trial", "Score"}のlist．Primary Key + historyに必要な属性を返す．
    
    """
    scores = dynamodb.batch_get_item(primary_keys, "ID", "Trial", "Score")
    scores = decimal_to_float(scores)
    
    return scores


def main():
    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    save_success_score("Match#1", "Team#1", 1, "2020-2-20-09:00:00",
                       "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                       0.8, dynamodb)
    save_success_score("Match#1", "Team#1", 2, "2020-2-21-09:00:00",
                       "2020-2-26-09:00:00", "2020-2-26-12:00:00",
                       0.2, dynamodb)
    save_success_score("Match#1", "Team#2", 1, "2020-2-20-09:00:00",
                       "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                       0.4, dynamodb)
    save_failed_score("Match#1", "Team#1", 1, "2020-2-20-09:00:00",
                      "2020-2-25-09:00:00", "2020-2-25-12:00:00",
                      "Error Message", dynamodb)
    save_failed_score("Match#1", "Team#1", 1, "2020-2-20-13:00:00",
                      "2020-2-25-14:00:00", "2020-2-25-15:00:00",
                      "Error Message", dynamodb)
    save_failed_score("Match#1", "Team#1", 1, "2020-2-20-16:00:00",
                      "2020-2-25-17:00:00", "2020-2-25-18:00:00",
                      "Error Message", dynamodb)
    
    print("----- fetch scores by batch -----")
    print(fetch_scores_by_batch([
        {"ID": "Scores#Match#1#Team#1", "Trial": "Success#1"},
        {"ID": "Scores#Match#1#Team#1", "Trial": "Success#2"}], dynamodb))


if __name__ == "__main__":
    main()

