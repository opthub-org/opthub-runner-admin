"""
Input/Output of data.

"""
import logging
import json
from time import sleep

LOGGER = logging.getLogger(__name__)


class EvaluationTrial:
    """
    
    """
    def __init__(self):
        pass

    def fetch_solution(self, interval):
        """
        Fetch solutions per interval.

        """
        # while True:
        #     response = {"solutions" : []} # mock
        #     if response["solutions"]:
        #         break  # solution found
        #     sleep(interval)
        # LOGGER.debug(response["solutions"][0])

        # self.__solution = response["solutions"][0]

        self.image = "opthub/sphere:latest" # use self.solution[problem ID] or use cache
        self.variable = json.dumps(2) + "\n"#json.dumps(self.__solution["variable"]) + "\n"
        self.environment = {}# self.__solution["environment"]
    
    def save_succeeded_evaluation(self, started_at, finished_at, objective, constraint):
        """
        save evaluation succeeded in evaluating to DB.

        """
        self.__evaluation = {} # mock
        # output evaluation to DB

    def save_failed_evaluation(self, started_at, finished_at, exc):
        """
        save evaluation failed in evaluating to DB.

        """
        self.__evaluation = {} # mock
        # output evaluation to DB
        


class ScoreTrial:
    """
    
    """
    def __init__(self):
        pass

    def fetch_evaluation(self, interval):
        """
        Fetch evaluations per interval.

        """
        # while True:
        #     response = {"evaluations" : []} # mock
        #     if response["evaluations"]:
        #         break  # solution found
        #     sleep(interval)
        # LOGGER.debug(response["evaluations"][0])

        # self.__evaluations = {{}}
        # self.__scores = {{}}

        self.current = json.dumps({"objective" : [0.5, 0.5], "constraint" : None, "info" : 10}) + "\n"
        self.history = json.dumps([{"objective" : [0.75, 0.25], "constraint" : None, "score" : 5, "info" : 10}, {"objective" : [0.25, 0.75], "constraint" : None, "score" : 4, "info" : 10}]) + "\n"

        self.image = "opthub/hypervolume:latest" # use self.evaluation[indicator ID] or use cache
        self.environment = [{"key" : "HV_REF_POINT", "value" : "[2,2]"}]# self.__solution["environment"]
    
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
        

        
    