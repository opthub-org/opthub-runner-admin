"""
scorerで使うhistoryを作成する関数．

"""
from utils.cache import Cache
from utils.converter import decimal_to_float
from utils.dynamodb import DynamoDB
from utils.zfill import zfill


def make_history(match_id, participant_id, trial_no, cache : Cache, dynamodb : DynamoDB):
    """
    match_idとparticipant_idを持つ参加者の，trial_noまでのHistoryを作成する関数．

    Parameters
    ----------
    match_id : str
        MatchID（cacheのキーに用いる）．
    participant_id : str
        ParticipantID（cacheのキーに用いる）．
    trial_no : str
        TrialNo．
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

    history = []
    for hist in cache.get_values():
        history.append(hist)
        if hist["TrialNo"] == trial_no:
            break
    
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
    trial_no : str
        TrialNo．
    cache : Cache
        書き込む対象のcache．
    dynamodb : DynamoDB
        cacheにない情報を取ってくるためのDynamoDB．

    """
    cache.load(match_id + "#" + participant_id)
    loaded_trial_no = cache.get_values()[-1]["TrialNo"] if len(cache.get_values()) > 0 else None

    if loaded_trial_no is not None and loaded_trial_no >= trial_no:
        return
    
    # DBからCacheにないデータを取ってくる
    evaluations = dynamodb.get_item_between_least_and_greatest({"ID": f"Evaluations#{match_id}#{participant_id}"},
                                                               "Trial",
                                                               "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
                                                               "Success#" + zfill(int(trial_no), len(trial_no)),
                                                               "Objective", "Constraint", "Info", "Feasible", "TrialNo")
    scores = dynamodb.get_item_between_least_and_greatest({"ID": f"Scores#{match_id}#{participant_id}"},
                                                          "Trial",
                                                          "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
                                                          "Success#" + zfill(int(trial_no), len(trial_no)),
                                                          "TrialNo", "Score")

    for evaluation, score in zip(evaluations, scores):
        if evaluation["TrialNo"] != score["TrialNo"]:
            raise Exception("Invalid Evaluations and Scores.")
        print(evaluation, score)
        
            # 取ってきたEvaluationとScoreをCacheに格納
        cache.append({"TrialNo": evaluation["TrialNo"],
                      "objective": decimal_to_float(evaluation["Objective"]),
                      "constraint": decimal_to_float(evaluation["Constraint"]),
                      "info": decimal_to_float(evaluation["Info"]),
                      "feasible": evaluation["Feasible"],
                      "score": decimal_to_float(score["Score"])})



def write_to_cache(match_id, participant_id, trial_no, objective, constraint, info, score, cache : Cache):
    """
    Cacheに書き込む関数．

    Parameters
    ----------
    match_id : str
        MatchID（cacheのキーに用いる）．
    participant_id : str
        ParticipantID（cacheのキーに用いる）．
    trial_no : str
        TrialNo．
    objective : float/list
        Objective．
    constraint : list
        Constraint．
    info : list
        Info．
    score : float
        Score．
    feasible : bool
        Feasible.
    cache : Cache
        書き込む対象のcache．

    """
    cache.load(match_id + "#" + participant_id)
    cache.append({"TrialNo": trial_no, "objective": objective, "constraint": constraint, "info": info, "score": score})



def main():
    from utils.converter import number_to_decimal
    cache = Cache()
    dynamodb = DynamoDB("localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    for i in range(1, 11):
        put_item_evaluation = {"ID": "Evaluations#Match#1#Team#1",
                               "Trial": f"Success#{str(i).zfill(4)}",
                               "TrialNo": str(i).zfill(4),
                               "ResourceType": "Evaluation",
                               "MatchID": "Match#1",
                               "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
                               "ParticipantID": "Team#1",
                               "StartedAt": f"2024-2-29-15:0{i}:00",
                               "FinishedAt": f"2024-2-29-15:0{i}:30",
                               "Status": "Success",
                               "Objective": [i, i],
                               "Constraint": None,
                               "Info": None,
                               "Feasible": None
        }
        put_item_score = {"ID": "Scores#Match#1#Team#1",
                          "Trial": f"Success#{str(i).zfill(4)}",
                          "TrialNo": str(i).zfill(4),
                          "ResourceType": "Score",
                          "MatchID": "Match#1",
                          "CreatedAt": f"2024-3-29-15:0{i - 1}:00",
                          "ParticipantID": "Team#1",
                          "StartedAt": f"2024-3-29-15:0{i}:00",
                          "FinishedAt": f"2024-3-29-15:0{i}:30",
                          "Status": "Success",
                          "Score": number_to_decimal(i/10),
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)
        put_item_evaluation = {"ID": "Evaluations#Match#1#Team#2",
                               "Trial": f"Success#{str(i).zfill(4)}",
                               "TrialNo": str(i).zfill(4),
                               "ResourceType": "Evaluation",
                               "MatchID": "Match#1",
                               "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
                               "ParticipantID": "Team#2",
                               "StartedAt": f"2024-2-29-15:0{i}:00",
                               "FinishedAt": f"2024-2-29-15:0{i}:30",
                               "Status": "Success",
                               "Objective": [i, i],
                               "Constraint": None,
                               "Info": None,
                               "Feasible": None
        }
        put_item_score = {"ID": "Scores#Match#1#Team#2",
                          "Trial": f"Success#{str(i).zfill(4)}",
                          "TrialNo": str(i).zfill(4),
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
    history = make_history("Match#1", "Team#1", "0001", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 8, Team#1) -----")
    history = make_history("Match#1", "Team#1", "0008", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- write (TrialNo = 9, Team#1) -----")
    write_to_cache("Match#1", "Team#1", "0009", [9, 9], None, None, number_to_decimal(9/10), cache)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 10, Team#2) -----")
    history = make_history("Match#1", "Team#2", "0010", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 3, Team#1) -----")
    history = make_history("Match#1", "Team#1", "0003", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 5, Team#2) -----")
    history = make_history("Match#1", "Team#2", "0005", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())

if __name__ == "__main__":
    main()