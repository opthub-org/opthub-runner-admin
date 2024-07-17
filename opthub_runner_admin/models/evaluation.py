"""This module provides functions to save and fetch evaluations to and from DynamoDB."""

from typing import TypedDict, cast

from opthub_runner_admin.lib.dynamodb import DynamoDB, PrimaryKey
from opthub_runner_admin.models.schema import FailedEvaluationSchema, SuccessEvaluationSchema
from opthub_runner_admin.utils.converter import decimal_to_float, number_to_decimal


class SuccessEvaluationCreateParams(TypedDict):
    """The input data to create a success evaluation.

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
    """

    match_id: str
    participant_id: str
    trial_no: str
    created_at: str
    started_at: str
    finished_at: str
    objective: float | list[float]
    constraint: float | list[float] | None
    info: object | None
    feasible: bool | None


class FailedEvaluationCreateParams(TypedDict):
    """The input data to create a failed evaluation.

    match_id (str): MatchID.
    participant_id (str): ParticipantID.
    trial_no (str): The zero-filled trial number.
    created_at (str): The time when the solution to be evaluated was created. ISOString format.
    started_at (str): The time when the evaluation of the solution started. ISOString format.
    finished_at (str): The time when the evaluation of the solution finished. ISOString format.
    error_message (str): The error message shown to the participant when the evaluation is failed.
    admin_error_message (str): The error message for the admin when the evaluation is failed.
    """

    match_id: str
    participant_id: str
    trial_no: str
    created_at: str
    started_at: str
    finished_at: str
    error_message: str
    admin_error_message: str


class SuccessEvaluation(TypedDict):
    """The fetched success evaluation.

    match_id (str): MatchID.
    participant_id (str): ParticipantID.
    trial_no (str): The zero-filled trial number.
    objective (object): The value of the objective function when the user-submitted solution was evaluated.
    constraint (object | None): The value of the constraint when the user-submitted solution was evaluated.
    info (object | None): The accompanying information when the user-submitted solution was evaluated.
    feasible (bool | None): The feasibility of the user-submitted solution.
    """

    match_id: str
    participant_id: str
    trial_no: str
    objective: object
    constraint: object | None
    info: object | None
    feasible: bool | None


def save_success_evaluation(
    dynamodb: DynamoDB,
    input_item: SuccessEvaluationCreateParams,
) -> None:
    """Save the evaluation information to DynamoDB when the evaluation is success.

    Args:
        input_item (SuccessEvaluationCreateInput): The input data to create a success evaluation.
        dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.
    """
    evaluation: SuccessEvaluationSchema = {
        "ID": f"Evaluations#{input_item["match_id"]}#{input_item["participant_id"]}",
        "Trial": f"Success#{input_item["trial_no"]}",
        "TrialNo": input_item["trial_no"],
        "ResourceType": "Evaluation",
        "MatchID": input_item["match_id"],
        "CreatedAt": input_item["created_at"],
        "ParticipantID": input_item["participant_id"],
        "StartedAt": input_item["started_at"],
        "FinishedAt": input_item["finished_at"],
        "Status": "Success",
        "Objective": number_to_decimal(input_item["objective"]),
        "Constraint": number_to_decimal(input_item["constraint"]),
        "Info": number_to_decimal(input_item["info"]),
        "Feasible": input_item["feasible"],
    }

    dynamodb.put_item(evaluation)


def save_failed_evaluation(
    dynamodb: DynamoDB,
    input_item: FailedEvaluationCreateParams,
) -> None:
    """Save the evaluation information to DynamoDB when the evaluation is failed.

    Args:
        input_item (FailedEvaluationCreateInput): The input data to create a failed evaluation.
        dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.
    """
    evaluation: FailedEvaluationSchema = {
        "ID": f"Evaluations#{input_item["match_id"]}#{input_item['participant_id']}",
        "Trial": f"Failed#{input_item["trial_no"]}",
        "TrialNo": input_item["trial_no"],
        "ResourceType": "Evaluation",
        "MatchID": input_item["match_id"],
        "CreatedAt": input_item["created_at"],
        "ParticipantID": input_item["participant_id"],
        "StartedAt": input_item["started_at"],
        "FinishedAt": input_item["finished_at"],
        "Status": "Failed",
        "ErrorMessage": input_item["error_message"],
        "AdminErrorMessage": input_item["admin_error_message"],
    }
    dynamodb.put_item(evaluation)


def fetch_success_evaluation_by_primary_key(
    dynamodb: DynamoDB,
    match_id: str,
    participant_id: str,
    trial_no: str,
) -> SuccessEvaluation:
    """Fetch the evaluation from DynamoDB by primary key.

    Args:
        match_id (str): MatchID.
        participant_id (str): ParticipantID.
        trial_no (str): The trial number.
        dynamodb (DynamoDB): Dynamo DB Wrapper object to communicate with Dynamo DB.

    Returns:
        Evaluation: The fetched evaluation.
    """
    primary_key: PrimaryKey = {
        "ID": f"Evaluations#{match_id}#{participant_id}",
        "Trial": "Success#" + trial_no,
    }

    evaluation = cast(SuccessEvaluationSchema | None, dynamodb.get_item(primary_key))

    if evaluation is None:
        msg = "Evaluation not found"
        raise ValueError(msg)

    return {
        "match_id": evaluation["MatchID"],
        "participant_id": evaluation["ParticipantID"],
        "trial_no": evaluation["TrialNo"],
        "objective": decimal_to_float(evaluation["Objective"]),
        "constraint": decimal_to_float(evaluation["Constraint"]),
        "info": evaluation["Info"],
        "feasible": evaluation["Feasible"],
    }
