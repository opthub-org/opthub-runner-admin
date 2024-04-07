"""Test DynamoDB class."""

from datetime import datetime

from opthub_runner.keys import (
    ACCESS_KEY_ID,
    REGION_NAME,
    SECRET_ACCESS_KEY,
    TABLE_NAME,
)
from opthub_runner.lib.dynamodb import DynamoDB, DynamoDBOptions, PrimaryKey
from opthub_runner.models.schema import SolutionSchema


def test_dynamodb() -> None:
    """Test DynamoDB class."""
    dynamodb = DynamoDB(
        DynamoDBOptions(
            {
                "region_name": REGION_NAME,
                "aws_access_key_id": ACCESS_KEY_ID,
                "aws_secret_access_key": SECRET_ACCESS_KEY,
                "table_name": TABLE_NAME,
            },
        ),
    )

    put_items = [
        SolutionSchema(
            {
                "ID": "Solutions#Match#10#Team#00010",
                "Trial": str(i + 1).zfill(5),
                "TrialNo": str(i + 1).zfill(5),
                "ResourceType": "Solution",
                "MatchID": "Match#10",
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "Team#00010",
                "UserID": "User#1",
                "Variable": [1, 2],
            },
        )
        for i in range(5)
    ]
    for i in range(5):
        dynamodb.put_item(put_items[i])

    primary_key = PrimaryKey({"ID": "Solutions#Match#10#Team#00010", "Trial": "00003"})
    if dynamodb.get_item(primary_key) != put_items[2]:
        msg = "dynamodb.get_item(primary_key) != put_items[2]"
        raise ValueError(msg)

    got_items = dynamodb.get_item_between_least_and_greatest(
        "Solutions#Match#10#Team#00010",
        "00002",
        "00004",
        ["TrialNo", "Variable", "UserID", "MatchID"],
    )
    expected_got_items = [
        {
            "TrialNo": str(i).zfill(5),
            "MatchID": "Match#10",
            "UserID": "User#1",
            "Variable": [1, 2],
        }
        for i in range(2, 5)
    ]
    if got_items != expected_got_items:
        msg = "got_items != expected_got_items"
        raise ValueError(msg)
