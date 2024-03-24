from opthub_runner.lib.cache import Cache
from opthub_runner.lib.converter import number_to_decimal
from opthub_runner.lib.dynamodb import DynamoDB


def test() -> None:
    cache = Cache()
    dynamodb = DynamoDB(
        "http://localhost:8000", "localhost", "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev"
    )

    for i in range(1, 11):
        put_item_evaluation = {
            "ID": "Evaluations#Match#1#Team#1",
            "Trial": f"Success#{str(i).zfill(4)}",
            "TrialNo": str(i).zfill(4),
            "ResourceType": "Evaluation",
            "MatchID": "Match#1",
            "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
            "ParticipantID": "Team#1",
            "StartedAt": f"2024-2-29-15:0{i}:00",
            "FinishedAt": f"2024-2-29-15:0{i}:30",
            "Status": "Success",
            "Objective": [i, i],
            "Constraint": None,
            "Info": None,
            "Feasible": None,
        }
        put_item_score = {
            "ID": "Scores#Match#1#Team#1",
            "Trial": f"Success#{str(i).zfill(4)}",
            "TrialNo": str(i).zfill(4),
            "ResourceType": "Score",
            "MatchID": "Match#1",
            "CreatedAt": f"2024-3-29-15:0{i - 1}:00",
            "ParticipantID": "Team#1",
            "StartedAt": f"2024-3-29-15:0{i}:00",
            "FinishedAt": f"2024-3-29-15:0{i}:30",
            "Status": "Success",
            "Score": number_to_decimal(i / 10),
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)
        put_item_evaluation = {
            "ID": "Evaluations#Match#1#Team#2",
            "Trial": f"Success#{str(i).zfill(4)}",
            "TrialNo": str(i).zfill(4),
            "ResourceType": "Evaluation",
            "MatchID": "Match#1",
            "CreatedAt": f"2024-2-29-15:0{i - 1}:00",
            "ParticipantID": "Team#2",
            "StartedAt": f"2024-2-29-15:0{i}:00",
            "FinishedAt": f"2024-2-29-15:0{i}:30",
            "Status": "Success",
            "Objective": [i, i],
            "Constraint": None,
            "Info": None,
            "Feasible": None,
        }
        put_item_score = {
            "ID": "Scores#Match#1#Team#2",
            "Trial": f"Success#{str(i).zfill(4)}",
            "TrialNo": str(i).zfill(4),
            "ResourceType": "Score",
            "MatchID": "Match#1",
            "CreatedAt": f"2024-3-29-15:0{i - 1}:00",
            "ParticipantID": "Team#2",
            "StartedAt": f"2024-3-29-15:0{i}:00",
            "FinishedAt": f"2024-3-29-15:0{i}:30",
            "Status": "Success",
            "Score": number_to_decimal(i / 100),
        }
        dynamodb.put_item(put_item_evaluation)
        dynamodb.put_item(put_item_score)
    print("----- history (TrialNo = 1, Team#1) -----")
    history = make_history("Match#1", "Team#1", "0001", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 8, Team#1) -----")
    history = make_history("Match#1", "Team#1", "0008", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- write (TrialNo = 9, Team#1) -----")
    write_to_cache("Match#1", "Team#1", "0009", [9, 9], None, None, number_to_decimal(9 / 10), cache)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 10, Team#2) -----")
    history = make_history("Match#1", "Team#2", "0010", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 3, Team#1) -----")
    history = make_history("Match#1", "Team#1", "0003", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
    print("----- history (TrialNo = 5, Team#2) -----")
    history = make_history("Match#1", "Team#2", "0005", cache, dynamodb)
    print(history)
    print("----- cache -----")
    print(cache.get_values())
