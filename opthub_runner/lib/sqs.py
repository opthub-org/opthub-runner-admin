from time import sleep
from typing import Any, TypedDict

import boto3


class MessageItem(TypedDict):
    """A type for the sqs message item."""

    ParticipantID: str
    TrialNo: str  # zero filled trial number


# TODO: MessageItemを使って適切に型をつける
class Message(TypedDict):
    """A type for the sqs message."""

    ReceiptHandle: str


class SQS:
    """A wrapper class for interaction with Amazon SQS."""

    queue_name: str
    interval: float
    sqs: Any
    receipt_handle: str | None
    queue_url: str

    """A wrapper class for interaction with Amazon SQS."""

    def __init__(self, queue_name: str, interval: float) -> None:
        """Initialize the class.

        Args:
            queue_name (str): The name of the Amazon SQS.
            interval (float): The interval for polling.
        """
        self.queue_name = queue_name
        self.interval = interval

        access_key_id = ""
        secret_access_key = ""
        region_name = ""
        self.sqs = boto3.client(
            "sqs",
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

        response = self.sqs.create_queue(QueueName=queue_name)
        self.queue_url = response["QueueUrl"]
        self.receipt_handle = None

    def polling_sqs_message(self) -> Message:
        """Fetch a message from SQS per interval.

        Returns:
            Message: A message from the SQS.
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

        message: Message = messages[0]
        self.receipt_handle = message["ReceiptHandle"]

        #
        # Launch a thread to extend the queue re-visibility. (has not been implemented)
        #

        return message

    def delete_sqs_message(self) -> None:
        """Delete an message in the sqs."""
        if self.receipt_handle is None:
            msg = "No message handled."
            raise RuntimeError(msg)

        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=self.receipt_handle)

        #
        # Stop a thread to extend the queue re-visibility. (has not been implemented)
        #
