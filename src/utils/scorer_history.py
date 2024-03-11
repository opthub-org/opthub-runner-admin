"""
scorerで使うhistoryを作成する関数．

"""
from utils.cache import Cache
from utils.converter import decimal_to_float
from utils.dynamoDB import DynamoDB



def make_history(match_id, participant_id, trial_no, cache : Cache, dynamodb : DynamoDB):
    """
    match_idとparticipant_idを持つ参加者の，trial_noまでのHistoryを作成する関数．

    Parameters
    ----------
    trial_no : int
        TrialNo．
    match_id : str
        MatchID（cacheのキーに用いる）．
    participant_id : str
        ParticipantID（cacheのキーに用いる）．
    cache : Cache
        Historyを作成するためのcache．
    dynamodb : DynamoDB
        cacheにない情報を取ってくるためのDynamoDB．
    
    Return
    ------
    history : dict
        History．
    """
    load_until_trial_no(match_id, participant_id, trial_no, cache, dynamodb)

    history = cache.get_values()
    history = [history[str(i)] for i in range(1, trial_no + 1)]
    
    return history


def load_until_trial_no(match_id, participant_id, trial_no, cache : Cache, dynamodb : DynamoDB):
    """
    loaded_trial_noからtrial_noまでのスコアと評価をバッチで取得し，取得したScoreとEvaluationの情報をcacheに書き込む関数．
    
    Parameters
    ----------
    match_id : str
        MatchID（cacheのキーに用いる）．
    participant_id : str
        ParticipantID（cacheのキーに用いる）．
    trial_no : int
        TrialNo．
    cache : Cache
        書き込む対象のcache．
    dynamodb : DynamoDB
        cacheにない情報を取ってくるためのDynamoDB．

    """
    cache.load(match_id + "#" + participant_id)
    loaded_trial_no = cache.get_length_of_values()

    if loaded_trial_no >= trial_no:
        return
    
    # DBから取ってくるデータのPrimary Keyを定義
    evaluation_primary_keys = [{"ID": "Evaluations#" + match_id + "#" + participant_id,
                                    "Trial": f"Success#{no}"} for no in range(loaded_trial_no + 1, trial_no + 1)]
    score_primary_keys = [{"ID": "Scores#" + match_id + "#" + participant_id,
                                    "Trial": f"Success#{no}"} for no in range(loaded_trial_no + 1, trial_no + 1)]

    # DBからCacheにないデータを取ってくる
    evaluations = dynamodb.batch_get_item(evaluation_primary_keys, "TrialNo", "Objective", "Constraint", "Info")
    scores = dynamodb.batch_get_item(score_primary_keys, "TrialNo", "Score")

    history_after_loaded_trial_no = {} # trial_no番目よりも後(trial_no ~ self.loaded_trial_no)のhistoryのデータ

    # 取ってきたEvaluationとScoreをCacheに格納
    for evaluation in evaluations:
        history_after_loaded_trial_no[str(int(evaluation["TrialNo"]))] = {"objective": decimal_to_float(evaluation["Objective"]),
                                                                          "constraint": decimal_to_float(evaluation["Constraint"]),
                                                                          "info": decimal_to_float(evaluation["Info"])}
    for score in scores:
            history_after_loaded_trial_no[str(int(score["TrialNo"]))]["score"] = decimal_to_float(score["Score"])

            # キャッシュに追加
            cache.append(str(int(score["TrialNo"])), history_after_loaded_trial_no[str(int(score["TrialNo"]))])


def write(match_id, participant_id, trial_no, objective, constraint, info, score, cache : Cache):
    """
    Cacheに書き込む関数．

    Parameters
    ----------
    match_id : str
        MatchID（cacheのキーに用いる）．
    participant_id : str
        ParticipantID（cacheのキーに用いる）．
    trial_no : int
        TrialNo．
    objective : float/list
        Objective．
    constraint : list
        Constraint．
    info : list
        Info．
    score : float
        Score．
    cache : Cache
        書き込む対象のcache．

    """
    cache.load(match_id + "#" + participant_id)
    cache.append(str(trial_no), {"objective": objective, "constraint": constraint, "info": info, "score": score})



def main():
    from utils.converter import number_to_decimal
    cache = Cache()
    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    for i in range(1, 10):
        put_item_evaluation = {"ID": "Evaluations#Match#1#Team#1",
                               "Trial": f"Success#{i}",
                               "TrialNo": i,
                               "ResourceType": "Evaluation",
                               "MatchID": "Match#1",
                               "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
                               "ParticipantID": "Team#1",
                               "StartedAt": f"2024-2-29-15:0{i}:00",
                               "FinishedAt": f"2024-2-29-15:0{i}:30",
                               "Status": "Success",
                               "Objective": [i, i],
                               "Constraint": None,
                               "Info": None
        }
        put_item_score = {"ID": "Scores#Match#1#Team#1",
                          "Trial": f"Success#{i}",
                          "TrialNo": i,
                          "ResourceType": "Score",
                          "MatchID": "Match#1",
                          "CreatedAt": f"2024-3-29-15:0{i - 1}:00",
                          "ParticipantID": "Team#1",
                          "StartedAt": f"2024-3-29-15:0{i}:00",
                          "FinishedAt": f"2024-3-29-15:0{i}:30",
                          "Status": "Success",
                          "Score": number_to_decimal(i/10)
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)
        put_item_evaluation = {"ID": "Evaluations#Match#1#Team#2",
                               "Trial": f"Success#{i}",
                               "TrialNo": i,
                               "ResourceType": "Evaluation",
                               "MatchID": "Match#1",
                               "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
                               "ParticipantID": "Team#2",
                               "StartedAt": f"2024-2-29-15:0{i}:00",
                               "FinishedAt": f"2024-2-29-15:0{i}:30",
                               "Status": "Success",
                               "Objective": [i, i],
                               "Constraint": None,
                               "Info": None
        }
        put_item_score = {"ID": "Scores#Match#1#Team#2",
                          "Trial": f"Success#{i}",
                          "TrialNo": i,
                          "ResourceType": "Score",
                          "MatchID": "Match#1",
                          "CreatedAt": f"2024-3-29-15:0{i - 1}:00",
                          "ParticipantID": "Team#2",
                          "StartedAt": f"2024-3-29-15:0{i}:00",
                          "FinishedAt": f"2024-3-29-15:0{i}:30",
                          "Status": "Success",
                          "Score": number_to_decimal(i/100)
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)
    print("----- history (TrialNo = 1, Team#1) -----")
    history = make_history("Match#1", "Team#1", 1, cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 8, Team#1) -----")
    history = make_history("Match#1", "Team#1", 8, cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- write (TrialNo = 9, Team#1) -----")
    write("Match#1", "Team#1", 9, [9, 9], None, None, number_to_decimal(9/10), cache)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 10, Team#2) -----")
    history = make_history("Match#1", "Team#2", 10, cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 3, Team#1) -----")
    history = make_history("Match#1", "Team#1", 3, cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 5, Team#2) -----")
    history = make_history("Match#1", "Team#2", 5, cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())

if __name__ == "__main__":
    main()