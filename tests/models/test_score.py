"""Test for score.py."""

from datetime import datetime
from pathlib import Path
from typing import cast

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.models.schema import FailedScoreSchema, SuccessScoreSchema
from opthub_runner_admin.models.score import save_failed_score, save_success_score


def test_score_model() -> None:
    """Test for save_failed_score and save_success_score."""
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
    save_failed_score(
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
        save_success_score(
            dynamodb,
            {
                "trial_no": f"0000{i}",
                "match_id": "Match#" + match_uuid,
                "participant_id": "Team#1",
                "started_at": datetime.now().isoformat(),
                "finished_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "score": i / 10,
            },
        )

    for i in range(1, 3):
        success_item = cast(
            SuccessScoreSchema,
            dynamodb.get_item({"ID": "Scores#Match#" + match_uuid + "#Team#1", "Trial": f"Success#0000{i}"}),
        )
        if float(success_item["Value"]) != i / 10:
            msg = "Failed in saving score."
            raise ValueError(msg)

    failed_item = cast(
        FailedScoreSchema,
        dynamodb.get_item({"ID": "Scores#Match#" + match_uuid + "#Team#1", "Trial": "Failed#00001"}),
    )
    if failed_item["ErrorMessage"] != "TestErrorMessage":
        msg = "Failed in saving score."
        raise ValueError(msg)
