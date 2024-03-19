from typing import Any, Dict, List, Optional, TypedDict, TypeVar

import boto3
from boto3.dynamodb.conditions import Key


# Primary key for Dynamo DB.
class PrimaryKey(TypedDict):
    """This class represents the primary key for Dynamo DB."""

    ID: str
    Trial: str


class DynamoDB:
    """The wrapper class for interaction with Amazon DynamoDB."""

    def __init__(
        self,
        endpoint_url: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        table_name: str,
    ) -> None:
        """
        Parameters
        ----------
        endpoint_url: str
            DynamoDBへの接続先URL．
        region_name: str
            サービスがデプロイされるリージョン．
        aws_access_key_id: str
            AWSアカウントのアクセスキーID．
        aws_secret_access_key: str
            AWSアクセスキーIDに対応する秘密アクセスキー．
        table_name: str
            テーブル名．

        """
        self.dynamoDB = boto3.resource(
            service_name="dynamodb",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.table_name = table_name
        self.table = self.dynamoDB.Table(self.table_name)

    def get_item(self, primary_key_value: PrimaryKey) -> dict[str, Any] | None:
        """
        Primary Keyを使ってDynamo DBからitemを取得．対応するitemがなければNoneを返す．

        Parameter
        ---------
        primary_key_value : dict[str, str]
            Primary KeyとそのValue．

        Return
        ------
        item : Dict[str, Any] | None
            取得したitem．

        """
        item: dict[str, Any] | None = self.table.get_item(Key=primary_key_value).get("Item")
        return item

    def put_item(self, item: dict[str, Any]) -> None:
        """
        Dynamo DBにitemを保存．

        Parameter
        ---------
        item : Dict[str, Any]
            Dynamo DBに保存するitem．

        """
        self.table.put_item(Item=item)

    def get_item_between_least_and_greatest(
        self, partition_key_value: Dict[str, str], sort_key: str, least: str, greatest: str, *attributes: str
    ) -> List[Dict[str, Any]]:
        """
        Partition Keyがpartition_key_valueであるitemのうち，least <= (Sort KeyのValue) <= greatestであるitemをDynamo DBから複数まとめて取得．

        Parameters
        ----------
        partition_key_value: Dict[str, str]
            Partition Key．
        sort_key: str
            Sort Key．
        least: str
            Sort KeyのValueの下限．
        greatest: str
            Sort KeyのValueの上限．
        attributes : tuple[str, ...]
            取得してくる属性(個数は任意)．値を渡さなければ，全ての属性を取ってくる．

        Return
        ------
        items : List[Dict[str, Any]] | None
            取得したitemのlist．

        """
        partition_key, value_of_partition_key = partition_key_value.popitem()

        if not attributes:
            # 属性の指定がなく全部取ってくるパターン．
            response = self.table.query(
                KeyConditionExpression=Key(partition_key).eq(value_of_partition_key)
                & Key(sort_key).between(least, greatest),
            )
        else:
            # 指定された属性のみ取ってくるパターン．
            response = self.table.query(
                KeyConditionExpression=Key(partition_key).eq(value_of_partition_key)
                & Key(sort_key).between(least, greatest),
                ProjectionExpression=",".join([f"#attr{i}" for i in range(len(attributes))]),
                ExpressionAttributeNames={f"#attr{i}": attr for i, attr in enumerate(attributes)},
            )
        items: list[dict[str, Any]] = response["Items"]

        return items


def main() -> None:
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


if __name__ == "__main__":
    main()
