"""
Amazon SQSをラップするクラス．

"""

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
    participant_id: str
    trial: str


class ScoreMessage(TypedDict):
    participant_id: str
    trial: str


class RunnerSQS:
    """
    Amazon SQSをラップするクラス．

    """

    def __init__(self, interval: float, options: SQSOptions) -> None:
        """
        Parameters
        ----------
        queue_name : str
            Amazon SQSの名前．
        interval : float
            pollingの間隔．
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
        self.receipt_handle = None

    def delete_partition_key_from_queue(self) -> None:
        """
        Delete message from queue if succeeded in evaluating the solution.

        """

        if self.receipt_handle is None:
            msg = "No message handled."
            raise RuntimeError(msg)

        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=self.receipt_handle)

        #
        # Stop a thread to extend the queue re-visibility. (has not been implemented)
        #

    def __polling_sqs_message(self) -> Message:
        """
        fetch a message from SQS per interval.

        Return
        ------
        message: dict
            Message fetched from SQS.
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
    def get_message_from_queue(self) -> EvaluationMessage:
        """
        Partition Keyに使うParticipantID，Trialをqueueから取得する．

        Return
        -------
        data : dict
            ParticipantID，Trialのdict．

        """
        message = self.__polling_sqs_message()
        body = json.loads(message["body"])

        evaluation_message: EvaluationMessage = {"participant_id": body["ParticipantID"], "trial": body["trial_no"]}

        return evaluation_message


class ScorerSQS(RunnerSQS):
    def get_partition_key_from_queue(self) -> ScoreMessage:
        """
        Partition Keyに使うParticipantID，Trialをqueueから取得する．

        Return
        -------
        data : dict
            ParticipantID，Trialのdict．

        """
        message = self.__polling_sqs_message()
        body = json.loads(message["body"])

        score_message: ScoreMessage = {"participant_id": body["ParticipantID"], "trial": "Success#" + body["trial_no"]}

        return score_message
