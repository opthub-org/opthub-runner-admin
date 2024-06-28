"""This module provides functions to manage the history of the trials."""

from decimal import Decimal
from typing import TypedDict, cast

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.scorer.cache import Cache, Trial
from opthub_runner_admin.utils.converter import decimal_to_float
from opthub_runner_admin.utils.zfill import zfill


class PartialEvaluation(TypedDict):
    """The partial type of the evaluation.

    TrialNo (str): The trial number.
    Objective (object | None): The objective value.
    Constraint (object | None): The constraint value.
    Info (object): The information.
    Feasible (bool | None): The feasibility.
    """

    TrialNo: str
    Objective: object | None
    Constraint: object | None
    Info: object
    Feasible: bool | None


class PartialScore(TypedDict):
    """The partial type of the score.

    TrialNo (str): The trial number.
    Value (float | None): The score.
    """

    TrialNo: str
    Value: Decimal | None


def make_history(
    match_id: str,
    participant_id: str,
    trial_no: str,
    cache: Cache,
    dynamodb: DynamoDB,
) -> list[Trial]:
    """Make the history up to trial_no.

    Args:
        match_id (str): The match ID.
        participant_id (str): The participant ID.
        trial_no (str): The trial number.
        cache (Cache): The cache instance.
        dynamodb (DynamoDB): The DynamoDB instance.

    Returns:
        list[Trial]: The history of the trials.
    """
    load_up_to_trial_no(match_id, participant_id, trial_no, cache, dynamodb)

    history = []

    for hist in cache.get_values():
        if hist["trial_no"] > trial_no:
            break

        history.append(hist)

    return history


def load_up_to_trial_no(match_id: str, participant_id: str, trial_no: str, cache: Cache, dynamodb: DynamoDB) -> None:
    """Load the history up to trial_no.

    Args:
        match_id (str): The match ID.
        participant_id (str): The participant ID.
        trial_no (str): The trial number.
        cache (Cache): The cache instance.
        dynamodb (DynamoDB): The DynamoDB instance.
    """
    cache.load(match_id + "#" + participant_id)
    loaded_trial_no = cache.get_values()[-1]["trial_no"] if len(cache.get_values()) > 0 else None

    # If the loaded trial number is greater than or equal to the trial number, do nothing.
    if loaded_trial_no is not None and loaded_trial_no >= trial_no:
        return

    # fetch evaluations from the database
    evaluations = dynamodb.get_item_between_least_and_greatest(
        f"Evaluations#{match_id}#{participant_id}",
        "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
        "Success#" + zfill(int(trial_no), len(trial_no)),
        ["Objective", "Constraint", "Info", "Feasible", "TrialNo"],
    )
    evaluations = cast(list[PartialEvaluation], evaluations)

    # fetch scores from the database
    scores = dynamodb.get_item_between_least_and_greatest(
        f"Scores#{match_id}#{participant_id}",
        "Success#" + (zfill(int(loaded_trial_no) + 1, len(loaded_trial_no)) if loaded_trial_no is not None else ""),
        "Success#" + zfill(int(trial_no), len(trial_no)),
        ["TrialNo", "Value"],
    )
    scores = cast(list[PartialScore], scores)

    # append the fetched evaluations and scores to the cache
    evaluation_index = 0

    for score in scores:
        if evaluations[evaluation_index]["TrialNo"] > score["TrialNo"]:
            msg = "The evaluation and score do not match."
            raise ValueError(msg)
        while evaluations[evaluation_index]["TrialNo"] < score["TrialNo"]:
            evaluation_index += 1

        evaluation = evaluations[evaluation_index]

        current: Trial = {
            "trial_no": evaluation["TrialNo"],
            "objective": decimal_to_float(evaluation["Objective"]),
            "constraint": decimal_to_float(evaluation["Constraint"]),
            "info": decimal_to_float(evaluation["Info"]),
            "feasible": evaluation["Feasible"],
            "score": cast(float, decimal_to_float(score["Value"])),
        }
        cache.append(current)


def write_to_cache(
    cache: Cache,
    match_id: str,
    participant_id: str,
    trial: Trial,
) -> None:
    """Write the trial to the cache.

    Args:
        cache (Cache): The cache instance.
        match_id (str): The match ID.
        participant_id (str): The participant ID.
        trial (Trial): The trial to write to the cache.
    """
    cache.load(match_id + "#" + participant_id)
    cache.append(trial)
