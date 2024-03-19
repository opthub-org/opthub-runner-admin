"""This module provides functions to save and fetch scores to and from DynamoDB."""

from typing import Any

from opthub_runner.utils.converter import number_to_decimal
from opthub_runner.utils.dynamodb import DynamoDB


def save_success_score(
    match_id: str,
    participant_id: str,
    trial_no: str,
    created_at: str,
    started_at: str,
    finished_at: str,
    score: float,
    dynamodb: DynamoDB,
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

    score_data: dict[str, Any] = {
        "ID": f"Scores#{match_id}#{participant_id}",
        "Trial": f"Success#{trial_no}",
        "TrialNo": trial_no,
        "ResourceType": "Score",
        "MatchID": match_id,
        "CreatedAt": created_at,
        "ParticipantID": participant_id,
        "StartedAt": started_at,
        "FinishedAt": finished_at,
        "Status": "Success",
        "Score": number_to_decimal(score),
    }

    dynamodb.put_item(score_data)


def save_failed_score(
    match_id, participant_id, trial_no, created_at, started_at, finished_at, error_message, dynamodb: DynamoDB
) -> None:
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
    score = {
        "ID": f"Scores#{match_id}#{participant_id}",
        "Trial": f"Failed#{trial_no}",
        "TrialNo": trial_no,
        "ResourceType": "Score",
        "MatchID": match_id,
        "CreatedAt": created_at,
        "ParticipantID": participant_id,
        "StartedAt": started_at,
        "FinishedAt": finished_at,
        "Status": "Failed",
        "ErrorMessage": error_message,
    }

    dynamodb.put_item(score)


def main():
    dynamodb = DynamoDB(
        "http://localhost:8000", "localhost", "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev"
    )

    save_success_score(
        "Match#1", "Team#1", "1", "2020-2-20-09:00:00", "2020-2-25-09:00:00", "2020-2-25-12:00:00", 0.8, dynamodb
    )
    save_success_score(
        "Match#1", "Team#1", "2", "2020-2-21-09:00:00", "2020-2-26-09:00:00", "2020-2-26-12:00:00", 0.2, dynamodb
    )
    save_success_score(
        "Match#1", "Team#2", "1", "2020-2-20-09:00:00", "2020-2-25-09:00:00", "2020-2-25-12:00:00", 0.4, dynamodb
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-13:00:00",
        "2020-2-25-14:00:00",
        "2020-2-25-15:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-16:00:00",
        "2020-2-25-17:00:00",
        "2020-2-25-18:00:00",
        "Error Message",
        dynamodb,
    )


if __name__ == "__main__":
    main()
