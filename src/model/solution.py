from time import sleep
import logging
import json

from utils.dynamoDB import DynamoDB

LOGGER = logging.getLogger(__name__)


class SolutionModel:

    def __init__(self, interval):
        self.variable = None
        self.image = None
        self.environment = None
        self.interval = interval
        self.keys = [{"ID": "Solutions#Match#1#User#1", "Trial" : "1"},
                     {"ID": "Solutions#Match#1#User#1", "Trial" : "2"},
                     {"ID": "Solutions#Match#1#User#2", "Trial" : "1"}]
        self.dynamoDB = DynamoDB()


    def fetch_item(self):
        while True:
            response = {"solutions" : self.keys} # mock, fetch by SQS
            if response["solutions"]:
                break  # solution found
            sleep(self.interval)
        LOGGER.debug(response["solutions"][0])

        solution = self.dynamoDB.fetch_item(response["solutions"][0])
        self.keys = self.keys[1:]

        self.variable = json.dumps(solution["Variable"]) + "\n"
        self.image = "opthub/sphere:latest" # use self.solution[problem ID] or use cache
        self.environment = solution["ProblemEnvironments"]
        return solution, context
