"""Test cases for solution.py."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB
from opthub_runner_admin.models.schema import SolutionSchema
from opthub_runner_admin.models.solution import fetch_solution_by_primary_key


def test_solution_model() -> None:
    """Test for fetch_solution_by_primary_key."""
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

    dynamodb.put_item(
        SolutionSchema(
            {
                "ID": "Solutions#Match#" + match_uuid + "#Team#1",
                "Trial": "00001",
                "MatchID": "Match#" + match_uuid,
                "TrialNo": "00001",
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "ResourceType": "Solution",
                "UserID": "User#1",
                "Variable": [Decimal("0.01"), Decimal("0.01")],
            },
        ),
    )

    solution = fetch_solution_by_primary_key(dynamodb, "Match#" + match_uuid, "Team#1", "00001")

    if solution["variable"] != [0.01, 0.01]:
        msg = "Variable is not correct."
        raise ValueError(msg)
