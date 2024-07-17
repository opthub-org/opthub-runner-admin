"""Test for evaluation.py."""

from datetime import datetime
from pathlib import Path

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.models.evaluation import (
    SuccessEvaluation,
    fetch_success_evaluation_by_primary_key,
    save_failed_evaluation,
    save_success_evaluation,
)


def test_evaluation_model() -> None:
    """Test for save_failed_evaluation, save_success_evaluation, and fetch_success_evaluation_by_primary_key."""
    config_file = "opthub_runner/opthub-runner.yml"
    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    match_uuid = "5a3fcd7d-3b7e-4a97-bac3-0531cfca538e"

    dynamodb = DynamoDB(
        {
            "aws_access_key_id": config["access_key_id"],
            "aws_secret_access_key": config["secret_access_key"],
            "region_name": config["region_name"],
            "table_name": config["table_name"],
        },
    )
    save_failed_evaluation(
        dynamodb,
        {
            "trial_no": "00001",
            "match_id": "Match#" + match_uuid,
            "participant_id": "Team#1",
            "started_at": datetime.now().isoformat(),
            "finished_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "error_message": "TestErrorMessage",
            "admin_error_message": "TestAdminErrorMessage",
        },
    )

    for i in range(1, 3):
        save_success_evaluation(
            dynamodb,
            {
                "trial_no": f"0000{i}",
                "match_id": "Match#" + match_uuid,
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
                "match_id": "Match#" + match_uuid,
                "trial_no": "00001",
                "objective": [1.1, 1.2],
                "constraint": None,
                "feasible": None,
                "info": None,
                "participant_id": "Team#1",
            },
        )

        if (
            fetch_success_evaluation_by_primary_key(dynamodb, "Match#" + match_uuid, "Team#1", "00001")
            != expected_evaluation
        ):
            msg = "Evaluation is not correct."
            raise ValueError(msg)
