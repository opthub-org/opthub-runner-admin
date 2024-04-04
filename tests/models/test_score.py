from datetime import datetime
from typing import cast

from opthub_runner.keys import ACCESS_KEY_ID, REGION_NAME, SECRET_ACCESS_KEY, TABLE_NAME
from opthub_runner.lib.dynamodb import DynamoDB
from opthub_runner.models.schema import FailedScoreSchema, SuccessScoreSchema
from opthub_runner.models.score import save_failed_score, save_success_score


def test() -> None:
    dynamodb = DynamoDB(
        {
            "aws_access_key_id": ACCESS_KEY_ID,
            "aws_secret_access_key": SECRET_ACCESS_KEY,
            "region_name": REGION_NAME,
            "table_name": TABLE_NAME,
        },
    )
    save_failed_score(
        dynamodb,
        {
            "trial_no": "00001",
            "match_id": "Match#1",
            "participant_id": "Team#1",
            "started_at": datetime.now().isoformat(),
            "finished_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "error_message": "TestErrorMessage",
        },
    )

    for i in range(1, 3):
        save_success_score(
            dynamodb,
            {
                "trial_no": f"0000{i}",
                "match_id": "Match#1",
                "participant_id": "Team#1",
                "started_at": datetime.now().isoformat(),
                "finished_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "score": i / 10,
            },
        )

    for i in range(1, 3):
        success_item = cast(
            SuccessScoreSchema,
            dynamodb.get_item({"ID": "Scores#Match#1#Team#1", "Trial": f"Success#0000{i}"}),
        )
        if float(success_item["Score"]) != i / 10:
            msg = "Failed in saving score."
            raise ValueError(msg)

    failed_item = cast(FailedScoreSchema, dynamodb.get_item({"ID": "Scores#Match#1#Team#1", "Trial": "Failed#00001"}))
    if failed_item["ErrorMessage"] != "TestErrorMessage":
        msg = "Failed in saving score."
        raise ValueError(msg)
