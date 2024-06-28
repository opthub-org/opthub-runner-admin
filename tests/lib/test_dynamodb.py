"""Test DynamoDB class."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB, DynamoDBOptions, PrimaryKey
from opthub_runner_admin.models.schema import SolutionSchema


def test_dynamodb() -> None:
    """Test DynamoDB class."""
    match_uuid = "dcc32372-f02d-19c7-866d-f9742d5372ca"
    config_file = "opthub_runner/opthub-runner.yml"

    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    dynamodb = DynamoDB(
        DynamoDBOptions(
            {
                "region_name": config["region_name"],
                "aws_access_key_id": config["access_key_id"],
                "aws_secret_access_key": config["secret_access_key"],
                "table_name": config["table_name"],
            },
        ),
    )

    put_items = [
        SolutionSchema(
            {
                "ID": "Solutions#Match#" + match_uuid + "#User#00010",
                "Trial": str(i + 1).zfill(5),
                "TrialNo": str(i + 1).zfill(5),
                "ResourceType": "Solution",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "User#00010",
                "UserID": "User#00010",
                "Variable": [1, 2],
            },
        )
        for i in range(5)
    ]
    for i in range(5):
        dynamodb.put_item(put_items[i])

    try:
        primary_key = PrimaryKey({"ID": "Solutions#Match#" + match_uuid + "#User#00010", "Trial": "00003"})
        if dynamodb.get_item(primary_key) != put_items[2]:
            msg = "dynamodb.get_item(primary_key) != put_items[2]"
            raise ValueError(msg)

        got_items = dynamodb.get_item_between_least_and_greatest(
            "Solutions#Match#" + match_uuid + "#User#00010",
            "00002",
            "00004",
            ["TrialNo", "Variable", "UserID", "MatchID"],
        )
        expected_got_items = [
            {
                "TrialNo": str(i).zfill(5),
                "MatchID": "Match#" + match_uuid,
                "UserID": "User#00010",
                "Variable": [Decimal(1), Decimal(2)],
            }
            for i in range(2, 5)
        ]
        if got_items != expected_got_items:
            msg = f"expected_got_items: {expected_got_items}, but got_items: {got_items}"
            raise ValueError(msg)
    finally:
        for i in range(5):
            dynamodb.table.delete_item(Key={"ID": put_items[i]["ID"], "Trial": put_items[i]["Trial"]})


def test_dynamodb_with_same_item() -> None:
    """Test DynamoDB class."""
    match_uuid = "dcc32372-f02d-19c7-866d-f9742d5372ca"
    config_file = "opthub_runner/opthub-runner.yml"

    if not Path(config_file).exists():
        msg = f"Configuration file not found: {config_file}"
        raise FileNotFoundError(msg)
    with Path(config_file).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    dynamodb = DynamoDB(
        DynamoDBOptions(
            {
                "region_name": config["region_name"],
                "aws_access_key_id": config["access_key_id"],
                "aws_secret_access_key": config["secret_access_key"],
                "table_name": config["table_name"],
            },
        ),
    )

    put_items = [
        SolutionSchema(
            {
                "ID": "Solutions#Match#" + match_uuid + "#User#00010",
                "Trial": str(i + 1).zfill(5),
                "TrialNo": str(i + 1).zfill(5),
                "ResourceType": "Solution",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "User#00010",
                "UserID": "User#00010",
                "Variable": [1, 2],
            },
        )
        for i in range(2)
    ]
    for i in range(2):
        dynamodb.put_item(put_items[i])

    try:
        primary_key = PrimaryKey({"ID": "Solutions#Match#" + match_uuid + "#User#00010", "Trial": "00001"})
        if dynamodb.get_item(primary_key) != put_items[0]:
            msg = "dynamodb.get_item(primary_key) != put_items[0]"
            raise ValueError(msg)

        put_item_with_same_trial_no = SolutionSchema(
            {
                "ID": "Solutions#Match#" + match_uuid + "#User#00010",
                "Trial": str(1).zfill(5),
                "TrialNo": str(1).zfill(5),
                "ResourceType": "Solution",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ParticipantID": "User#00010",
                "UserID": "User#00010",
                "Variable": [100, 200],
            },
        )

        dynamodb.put_item(put_item_with_same_trial_no)

        if dynamodb.get_item(primary_key) != put_items[0]:
            msg = "Item replaced."
            raise ValueError(msg)

    finally:
        for i in range(2):
            dynamodb.table.delete_item(Key={"ID": put_items[i]["ID"], "Trial": put_items[i]["Trial"]})
