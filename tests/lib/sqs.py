def test() -> None:
    from opthub_runner.keys import ACCESS_KEY_ID, QUEUE_URL, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
    from opthub_runner.lib.dynamodb import DynamoDB

    dynamodb = DynamoDB(REGION_NAME, ACCESS_KEY_ID, SECRET_ACCESS_KEY, TABLE_NAME)
    sqs = SQS(REGION_NAME, 2.0)

    response = sqs.sqs.purge_queue(QueueUrl=sqs.queue_url)
    print(response)

    for i in range(1, 3):
        put_item = {
            "ID": "Solutions#Match#1#Team#1",
            "Trial": str(i).zfill(2),
            "ParticipantID": "Team#1",
            "Variable": [1, 2],
            "UserID": "User#1",
            "MatchID": "Match#1",
            "CreatedAt": f"2024-03-05-00:{str(i).zfill(2)}:00",
            "ResourceType": "Solutions",
            "TrialNo": str(i).zfill(2),
        }
        dynamodb.put_item(put_item)

    message = sqs.polling_sqs_message()

    print(message)

    sqs.delete_sqs_message()

    message = sqs.polling_sqs_message()

    print(message)

    sqs.delete_sqs_message()


if __name__ == "__main__":
    main()
