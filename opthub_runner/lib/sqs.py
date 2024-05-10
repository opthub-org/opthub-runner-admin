"""This module communicates with Amazon SQS."""

import json
from threading import Thread
from time import sleep, time
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

    match_id: str
    participant_id: str
    trial: str
    trial_no: str


class ScoreMessage(TypedDict):
    """The message from SQS for scoring."""

    match_id: str
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

        # Launch a thread to extend the queue re-visibility.
        self.visibility_timeout_extender: Thread = Thread(
            target=self.__extend_visibility_timeout,
            args=(),
        )
        # Set the thread as a daemon. When the main thread exits, the daemon thread will exit.
        self.visibility_timeout_extender.setDaemon(True)

        self.visibility_timeout_extender.start()
        self.start: float | None = None

    def delete_message_from_queue(self) -> None:
        """Delete the message from SQS."""
        if self.receipt_handle is None:
            msg = "No message handled."
            raise RuntimeError(msg)

        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=self.receipt_handle)

        # Stop a thread to extend the queue re-visibility.
        if self.visibility_timeout_extender is None:
            msg = "Visibility timeout extender is None."
            raise ValueError(msg)

        self.receipt_handle = None
        self.start = None

    def _polling_sqs_message(self) -> Message:
        """Polling the message from SQS.

        Returns:
            Message: The message from SQS.
        """
        while True:
            self.start = time()

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

        return message

    def __extend_visibility_timeout(self) -> None:
        """Extend the visibility timeout of the message."""
        if self.visibility_timeout_extender is None:
            msg = "Visibility timeout extender is None."
            raise RuntimeError(msg)

        current_visibility_timeout = 8

        while True:
            if self.receipt_handle is None:
                current_visibility_timeout = 8
                sleep(1)
                continue

            if self.start is None:
                msg = "Message is handled, but start is None."
                raise ValueError(msg)

            current_time = time()

            if current_time - self.start < current_visibility_timeout - 4:
                sleep(1)
                continue

            self.sqs.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=self.receipt_handle,
                VisibilityTimeout=current_visibility_timeout * 2,
            )

            current_visibility_timeout *= 2


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
            "match_id": body["MatchID"],
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
            "match_id": body["MatchID"],
            "participant_id": body["ParticipantID"],
            "trial": "Success#" + body["TrialNo"],
            "trial_no": body["TrialNo"],
        }

        return score_message
