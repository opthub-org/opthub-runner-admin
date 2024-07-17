"""Tests for the SQS classes."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml

from opthub_runner_admin.lib.dynamodb import DynamoDB, DynamoDBOptions
from opthub_runner_admin.lib.sqs import EvaluationMessage, EvaluatorSQS, ScoreMessage, ScorerSQS, SQSOptions
from opthub_runner_admin.models.schema import FailedEvaluationSchema, SolutionSchema, SuccessEvaluationSchema


def test_evaluator_sqs() -> None:
    """Test EvaluatorSQS."""
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

    match_uuid = "dcc32372-f02d-19c7-866d-f9742d5372ca"
    interval = 1.0

    sqs = EvaluatorSQS(
        interval,
        SQSOptions(
            {
                "queue_name": config["evaluator_queue_name"],
                "queue_url": config["evaluator_queue_url"],
                "aws_access_key_id": config["access_key_id"],
                "aws_secret_access_key": config["secret_access_key"],
                "region_name": config["region_name"],
            },
        ),
    )

    sqs.sqs.purge_queue(QueueUrl=sqs.queue_url)

    put_items = [
        SolutionSchema(
            {
                "ID": "Solutions#Match#" + match_uuid + "#User#1",
                "Trial": str(i + 1).zfill(5),
                "ParticipantID": "User#1",
                "Variable": [Decimal(1), Decimal(2)],
                "UserID": "User#1",
                "MatchID": "Match#" + match_uuid,
                "CreatedAt": datetime.now().isoformat(),
                "ResourceType": "Solution",
                "TrialNo": str(i + 1).zfill(5),
            },
        )
        for i in range(3)
    ]

    for i in range(3):
        dynamodb.put_item(put_items[i])

    messages = []
    for _ in range(3):
        message = sqs.get_message_from_queue()
        sqs.delete_message_from_queue()

        messages.append(message)

    for i in range(3):
        expected_message = EvaluationMessage(
            {
                "match_id": put_items[i]["MatchID"],
                "participant_id": put_items[i]["ParticipantID"],
                "trial": put_items[i]["TrialNo"],
                "trial_no": put_items[i]["TrialNo"],
            },
        )

        if expected_message not in messages:
            msg = "Expected message not in messages."
            raise ValueError(msg)

        messages.remove(expected_message)


def test_scorer_sqs() -> None:
    """Test ScorerSQS."""
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

    interval = 1.0
    sqs = ScorerSQS(
        interval,
        SQSOptions(
            {
                "queue_name": config["scorer_queue_name"],
                "queue_url": config["scorer_queue_url"],
                "aws_access_key_id": config["access_key_id"],
                "aws_secret_access_key": config["secret_access_key"],
                "region_name": config["region_name"],
            },
        ),
    )

    sqs.sqs.purge_queue(QueueUrl=sqs.queue_url)

    put_items_success = [
        SuccessEvaluationSchema(
            {
                "ID": "Evaluations#Match#1#Team#1",
                "Trial": "Success#" + str(i + 1).zfill(5),
                "ParticipantID": "Team#1",
                "MatchID": "Match#1",
                "CreatedAt": datetime.now().isoformat(),
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "ResourceType": "Evaluation",
                "TrialNo": str(i + 1).zfill(5),
                "Status": "Success",
                "Objective": Decimal(str(1.2 + i)),
                "Constraint": 1,
                "Info": {},
                "Feasible": True,
            },
        )
        for i in range(3)
    ]
    put_items_failed = [
        FailedEvaluationSchema(
            {
                "ID": "Evaluations#Match#1#Team#1",
                "Trial": "Failed#" + str(i + 1).zfill(5),
                "ParticipantID": "Team#1",
                "MatchID": "Match#1",
                "CreatedAt": datetime.now().isoformat(),
                "StartedAt": datetime.now().isoformat(),
                "FinishedAt": datetime.now().isoformat(),
                "ResourceType": "Evaluation",
                "Status": "Failed",
                "ErrorMessage": "KeyboardInterrupt\n",
                "AdminErrorMessage": "KeyboardInterrupt\n",
                "TrialNo": str(i + 1).zfill(5),
            },
        )
        for i in range(3, 5)
    ]

    put_items = put_items_failed + put_items_success

    for i in range(5):
        dynamodb.put_item(put_items[i])

    messages = []
    for _ in range(3):
        message = sqs.get_message_from_queue()
        sqs.delete_message_from_queue()

        messages.append(message)

    for i in range(5):
        if put_items[i]["Status"] != "Success":
            continue
        expected_message = ScoreMessage(
            {
                "match_id": put_items[i]["MatchID"],
                "participant_id": put_items[i]["ParticipantID"],
                "trial": put_items[i]["Trial"],
                "trial_no": put_items[i]["TrialNo"],
            },
        )

        if expected_message not in messages:
            msg = "Expected message not in messages."
            raise ValueError(msg)

        messages.remove(expected_message)
