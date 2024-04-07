"""Tests for history.py."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from opthub_runner.keys import ACCESS_KEY_ID, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.scorer.cache import Cache, Trial
from opthub_runner.scorer.history import make_history, write_to_cache

if TYPE_CHECKING:
    from opthub_runner.models.schema import FailedScoreSchema, SuccessEvaluationSchema, SuccessScoreSchema


def test_history_all_success() -> None:
    """Test for make_history and write_to_cache."""
    cache = Cache()
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "region_name": REGION_NAME,
            "table_name": TABLE_NAME,
        },
    )

    expected_history = [
        Trial(
            {
                "TrialNo": str(i).zfill(5),
                "Objective": [i, i],
                "Constraint": None,
                "Info": None,
                "Score": i / 10,
                "Feasible": None,
            },
        )
        for i in range(1, 10)
    ]

    for i in range(1, 10):
        put_item_evaluation: SuccessEvaluationSchema = {
            "ID": "Evaluations#Match#1#Team#1",
            "Trial": f"Success#{str(i).zfill(5)}",
            "TrialNo": str(i).zfill(5),
            "ResourceType": "Evaluation",
            "MatchID": "Match#1",
            "CreatedAt": datetime.now().isoformat(),
            "ParticipantID": "Team#1",
            "StartedAt": datetime.now().isoformat(),
            "FinishedAt": datetime.now().isoformat(),
            "Status": "Success",
            "Objective": [i, i],
            "Constraint": None,
            "Info": None,
            "Feasible": None,
        }
        put_item_score: SuccessScoreSchema = {
            "ID": "Scores#Match#1#Team#1",
            "Trial": f"Success#{str(i).zfill(5)}",
            "TrialNo": str(i).zfill(5),
            "ResourceType": "Score",
            "MatchID": "Match#1",
            "CreatedAt": datetime.now().isoformat(),
            "ParticipantID": "Team#1",
            "StartedAt": datetime.now().isoformat(),
            "FinishedAt": datetime.now().isoformat(),
            "Status": "Success",
            "Score": Decimal(str(i / 10)),
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)

    history = make_history("Match#1", "Team#1", "00002", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    if cache.get_values() != expected_history[:2]:
        msg = "Cache values are not correct."
        raise ValueError(msg)

    history = make_history("Match#1", "Team#1", "00006", cache, dynamodb)

    if history != expected_history[:6]:
        msg = "History is not correct."
        raise ValueError(msg)

    write_to_cache(
        cache,
        "Match#1",
        "Team#1",
        {
            "TrialNo": "00007",
            "Objective": [7, 7],
            "Constraint": None,
            "Feasible": None,
            "Info": None,
            "Score": 7 / 10,
        },
    )
    if cache.get_values() != expected_history[:7]:
        msg = "Cache values are not correct."
        raise ValueError(msg)

    history = make_history("Match#1", "Team#1", "00003", cache, dynamodb)

    if history != expected_history[:3]:
        msg = "History is not correct."
        raise ValueError(msg)

    if cache.get_values() != expected_history[:7]:
        msg = "Cache values are not correct."
        raise ValueError(msg)


def test_history_not_all_success() -> None:
    """Test for make_history when not all trials are successful."""
    cache = Cache()
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "region_name": REGION_NAME,
            "table_name": TABLE_NAME,
        },
    )

    success_trial_no = [1, 2, 5]
    failed_trial_no = [3, 4]

    expected_history = [
        Trial(
            {
                "TrialNo": str(i).zfill(5),
                "Objective": [i, i],
                "Constraint": None,
                "Info": None,
                "Score": i / 10,
                "Feasible": None,
            },
        )
        for i in success_trial_no
    ]

    for i in range(1, 6):
        put_item_evaluation: SuccessEvaluationSchema = {
            "ID": "Evaluations#Match#1#Team#1",
            "Trial": f"Success#{str(i).zfill(5)}",
            "TrialNo": str(i).zfill(5),
            "ResourceType": "Evaluation",
            "MatchID": "Match#1",
            "CreatedAt": datetime.now().isoformat(),
            "ParticipantID": "Team#1",
            "StartedAt": datetime.now().isoformat(),
            "FinishedAt": datetime.now().isoformat(),
            "Status": "Success",
            "Objective": [i, i],
            "Constraint": None,
            "Info": None,
            "Feasible": None,
        }

        dynamodb.put_item(put_item_evaluation)

        if i in success_trial_no:
            put_item_score_success: SuccessScoreSchema = {
                "ID": "Scores#Match#1#Team#1",
                "Trial": f"Success#{str(i).zfill(5)}",
                "TrialNo": str(i).zfill(5),
                "ResourceType": "Score",
                "MatchID": "Match#1",
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "Status": "Success",
                "Score": Decimal(str(i / 10)),
            }
            dynamodb.put_item(put_item_score_success)
        elif i in failed_trial_no:
            put_item_score_failed: FailedScoreSchema = {
                "ID": "Scores#Match#1#Team#1",
                "Trial": f"Failed#{str(i).zfill(5)}",
                "TrialNo": str(i).zfill(5),
                "ResourceType": "Score",
                "MatchID": "Match#1",
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "Status": "Failed",
                "ErrorMessage": "TestErrorMessage",
            }
            dynamodb.put_item(put_item_score_failed)

    history = make_history("Match#1", "Team#1", "00002", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    history = make_history("Match#1", "Team#1", "00004", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    history = make_history("Match#1", "Team#1", "00005", cache, dynamodb)

    if history != expected_history:
        msg = "History is not correct."
        raise ValueError(msg)
