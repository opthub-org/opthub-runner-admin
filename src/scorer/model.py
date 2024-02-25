"""
Input/Output of data.

"""
import logging
import json
from time import sleep
from utils.dynamoDB import DynamoDB

LOGGER = logging.getLogger(__name__)


class ScoreTrial:
    """
    Calculating score of trial.
    
    """
    def __init__(self):
        self.keys = [{"ID": "Evaluations#Match#1#User#1", "Trial" : "Success#1"},
                     {"ID": "Evaluations#Match#1#User#1", "Trial" : "Success#2"},
                     {"ID": "Evaluations#Match#1#User#1", "Trial" : "Success#3"}]

        self.dynamoDB = DynamoDB()

    def fetch_evaluation(self, interval):
        """
        Fetch evaluations per interval.

        """
        while True:
            response = {"evaluations" : self.keys} # mock
            if response["evaluations"]:
                break  # solution found
            sleep(interval)
        LOGGER.debug(response["evaluations"][0])

        self.__current_evaluation = self.dynamoDB.fetch_item(response["evaluations"][0])

        self.__evaluations = self.dynamoDB.fetch_items([{"ID" : self.__current_evaluation["ID"], "Trial" : f"Success#{i}"} for i in range(1, int(self.__current_evaluation["TrialNo"] + 1))], "TrialNo", "Objective", "Constraint", "Info")

        self.__scores = self.dynamoDB.fetch_items([{"ID" : f'Scores#{self.__current_evaluation["MatchID"]}#{self.__current_evaluation["UserID"]}', "Trial" : f"Success#{i}"} for i in range(1, int(self.__current_evaluation["TrialNo"]))], "Score", "TrialNo")
        self.keys = self.keys[1:]
        
        self.current = json.dumps({"objective": self.__current_evaluation["Objective"],
                        "constraint": self.__current_evaluation["Constraint"],
                        "info": self.__current_evaluation["Info"]}) + "\n"
        
        self.history = [dict() for _ in range(int(self.__current_evaluation["TrialNo"]))]
        for eval_data in self.__evaluations:
            if eval_data["TrialNo"] <= self.__current_evaluation["TrialNo"]:
                self.history[eval_data["TrialNo"]]["Objective"] = eval_data["Objective"]
                self.history[eval_data["TrialNo"]]["Constraint"] = eval_data["Constraint"]
                self.history[eval_data["TrialNo"]]["Info"] = eval_data["Info"]
        for score_data in self.__scores:
            if score_data["TrialNo"] < self.__current_evaluation["TrialNo"]:
                self.history[score_data["TrialNo"]] = score_data["Score"]
            
        self.history = json.dumps(self.history) + "\n"

        self.image = "opthub/best:latest" # use self.evaluation[indicator ID] or use cache
        self.environment = self.__current_evaluation["ProblemEnvironments"]
    
    def save_succeeded_score(self, started_at, finished_at, score):
        """
        save score succeeded in calculating to DB.

        """
        # mock
        # output score to DB

    def save_failed_score(self, started_at, finished_at, exc):
        """
        save score failed in calculating to DB.

        """
        # mock
        # output score to DB
        

        
    