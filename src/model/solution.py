"""
Solutionの取得

"""
import logging

from utils.dynamoDB import DynamoDB

LOGGER = logging.getLogger(__name__)


def fetch_solution_by_primary_key(match_id, participant_id, trial_no, dynamodb : DynamoDB):
    """
    Primary Keyを使ってDynamo DBからSolutionを取ってくる関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial_no : int
        試行番号．
    dynamodb : DynamoDB
        dynamo DBと通信するためのラッパークラスのオブジェクト．
    
    Return
    ------
    solution : dict
        取ってきたSolution．
    """
    primary_key = {"ID" : f"Solutions#{match_id}#{participant_id}",
                   "Trial" : str(trial_no)}
    solution = dynamodb.get_item(primary_key)

    return solution


def main():
    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    solution = fetch_solution_by_primary_key("Match#1", "Team#1", 1, dynamodb)
    print("----- solution -----")
    print(solution)


if __name__ == "__main__":
    main()




