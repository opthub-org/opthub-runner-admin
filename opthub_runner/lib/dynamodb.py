from typing import Any, Dict, List, Literal, Optional, TypedDict, TypeVar

import boto3
from boto3.dynamodb.conditions import Key

from opthub_runner.lib.schema import Schema


# Primary key for Dynamo DB.
class PrimaryKey(TypedDict):
    """This class represents the primary key for Dynamo DB."""

    ID: str
    Trial: str


class DynamoDBOptions(TypedDict):
    """The options for DynamoDB."""

    endpoint_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    table_name: str


class DynamoDB:
    """The wrapper class for interaction with Amazon DynamoDB."""

    def __init__(
        self,
        options: DynamoDBOptions,
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
            endpoint_url=options["endpoint_url"],
            region_name=options["region_name"],
            aws_access_key_id=options["aws_access_key_id"],
            aws_secret_access_key=options["aws_secret_access_key"],
        )
        self.table_name = options["table_name"]
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

    def put_item(self, item: Schema) -> None:
        """
        Dynamo DBにitemを保存．

        Parameter
        ---------
        item : Dict[str, Any]
            Dynamo DBに保存するitem．

        """
        self.table.put_item(Item=item)

    def get_item_between_least_and_greatest(
        self,
        partition_key: str,
        least_trial_no: str,
        greatest_trial_no: str,
        *attributes: str,
    ) -> list[dict[str, Any]]:
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
        if not attributes:
            # 属性の指定がなく全部取ってくるパターン．
            response = self.table.query(
                KeyConditionExpression=Key("ID").eq(partition_key)
                & Key("Trial").between(least_trial_no, greatest_trial_no),
            )
        else:
            # 指定された属性のみ取ってくるパターン．
            response = self.table.query(
                KeyConditionExpression=Key("ID").eq(partition_key)
                & Key("Trial").between(least_trial_no, greatest_trial_no),
                ProjectionExpression=",".join([f"#attr{i}" for i in range(len(attributes))]),
                ExpressionAttributeNames={f"#attr{i}": attr for i, attr in enumerate(attributes)},
            )
        items: list[dict[str, Any]] = response["Items"]

        return items
