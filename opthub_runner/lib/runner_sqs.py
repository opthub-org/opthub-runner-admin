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
        # self.response = [{"ParticipantID": "Team#1", "Trial": "001"},
        #     {"ParticipantID": "Team#1", "Trial": "002"},
        #     {"ParticipantID": "Team#1", "Trial": "003"}]
        self.response = [
            {"ParticipantID": "Team#1", "Trial": "Success#001"},
            {"ParticipantID": "Team#1", "Trial": "Success#002"},
            {"ParticipantID": "Team#1", "Trial": "Success#003"},
        ]

    def get_partition_key_from_queue(self, interval):
        """
        Partition Keyに使うParticipantID，TrialNoをqueueから取得するまでpollingする．

        Parameter
        ---------
        interval : float
            pollingの間隔．

        Return
        -------
        data : dict
            ParticipantID，Trialのdict．

        """

        while True:
            # SQSから取得する部分（未実装）．
            if self.response:
                break

            sleep(interval)

        data = {"ParticipantID": self.response[0]["ParticipantID"], "Trial": self.response[0]["Trial"]}
        self.response = self.response[1:]

        return data
