import boto3
from time import sleep
from typing import Dict



class SQS:
    """
    A wrapper class for interaction with Amazon SQS.

    """

    def __init__(self, queue_name: str, interval: float) -> None:
        """
        Parameters
        ----------
        queue_name: str
            The name of queue.
        interval: float
            Polling interval.
        """
        self.queue_name = queue_name
        self.interval = interval

        access_key_id = ""
        secret_access_key = ""
        region_name = ""
        self.sqs = boto3.client("sqs",
                                region_name=region_name,
                                aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key)
        
        response = self.sqs.create_queue(
            QueueName=queue_name)
        self.queue_url = response["QueueUrl"]
        self.receipt_handle = None

    
    def polling_sqs_message(self) -> Dict[str, str]:
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
        
        message = messages[0]
        self.receipt_handle = message["ReceiptHandle"]

        #
        # Launch a thread to extend the queue re-visibility. (has not been implemented)
        #

        return message


    def delete_sqs_message(self) -> None:
        """
        Delete message.
        
        """

        if self.receipt_handle is None:
            raise Exception("No message handled.")
        
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=self.receipt_handle
        )

        #
        # Stop a thread to extend the queue re-visibility. (has not been implemented)
        #


