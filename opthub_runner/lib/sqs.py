"""This module communicates with Amazon SQS."""

import json
from time import sleep
from typing import TypedDict

import boto3


class Message(TypedDict):
    """The message from SQS."""

    receipt_handle: str
    body: str


class SQSOptions(TypedDict):
    """The options for SQS."""

    queue_name: str
    queue_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str


class EvaluationMessage(TypedDict):
    """The message from SQS for evaluation."""

    participant_id: str
    trial: str
    trial_no: str


class ScoreMessage(TypedDict):
    """The message from SQS for scoring."""

    participant_id: str
    trial: str
    trial_no: str


class RunnerSQS:
    """The class to communicate with Amazon SQS."""

    def __init__(self, interval: float, options: SQSOptions) -> None:
        """Initialize the class.

        Args:
            interval (float): The interval to fetch messages from SQS.
            options (SQSOptions): The options for SQS.
        """
        self.queue_name = options["queue_name"]
        self.interval = interval

        self.sqs = boto3.client(
            "sqs",
            region_name=options["region_name"],
            aws_access_key_id=options["aws_access_key_id"],
            aws_secret_access_key=options["aws_secret_access_key"],
        )

        self.queue_url = options["queue_url"]
        self.receipt_handle: str | None = None

    def delete_message_from_queue(self) -> None:
        """Delete the message from SQS."""
        if self.receipt_handle is None:
            msg = "No message handled."
            raise RuntimeError(msg)

        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=self.receipt_handle)

        #
        # Stop a thread to extend the queue re-visibility. (has not been implemented)
        #

    def _polling_sqs_message(self) -> Message:
        """Polling the message from SQS.

        Returns:
            Message: The message from SQS.
        """
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
            )
            messages = response.get("Messages", [])

            if messages:
                break
            sleep(self.interval)

        message: Message = {"receipt_handle": messages[0]["ReceiptHandle"], "body": messages[0]["Body"]}
        self.receipt_handle = messages[0]["ReceiptHandle"]

        #
        # Launch a thread to extend the queue re-visibility. (has not been implemented)
        #

        return message


class EvaluatorSQS(RunnerSQS):
    """The class to communicate with Amazon SQS for evaluation."""

    def get_message_from_queue(self) -> EvaluationMessage:
        """Get the message from SQS.

        Returns:
            EvaluationMessage: The message from SQS for evaluation.
        """
        message = self._polling_sqs_message()
        body = json.loads(message["body"])

        evaluation_message: EvaluationMessage = {
            "participant_id": body["ParticipantID"],
            "trial": body["TrialNo"],
            "trial_no": body["TrialNo"],
        }

        return evaluation_message


class ScorerSQS(RunnerSQS):
    """The class to communicate with Amazon SQS for scoring."""

    def get_message_from_queue(self) -> ScoreMessage:
        """Get the message from SQS.

        Returns:
            ScoreMessage: The message from SQS for scoring.
        """
        message = self._polling_sqs_message()
        body = json.loads(message["body"])

        score_message: ScoreMessage = {
            "participant_id": body["ParticipantID"],
            "trial": "Success#" + body["TrialNo"],
            "trial_no": body["TrialNo"],
        }

        return score_message
