"""
scorerで使うhistoryを作成する関数．

"""

from typing import TypedDict, cast

from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.scorer.cache import Cache, Trial
from opthub_runner.utils.converter import decimal_to_float
from opthub_runner.utils.zfill import zfill


class PartialEvaluation(TypedDict):
    TrialNo: str
    Objective: object | None
    Constraint: object | None
    Info: object
    Feasible: bool | None


class PartialScore(TypedDict):
    TrialNo: str
    Score: object | None


def make_history(match_id: str, participant_id: str, trial_no: str, cache: Cache, dynamodb: DynamoDB) -> list[Trial]:
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
    history : list
        History．
    """
    load_until_trial_no(match_id, participant_id, trial_no, cache, dynamodb)

    history = []

    for hist in cache.get_values():
        history.append(hist)
        if hist["TrialNo"] == trial_no:
            break

    return history


def load_until_trial_no(match_id: str, participant_id: str, trial_no: str, cache: Cache, dynamodb: DynamoDB) -> None:
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
    evaluations = dynamodb.get_item_between_least_and_greatest(
        f"Evaluations#{match_id}#{participant_id}",
        "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
        "Success#" + zfill(int(trial_no), len(trial_no)),
        ["Objective", "Constraint", "Info", "Feasible", "TrialNo"],
    )
    evaluations = cast(list[PartialEvaluation], evaluations)
    scores = dynamodb.get_item_between_least_and_greatest(
        f"Scores#{match_id}#{participant_id}",
        "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
        "Success#" + zfill(int(trial_no), len(trial_no)),
        ["TrialNo", "Score"],
    )
    scores = cast(list[PartialScore], scores)

    for evaluation, score in zip(evaluations, scores, strict=True):
        # 取ってきたEvaluationとScoreをCacheに格納

        current: Trial = {
            "TrialNo": evaluation["TrialNo"],
            "Objective": decimal_to_float(evaluation["Objective"]),
            "Constraint": decimal_to_float(evaluation["Constraint"]),
            "Info": decimal_to_float(evaluation["Info"]),
            "Feasible": evaluation["Feasible"],
            "Score": cast(float, decimal_to_float(score["Score"])),
        }
        cache.append(current)


def write_to_cache(
    cache: Cache,
    match_id: str,
    participant_id: str,
    trial: Trial,
) -> None:
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
    cache.append(trial)
