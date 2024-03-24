from opthub_runner.models.evaluation import save_failed_evaluation, save_success_evaluation
from opthub_runner.lib.dynamodb import DynamoDB


def test():
    dynamodb = DynamoDB(
        "http://localhost:8000",
        "localhost",
        "aaaaa",
        "aaaaa",
        "opthub-dynamodb-participant-trials-dev",
    )

    save_success_evaluation(
        dynamodb,
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        [1.1, 2.2],
        None,
        None,
        None,
    )
    save_success_evaluation(
        "Match#1",
        "Team#1",
        "2",
        "2020-2-21-09:00:00",
        "2020-2-26-09:00:00",
        "2020-2-26-12:00:00",
        [2.2, 4.7],
        None,
        None,
        None,
        dynamodb,
    )
    save_success_evaluation(
        "Match#1",
        "Team#2",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        [2.5, 3.1],
        None,
        None,
        None,
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-13:00:00",
        "2020-2-25-14:00:00",
        "2020-2-25-15:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_evaluation(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-16:00:00",
        "2020-2-25-17:00:00",
        "2020-2-25-18:00:00",
        "Error Message",
        dynamodb,
    )

    print("----- fetch evaluations by primary key -----")
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#1", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Success#2", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#3", dynamodb))
    print(fetch_evaluation_by_primary_key("Match#1", "Team#1", "Failed#1#4", dynamodb))
