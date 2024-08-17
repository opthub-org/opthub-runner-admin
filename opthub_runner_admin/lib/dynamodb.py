"""This module provides a wrapper class for Amazon DynamoDB."""

import logging
from typing import Any, TypedDict, cast

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import BotoCoreError

from opthub_runner_admin.models.schema import Schema

LOGGER = logging.getLogger(__name__)


class PrimaryKey(TypedDict):
    """This class represents the primary key."""

    ID: str
    Trial: str


class DynamoDBOptions(TypedDict):
    """The options for DynamoDB."""

    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    table_name: str


class DynamoDB:
    """This class provides a wrapper for Amazon DynamoDB."""

    def __init__(
        self,
        options: DynamoDBOptions,
    ) -> None:
        """Initialize the class.

        Args:
            options (DynamoDBOptions): The options for DynamoDB.
        """
        self.dynamoDB = boto3.resource(
            service_name="dynamodb",
            region_name=options["region_name"],
            aws_access_key_id=options["aws_access_key_id"],
            aws_secret_access_key=options["aws_secret_access_key"],
        )
        self.table_name = options["table_name"]
        self.table = self.dynamoDB.Table(self.table_name)

    def check_accessible(self) -> None:
        """Check if the table is accessible."""
        try:
            self.table.get_item(Key={"ID": "dummyID", "Trial": "dummyTrial"})
        except Exception as e:
            msg = "Failed to access DynamoDB."
            LOGGER.exception(msg)
            raise Exception from e

    def get_item(self, primary_key_value: PrimaryKey) -> dict[str, Any] | None:
        """Get item from DynamoDB.

        Args:
            primary_key_value (PrimaryKey): The primary key value.

        Returns:
            Any | None: The item.
        """
        item: dict[str, Any] | None = self.table.get_item(Key=cast(dict[str, Any], primary_key_value)).get("Item")
        return item

    def put_item(self, item: Schema) -> None:
        """Put item to DynamoDB.

        Args:
            item (Schema): The item to put.
        """
        try:
            self.table.put_item(
                Item=cast(dict[str, Any], item),
                ConditionExpression=Attr("ID").not_exists() & Attr("Trial").not_exists(),
            )
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            LOGGER.warning("The item already exists.")
        except BotoCoreError as e:
            msg = "Failed to put item to DynamoDB."
            LOGGER.exception(msg)
            raise BotoCoreError from e

    def get_item_between_least_and_greatest(
        self,
        partition_key: str,
        least_trial: str,
        greatest_trial: str,
        attributes: list[str],
    ) -> list[Any]:
        """Get items from DynamoDB between least_trial and greatest_trial.

        Args:
            partition_key (str): The partition key.
            least_trial (str): The least trial.
            greatest_trial (str): The greatest trial.
            attributes (list[str]): The attributes to get.

        Returns:
            list[Any]: The items.
        """
        if not attributes:
            # get all attributes
            response = self.table.query(
                KeyConditionExpression=Key("ID").eq(partition_key) & Key("Trial").between(least_trial, greatest_trial),
            )
        else:
            # get specific attributes
            response = self.table.query(
                KeyConditionExpression=Key("ID").eq(partition_key) & Key("Trial").between(least_trial, greatest_trial),
                ProjectionExpression=",".join([f"#attr{i}" for i in range(len(attributes))]),
                ExpressionAttributeNames={f"#attr{i}": attr for i, attr in enumerate(attributes)},
            )
        items: list[dict[str, Any]] = response["Items"]

        return items
