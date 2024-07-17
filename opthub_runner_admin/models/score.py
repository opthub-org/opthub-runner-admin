"""This module provides functions to save and fetch scores to and from DynamoDB."""

from decimal import Decimal
from typing import TYPE_CHECKING, TypedDict

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.utils.converter import number_to_decimal

if TYPE_CHECKING:
    from opthub_runner_admin.models.schema import FailedScoreSchema, SuccessScoreSchema


class SuccessScoreCreateParams(TypedDict):
    """The input data to create a success score.

    match_id (str): MatchID.
    participant_id (str): ParticipantID.
    trial_no (str): The zero-filled trial number.
    created_at (str): The time when the score to be calculated was created. ISOString format.
    started_at (str): The time when the calculation of the score started. ISOString format.
    finished_at (str): The time when the calculation of the score finished. ISOString format.
    score (float): The score of the evaluation.
    """

    match_id: str
    participant_id: str
    trial_no: str
    created_at: str
    started_at: str
    finished_at: str
    score: float


class FailedScoreCreateParams(TypedDict):
    """The input data to create a failed score.

    match_id (str): MatchID.
    participant_id (str): ParticipantID.
    trial_no (str): The zero-filled trial number.
    created_at (str): The time when the score to be calculated was created. ISOString format.
    started_at (str): The time when the calculation of the score started. ISOString format.
    finished_at (str): The time when the calculation of the score finished. ISOString format.
    error_message (str): The error message shown to the participant when the calculation of score is failed.
    admin_error_message (str): The error message for the admin when the calculation of score is failed.
    """

    match_id: str
    participant_id: str
    trial_no: str
    created_at: str
    started_at: str
    finished_at: str
    error_message: str
    admin_error_message: str


def save_success_score(
    dynamodb: DynamoDB,
    input_item: SuccessScoreCreateParams,
) -> None:
    """Save the success score to DynamoDB.

    Args:
        dynamodb (DynamoDB): The DynamoDB instance.
        input_item (SuccessScoreCreateParams): The input data to create a success score.
    """
    score = number_to_decimal(input_item["score"])
    if not isinstance(score, Decimal):
        msg = "score must be a float"
        raise TypeError(msg)

    score_data: SuccessScoreSchema = {
        "ID": f"Scores#{input_item["match_id"]}#{input_item["participant_id"]}",
        "Trial": f"Success#{input_item["trial_no"]}",
        "TrialNo": input_item["trial_no"],
        "ResourceType": "Score",
        "MatchID": input_item["match_id"],
        "CreatedAt": input_item["created_at"],
        "ParticipantID": input_item["participant_id"],
        "StartedAt": input_item["started_at"],
        "FinishedAt": input_item["finished_at"],
        "Status": "Success",
        "Value": score,
    }
    dynamodb.put_item(score_data)


def save_failed_score(dynamodb: DynamoDB, input_item: FailedScoreCreateParams) -> None:
    """Save the failed score to DynamoDB.

    Args:
        dynamodb (DynamoDB): The DynamoDB instance.
        input_item (FailedScoreCreateParams): The input data to create a failed score.
    """
    score: FailedScoreSchema = {
        "ID": f"Scores#{input_item["match_id"]}#{input_item["participant_id"]}",
        "Trial": f"Failed#{input_item["trial_no"]}",
        "TrialNo": input_item["trial_no"],
        "ResourceType": "Score",
        "MatchID": input_item["match_id"],
        "CreatedAt": input_item["created_at"],
        "ParticipantID": input_item["participant_id"],
        "StartedAt": input_item["started_at"],
        "FinishedAt": input_item["finished_at"],
        "Status": "Failed",
        "ErrorMessage": input_item["error_message"],
        "AdminErrorMessage": input_item["admin_error_message"],
    }
    dynamodb.put_item(score)
