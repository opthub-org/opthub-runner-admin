"""This module provides functions to save and fetch evaluations to and from DynamoDB."""

from typing import Literal, TypedDict

from opthub_runner.utils.converter import decimal_to_float, number_to_decimal
from opthub_runner.utils.dynamodb import DynamoDB


class Evaluation(TypedDict):
    """This class represents the competition type."""

    Status: Literal["Success", "Failed"]
    Objective: object | None
    Constraint: object | None
    Info: object | None


def save_success_evaluation(
    match_id: str,
    participant_id: str,
    trial_no: str,
    created_at: str,
    started_at: str,
    finished_at: str,
    objective: float | list[float],
    constraint: float | list[float] | None,
    info: object,
    feasible: bool | None,
    dynamodb: DynamoDB,
) -> None:
    """Save the evaluation information to DynamoDB when the evaluation is successful.

    Args:
        match_id (str): MatchID.
        participant_id (str): ParticipantID.
        trial_no (str): The zero-filled trial number.
        created_at (str): The time when the solution to be evaluated was created. ISOString format.
        started_at (str): The time when the evaluation of the solution started. ISOString format.
        finished_at (str): The time when the evaluation of the solution finished. ISOString format.
        objective (float | list[float]):
            The value of the objective function when the user-submitted solution was evaluated.
            If it is a single-objective, it is a float, and if it is a multi-objective, it is a list of floats.
        constraint (float | list[float] | None):
            The value of the constraint when the user-submitted solution was evaluated.
        info (object): The accompanying information when the user-submitted solution was evaluated.
        feasible (bool | None): The feasibility of the user-submitted solution.
        dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.
    """
    evaluation = {
        "ID": f"Evaluations#{match_id}#{participant_id}",
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
        "Feasible": feasible,
    }

    dynamodb.put_item(evaluation)


def save_failed_evaluation(
    match_id: str,
    participant_id: str,
    trial_no: str,
    created_at: str,
    started_at: str,
    finished_at: str,
    error_message: str,
    dynamodb: DynamoDB,
) -> None:
    """Save the evaluation information to DynamoDB when the evaluation is failed.

    match_id (str): MatchID.
    participant_id (str): ParticipantID.
    trial_no (str): The zero-filled trial number.
    created_at (str): The time when the solution to be evaluated was created. ISOString format.
    started_at (str): The time when the evaluation of the solution started. ISOString format.
    finished_at (str): The time when the evaluation of the solution finished. ISOString format.
    error_message (str): The error message when the evaluation is failed.
    dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.
    """
    evaluation = {
        "ID": f"Evaluations#{match_id}#{participant_id}",
        "Trial": f"Failed#{trial_no}",
        "TrialNo": trial_no,
        "ResourceType": "Evaluation",
        "MatchID": match_id,
        "CreatedAt": created_at,
        "ParticipantID": participant_id,
        "StartedAt": started_at,
        "FinishedAt": finished_at,
        "Status": "Failed",
        "ErrorMessage": error_message,
    }

    dynamodb.put_item(evaluation)


def fetch_evaluation_by_primary_key(match_id: str, participant_id: str, trial: str, dynamodb: DynamoDB) -> Evaluation:
    """Fetch the evaluation from DynamoDB by primary key.

    Args:
        match_id (str): MatchID.
        participant_id (str): ParticipantID.
        trial (str): The trial number.
        dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.

    Returns:
        Evaluation: The fetched evaluation.
    """
    primary_key = {"ID": f"Evaluations#{match_id}#{participant_id}", "Trial": trial}
    evaluation: Evaluation = dynamodb.get_item(primary_key)

    # decimalのままだとScoreの計算に使いにくい属性をfloatに変換
    if evaluation["Status"] == "Success":
        evaluation["Objective"] = decimal_to_float(evaluation["Objective"])
        evaluation["Constraint"] = decimal_to_float(evaluation["Constraint"])
        evaluation["Info"] = decimal_to_float(evaluation["Info"])

    return evaluation


def main() -> None:
    dynamodb = DynamoDB(
        "http://localhost:8000",
        "localhost",
        "aaaaa",
        "aaaaa",
        "opthub-dynamodb-participant-trials-dev",
    )

    save_success_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        [1.1, 2.2],
        None,
        None,
        None,
        dynamodb,
    )
    save_success_evaluation(
        "Match#1",
        "Team#1",
        "2",
        "2020-2-21-09:00:00",
        "2020-2-26-09:00:00",
        "2020-2-26-12:00:00",
        [2.2, 4.7],
        None,
        None,
        None,
        dynamodb,
    )
    save_success_evaluation(
        "Match#1",
        "Team#2",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        [2.5, 3.1],
        None,
        None,
        None,
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-13:00:00",
        "2020-2-25-14:00:00",
        "2020-2-25-15:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-16:00:00",
        "2020-2-25-17:00:00",
        "2020-2-25-18:00:00",
        "Error Message",
        dynamodb,
    )

    print("----- fetch evaluations by primary key -----")
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#1", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#2", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#3", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#4", dynamodb))


if __name__ == "__main__":
    main()
