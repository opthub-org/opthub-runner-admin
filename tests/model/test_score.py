from opthub_runner.model import save_failed_score, save_success_score
from opthub_runner.lib.dynamodb import DynamoDB


def test():
    dynamodb = DynamoDB(
        "http://localhost:8000", "localhost", "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev"
    )

    save_success_score(
        "Match#1", "Team#1", "1", "2020-2-20-09:00:00", "2020-2-25-09:00:00", "2020-2-25-12:00:00", 0.8, dynamodb
    )
    save_success_score(
        "Match#1", "Team#1", "2", "2020-2-21-09:00:00", "2020-2-26-09:00:00", "2020-2-26-12:00:00", 0.2, dynamodb
    )
    save_success_score(
        "Match#1", "Team#2", "1", "2020-2-20-09:00:00", "2020-2-25-09:00:00", "2020-2-25-12:00:00", 0.4, dynamodb
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-09:00:00",
        "2020-2-25-09:00:00",
        "2020-2-25-12:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-13:00:00",
        "2020-2-25-14:00:00",
        "2020-2-25-15:00:00",
        "Error Message",
        dynamodb,
    )
    save_failed_score(
        "Match#1",
        "Team#1",
        "1",
        "2020-2-20-16:00:00",
        "2020-2-25-17:00:00",
        "2020-2-25-18:00:00",
        "Error Message",
        dynamodb,
    )


if __name__ == "__main__":
    main()
