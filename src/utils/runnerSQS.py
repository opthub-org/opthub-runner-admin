"""
Amazon SQSをラップするクラス．

"""
from time import sleep


class RunnerSQS:
    """
    Amazon SQSをラップするクラス．

    """

    def __init__(self, queue_name):
        """
        Parameter
        ---------
        queue_name : str
            Amazon SQSの名前．

        """
        self.queue_name = queue_name
    

    def get_partition_key_from_queue(self, interval):
        """
        Partition Keyに使うMatchID，ParticipantID，TrialNoをqueueから取得するまでpollingする．

        Parameter
        ---------
        interval : float
            pollingの間隔．

        Return
        -------
        data : dict
            MatchID，ParticipantID，TrialNoのdict．

        """

        while True:
            response = [{"MatchID": "Match#1",
                        "ParticipantID": "Team#1",
                        "TrialNo": 1}] # SQSから取得する部分（未実装）．
            if response:
                break

            sleep(interval)
        
        data = {"MatchID": response[0]["MatchID"],
                "ParticipantID": response[0]["ParticipantID"],
                "TrialNo": response[0]["TrialNo"]}
        
        return data
