"""This module provides functions to save and fetch scores to and from DynamoDB."""

from decimal import Decimal
from typing import TYPE_CHECKING, TypedDict, cast

from opthub_runner.lib.converter import number_to_decimal
from opthub_runner.lib.dynamodb import DynamoDB

if TYPE_CHECKING:
    from opthub_runner.lib.schema import FailedScoreSchema, SuccessScoreSchema


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
    trial_no: int
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
    error_message (str): The error message when the calculation of score is failed.
    """

    match_id: str
    participant_id: str
    trial_no: int
    created_at: str
    started_at: str
    finished_at: str
    error_message: str


def save_success_score(
    dynamodb: DynamoDB,
    input_item: SuccessScoreCreateParams,
) -> None:
    """
    スコアの計算に成功した場合に，Dynamo DBにScoreを保存するための関数．

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
        Scoreの計算を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        Scoreの計算を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    score : float
        trial_noまでの解の評価系列をスコアリングした結果．

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
        "Score": score,
    }
    dynamodb.put_item(score_data)


def save_failed_score(dynamodb: DynamoDB, input_item: FailedScoreCreateParams) -> None:
    """
    Scoreの計算に失敗した場合に，Dynamo DBにScoreを保存するための関数．

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
        Scoreの計算を開始した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    finished_at : str
        Scoreの計算を終了した時刻．yyyy-mm-dd-hh:mm:ssのフォーマット．
    error_message : str
        エラーメッセージ．

    """
    score: FailedScoreSchema = {
        "ID": f"Scores#{input_item["match_id"]}#{input_item["participant_id"]}",
        "Trial": f"Failed#{input_item["trial_no"]}",
        "TrialNo": int(input_item["trial_no"]),
        "ResourceType": "Score",
        "MatchID": input_item["match_id"],
        "CreatedAt": input_item["created_at"],
        "ParticipantID": input_item["participant_id"],
        "StartedAt": input_item["started_at"],
        "FinishedAt": input_item["finished_at"],
        "Status": "Failed",
        "ErrorMessage": input_item["error_message"],
    }

    dynamodb.put_item(score)