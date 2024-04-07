"""Tests for the SQS classes."""

from datetime import datetime
from decimal import Decimal

from opthub_runner.keys import (
    ACCESS_KEY_ID,
    EVALUATOR_QUEUE_NAME,
    EVALUATOR_QUEUE_URL,
    REGION_NAME,
    SCORER_QUEUE_NAME,
    SCORER_QUEUE_URL,
    SECRET_ACCESS_KEY,
    TABLE_NAME,
)
from opthub_runner.lib.dynamodb import DynamoDB, DynamoDBOptions
from opthub_runner.lib.sqs import EvaluationMessage, EvaluatorSQS, ScoreMessage, ScorerSQS, SQSOptions
from opthub_runner.models.schema import FailedEvaluationSchema, SolutionSchema, SuccessEvaluationSchema


def test_evaluator_sqs() -> None:
    """Test EvaluatorSQS."""
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

    interval = 1.0
    sqs = EvaluatorSQS(
        interval,
        SQSOptions(
            {
                "queue_name": EVALUATOR_QUEUE_NAME,
                "queue_url": EVALUATOR_QUEUE_URL,
                "aws_access_key_id": ACCESS_KEY_ID,
                "aws_secret_access_key": SECRET_ACCESS_KEY,
                "region_name": REGION_NAME,
            },
        ),
    )

    sqs.sqs.purge_queue(QueueUrl=sqs.queue_url)

    put_items = [
        SolutionSchema(
            {
                "ID": "Solutions#Match#1#Team#1",
                "Trial": str(i + 1).zfill(5),
                "ParticipantID": "Team#1",
                "Variable": [1, 2],
                "UserID": "User#1",
                "MatchID": "Match#1",
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

    interval = 1.0
    sqs = ScorerSQS(
        interval,
        SQSOptions(
            {
                "queue_name": SCORER_QUEUE_NAME,
                "queue_url": SCORER_QUEUE_URL,
                "aws_access_key_id": ACCESS_KEY_ID,
                "aws_secret_access_key": SECRET_ACCESS_KEY,
                "region_name": REGION_NAME,
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
                "participant_id": put_items[i]["ParticipantID"],
                "trial": put_items[i]["Trial"],
                "trial_no": put_items[i]["TrialNo"],
            },
        )

        if expected_message not in messages:
            msg = "Expected message not in messages."
            raise ValueError(msg)

        messages.remove(expected_message)
