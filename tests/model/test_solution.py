from opthub_runner.models.solution import fetch_solution_by_primary_key
from opthub_runner.lib.dynamodb import DynamoDB


def test():
    dynamodb = DynamoDB(
        "http://localhost:8000", "localhost", "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev"
    )
    solution = fetch_solution_by_primary_key("Match#1", "Team#1", "1", dynamodb)
    print("----- solution -----")
    print(solution)
