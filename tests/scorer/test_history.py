"""Tests for history.py."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.scorer.cache import Cache, Trial
from opthub_runner_admin.scorer.history import make_history

if TYPE_CHECKING:
    from opthub_runner_admin.models.schema import FailedScoreSchema, SuccessEvaluationSchema, SuccessScoreSchema


def test_history_all_success() -> None:
    """Test for make_history and write_to_cache."""
    config_file = "opthub_runner/opthub-runner.yml"
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    cache = Cache()

    match_uuid = "5a3fcd7d-3b7e-4a97-bac3-0531cfca538e"

    dynamodb = DynamoDB(
        {
            "aws_access_key_id": config["access_key_id"],
            "aws_secret_access_key": config["secret_access_key"],
            "region_name": config["region_name"],
            "table_name": config["table_name"],
        },
    )

    expected_history = [
        Trial(
            {
                "trial_no": str(i).zfill(5),
                "objective": [i, i],
                "constraint": None,
                "info": None,
                "score": i / 10,
                "feasible": None,
            },
        )
        for i in range(1, 10)
    ]

    for i in range(1, 10):
        put_item_evaluation: SuccessEvaluationSchema = {
            "ID": "Evaluations#Match#" + match_uuid + "#Team#1",
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
            "IgnoreStream": False,
        }
        put_item_score: SuccessScoreSchema = {
            "ID": "Scores#Match#" + match_uuid + "#Team#1",
            "Trial": f"Success#{str(i).zfill(5)}",
            "TrialNo": str(i).zfill(5),
            "ResourceType": "Score",
            "MatchID": "Match#" + match_uuid,
            "CreatedAt": datetime.now().isoformat(),
            "ParticipantID": "Team#1",
            "StartedAt": datetime.now().isoformat(),
            "FinishedAt": datetime.now().isoformat(),
            "Status": "Success",
            "Value": Decimal(str(i / 10)),
            "IgnoreStream": False,
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)

    history = make_history("Match#" + match_uuid, "Team#1", "00002", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    if cache.get_values() != expected_history[:2]:
        msg = "Cache values are not correct."
        raise ValueError(msg)

    history = make_history("Match#" + match_uuid, "Team#1", "00006", cache, dynamodb)

    if history != expected_history[:6]:
        msg = "History is not correct."
        raise ValueError(msg)

    history = make_history("Match#" + match_uuid, "Team#1", "00003", cache, dynamodb)

    if history != expected_history[:3]:
        msg = "History is not correct."
        raise ValueError(msg)

    if cache.get_values() != expected_history[:6]:
        msg = "Cache values are not correct."
        raise ValueError(msg)


def test_history_not_all_success() -> None:
    """Test for make_history when not all trials are successful."""
    config_file = "opthub_runner/opthub-runner.yml"
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    match_uuid = "5a3fcd7d-3b7e-4a97-bac3-0531cfca538e"

    cache = Cache()
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": config["access_key_id"],
            "aws_secret_access_key": config["secret_access_key"],
            "region_name": config["region_name"],
            "table_name": config["table_name"],
        },
    )

    success_trial_no = [1, 2, 5]
    failed_trial_no = [3, 4]

    expected_history = [
        Trial(
            {
                "trial_no": str(i).zfill(5),
                "objective": [i, i],
                "constraint": None,
                "info": None,
                "score": i / 10,
                "feasible": None,
            },
        )
        for i in success_trial_no
    ]

    for i in range(1, 6):
        put_item_evaluation: SuccessEvaluationSchema = {
            "ID": "Evaluations#Match#" + match_uuid + "#Team#1",
            "Trial": f"Success#{str(i).zfill(5)}",
            "TrialNo": str(i).zfill(5),
            "ResourceType": "Evaluation",
            "MatchID": "Match#" + match_uuid,
            "CreatedAt": datetime.now().isoformat(),
            "ParticipantID": "Team#1",
            "StartedAt": datetime.now().isoformat(),
            "FinishedAt": datetime.now().isoformat(),
            "Status": "Success",
            "Objective": [i, i],
            "Constraint": None,
            "Info": None,
            "Feasible": None,
            "IgnoreStream": False,
        }

        dynamodb.put_item(put_item_evaluation)

        if i in success_trial_no:
            put_item_score_success: SuccessScoreSchema = {
                "ID": "Scores#Match#" + match_uuid + "#Team#1",
                "Trial": f"Success#{str(i).zfill(5)}",
                "TrialNo": str(i).zfill(5),
                "ResourceType": "Score",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "Status": "Success",
                "Value": Decimal(str(i / 10)),
                "IgnoreStream": False,
            }
            dynamodb.put_item(put_item_score_success)
        elif i in failed_trial_no:
            put_item_score_failed: FailedScoreSchema = {
                "ID": "Scores#Match#" + match_uuid + "#Team#1",
                "Trial": f"Failed#{str(i).zfill(5)}",
                "TrialNo": str(i).zfill(5),
                "ResourceType": "Score",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "Status": "Failed",
                "ErrorMessage": "TestErrorMessage",
                "AdminErrorMessage": "TestAdminErrorMessage",
                "IgnoreStream": False,
            }
            dynamodb.put_item(put_item_score_failed)

    history = make_history("Match#" + match_uuid, "Team#1", "00002", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    history = make_history("Match#" + match_uuid, "Team#1", "00004", cache, dynamodb)

    if history != expected_history[:2]:
        msg = "History is not correct."
        raise ValueError(msg)

    history = make_history("Match#" + match_uuid, "Team#1", "00005", cache, dynamodb)

    if history != expected_history:
        msg = "History is not correct."
        raise ValueError(msg)
