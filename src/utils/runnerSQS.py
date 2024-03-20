"""
Amazon SQSをラップするクラス．

"""
from utils.sqs import SQS
import json



class RunnerSQS:
    """
    Amazon SQSをラップするクラス．

    """

    def __init__(self, queue_name, interval):
        """
        Parameters
        ----------
        queue_name : str
            Amazon SQSの名前．
        interval : float
            pollingの間隔．ß
        """
        self.interval = interval
        self.sqs = SQS(queue_name, interval)
    

    def get_partition_key_from_queue(self):
        """
        Partition Keyに使うParticipantID，Trialをqueueから取得する．

        Return
        -------
        data : dict
            ParticipantID，Trialのdict．

        """
        message = self.sqs.polling_sqs_message()
        data = json.loads(message["Body"])

        data["Trial"] = data["TrialNo"]
        
        return data
    
    def delete_partition_key_from_queue(self):
        """
        Delete message (Partition Key) from queue if succeeded in evaluating the solution.
        
        """
        self.sqs.delete_sqs_message()

        return