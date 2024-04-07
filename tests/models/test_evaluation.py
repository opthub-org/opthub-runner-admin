"""Test for evaluation.py."""

from datetime import datetime

from opthub_runner.keys import ACCESS_KEY_ID, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.models.evaluation import (
    SuccessEvaluation,
    fetch_success_evaluation_by_primary_key,
    save_failed_evaluation,
    save_success_evaluation,
)


def test_evaluation_model() -> None:
    """Test for save_failed_evaluation, save_success_evaluation, and fetch_success_evaluation_by_primary_key."""
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "region_name": REGION_NAME,
            "table_name": TABLE_NAME,
        },
    )
    save_failed_evaluation(
        dynamodb,
        {
            "trial_no": "00001",
            "match_id": "Match#1",
            "participant_id": "Team#1",
            "started_at": datetime.now().isoformat(),
            "finished_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "error_message": "TestErrorMessage",
        },
    )

    for i in range(1, 3):
        save_success_evaluation(
            dynamodb,
            {
                "trial_no": f"0000{i}",
                "match_id": "Match#1",
                "participant_id": "Team#1",
                "started_at": datetime.now().isoformat(),
                "finished_at": datetime.now().isoformat(),
                "constraint": None,
                "created_at": datetime.now().isoformat(),
                "feasible": None,
                "info": None,
                "objective": [1 + i / 10, 1 + i / 5],
            },
        )

        expected_evaluation = SuccessEvaluation(
            {
                "match_id": "Match#1",
                "trial_no": "00001",
                "objective": [1.1, 1.2],
                "constraint": None,
                "feasible": None,
                "info": None,
                "participant_id": "Team#1",
            },
        )

        if fetch_success_evaluation_by_primary_key(dynamodb, "Match#1", "Team#1", "00001") != expected_evaluation:
            msg = "Evaluation is not correct."
            raise ValueError(msg)
