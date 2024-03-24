"""This module provides functions to save and fetch solutions to and from DynamoDB."""

from typing import TypedDict, cast

from opthub_runner.lib.converter import decimal_to_float
from opthub_runner.lib.dynamodb import DynamoDB, PrimaryKey


class Solution(TypedDict):
    """The solution data."""

    variable: object


def fetch_solution_by_primary_key(
    match_id: str,
    participant_id: str,
    trial: str,
    dynamodb: DynamoDB,
) -> Solution | None:
    """Fetch the solution by the primary key.

    Args:
        match_id (str): The match ID.
        participant_id (str): The participant ID.
        trial (str): The zero-filled trial  number.
        dynamodb (DynamoDB): The DynamoDB instance.

    Returns:
        Solution | None: The solution if it exists, otherwise None.
    """
    primary_key: PrimaryKey = {"ID": f"Solutions#{match_id}#{participant_id}", "Trial": trial}
    solution = cast(Solution | None, dynamodb.get_item(primary_key))

    if solution is None:
        return None

    # Decimal can not be used for evaluation, so convert it to float.
    return {
        "variable": decimal_to_float(solution["Variable"]),
    }
