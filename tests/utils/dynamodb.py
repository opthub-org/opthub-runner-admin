def test() -> None:
    dynamodb = DynamoDB(
        "http://localhost:8000",
        "localhost",
        "aaaaa",
        "aaaaa",
        "opthub-dynamodb-participant-trials-dev",
    )

    for i in range(1, 11):
        put_item = {
            "ID": "Solutions#Match#10#Team#10",
            "Trial": str(i).zfill(2),
            "ParticipantID": "Team#10",
            "Variable": [1, 2],
            "UserID": "User#1",
            "MatchID": "Match#10",
            "CreatedAt": f"2024-01-05-00:{str(i).zfill(2)}:00",
            "ResourceType": "Solutions",
            "TrialNo": str(i).zfill(2),
        }

        print("----- put item -----")
        dynamodb.put_item(put_item)
        print(put_item)

    primary_key: PrimaryKey = {"ID": "Solutions#Match#10#Team#10", "Trial": "03"}
    print("----- get item -----")
    got_item = dynamodb.get_item(primary_key)
    print(got_item)

    print("----- get items -----")
    items = dynamodb.get_item_between_least_and_greatest(
        {"ID": "Solutions#Match#10#Team#10"}, "Trial", "02", "08", "TrialNo", "Variable", "UserID", "MatchID"
    )
    print(items)
