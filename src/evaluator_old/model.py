"""
Input/Output of data.

"""
import logging
import json
from time import sleep
from utils.dynamoDB import DynamoDB


LOGGER = logging.getLogger(__name__)



class EvaluationTrial:
    """
    Evaluate trial.

    """
    def __init__(self):
        self.keys = [{"ID": "Solutions#Match#1#User#1", "Trial" : "1"},
                     {"ID": "Solutions#Match#1#User#1", "Trial" : "2"},
                     {"ID": "Solutions#Match#1#User#2", "Trial" : "1"}]
        self.dynamoDB = DynamoDB()

    def fetch_solution(self, interval):
        """
        Fetch solutions per interval.

        """
        while True:
            response = {"solutions" : self.keys} # mock, fetch by SQS
            if response["solutions"]:
                break  # solution found
            sleep(interval)
        LOGGER.debug(response["solutions"][0])
        
        self.__solution = self.dynamoDB.fetch_item(response["solutions"][0])
        self.keys = self.keys[1:]

        self.image = "opthub/sphere:latest" # use self.solution[problem ID] or use cache
        self.variable = json.dumps(self.__solution["Variable"]) + "\n"
        self.environment = self.__solution["ProblemEnvironments"]
    
    def save_succeeded_evaluation(self, started_at, finished_at, objective, constraint):
        """
        save evaluation succeeded in evaluating to DB.

        """
        evaluation_data = self.__make_succeeded_evaluation_data(started_at, finished_at, objective, constraint)
        self.dynamoDB.put_item(evaluation_data) # output evaluation to DB

    def save_failed_evaluation(self, started_at, finished_at, exc):
        """
        save evaluation failed in evaluating to DB.

        """
        evaluation_data = self.__make_failed_evaluation_data(started_at, finished_at, exc)
        self.dynamoDB.put_item(evaluation_data) # output evaluation to DB

    def __make_succeeded_evaluation_data(self, started_at, finished_at, objective, constraint):
        evaluation = {"ID": f'Evaluations#{self.__solution["MatchID"]}#{self.__solution["UserID"]}',
                     "Trial": f'Success#{self.__solution["Trial"]}',
                     "TrialNo": self.__solution["TrialNo"],
                     "ResourceType": "Evaluation",
                     "CompetitionID": self.__solution["CompetitionID"],
                     "ProblemID": self.__solution["ProblemID"],
                     "IndicatorID": self.__solution["IndicatorID"],
                     "ProblemEnvironments": self.__solution["ProblemEnvironments"],
                     "MethodID": self.__solution["MethodID"],
                     "MatchGroupID": self.__solution["MatchGroupID"],
                     "MatchID": self.__solution["MatchID"],
                     "CreatedAt": self.__solution["CreatedAt"],
                     "UserID": self.__solution["UserID"],
                     "StartedAt": started_at,
                     "FinishedAt": finished_at,
                     "Status": "Success",
                     "FailedNum": 0,
                     "Objective": objective,
                     "Constraint": constraint,
                     "Info": []}
        return evaluation

    def __make_failed_evaluation_data(self, started_at, finished_at, exc):
        evaluation = {"ID": f'Evaluations#{self.__solution["MatchID"]}#{self.__solution["UserID"]}',
                     "Trial": f'Failed#{self.__solution["Trial"]}',
                     "TrialNo": self.__solution["TrialNo"],
                     "ResourceType": "Evaluation",
                     "CompetitionID": self.__solution["CompetitionID"],
                     "ProblemID": self.__solution["ProblemID"],
                     "IndicatorID": self.__solution["IndicatorID"],
                     "ProblemEnvironments": self.__solution["ProblemEnvironments"],
                     "MethodID": self.__solution["MethodID"],
                     "MatchGroupID": self.__solution["MatchGroupID"],
                     "MatchID": self.__solution["MatchID"],
                     "CreatedAt": self.__solution["CreatedAt"],
                      "UserID": self.__solution["UserID"],
                     "StartedAt": started_at,
                     "FinishedAt": finished_at,
                     "Status": "Failed",
                     "FailedNum": 1,
                     "ErrorMessage" : exc}
        return evaluation