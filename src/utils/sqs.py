import boto3
from time import sleep
from typing import Dict
from utils.keys import ACCESS_KEY_ID, REGION_NAME, SECRET_ACCESS_KEY, QUEUE_URL, TABLE_NAME



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


        self.sqs = boto3.client("sqs",
                                region_name=REGION_NAME,
                                aws_access_key_id=ACCESS_KEY_ID,
                                aws_secret_access_key=SECRET_ACCESS_KEY)
        
        self.queue_url = QUEUE_URL
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


def main():
    from utils.dynamodb import DynamoDB

    dynamodb = DynamoDB(REGION_NAME,
                        ACCESS_KEY_ID,
                        SECRET_ACCESS_KEY,
                        TABLE_NAME)
    sqs = SQS(REGION_NAME, 2.0)

    response = sqs.sqs.purge_queue(QueueUrl=sqs.queue_url)
    print(response)
    
    for i in range(1, 3):
        put_item = {"ID": "Solutions#Match#1#Team#1",
                    "Trial": str(i).zfill(2),
                    "ParticipantID": "Team#1",
                    "Variable": [1, 2],
                    "UserID": "User#1",
                    "MatchID": "Match#1", 
                    "CreatedAt": f"2024-03-05-00:{str(i).zfill(2)}:00",
                    "ResourceType": "Solutions",
                    "TrialNo": str(i).zfill(2)}
        dynamodb.put_item(put_item)

    message = sqs.polling_sqs_message()

    print(message)
    
    sqs.delete_sqs_message()

    message = sqs.polling_sqs_message()

    print(message)
    
    sqs.delete_sqs_message()


if __name__ == "__main__":
    main()
