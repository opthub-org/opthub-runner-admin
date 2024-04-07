"""Test cases for solution.py."""

from datetime import datetime
from decimal import Decimal

from opthub_runner.keys import ACCESS_KEY_ID, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.models.schema import SolutionSchema
from opthub_runner.models.solution import fetch_solution_by_primary_key


def test_solution_model() -> None:
    """Test for fetch_solution_by_primary_key."""
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "region_name": REGION_NAME,
            "table_name": TABLE_NAME,
        },
    )

    dynamodb.put_item(
        SolutionSchema(
            {
                "ID": "Solutions#Match#1#Team#1",
                "Trial": "00001",
                "MatchID": "Match#1",
                "TrialNo": "00001",
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#1",
                "ResourceType": "Solution",
                "UserID": "User#1",
                "Variable": [Decimal("0.01"), Decimal("0.01")],
            },
        ),
    )

    solution = fetch_solution_by_primary_key(dynamodb, "Match#1", "Team#1", "00001")

    if solution["variable"] != [0.01, 0.01]:
        msg = "Variable is not correct."
        raise ValueError(msg)
