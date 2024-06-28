"""This module provides functions to save and fetch solutions to and from DynamoDB."""

from typing import TypedDict, cast

from opthub_runner_admin.lib.dynamodb import DynamoDB, PrimaryKey
from opthub_runner_admin.models.schema import SolutionSchema
from opthub_runner_admin.utils.converter import decimal_to_float


class Solution(TypedDict):
    """The solution data.

    variable (object): The variable of the solution.
    """

    variable: object


def fetch_solution_by_primary_key(
    dynamodb: DynamoDB,
    match_id: str,
    participant_id: str,
    trial_no: str,
) -> Solution:
    """Fetch the solution by the primary key.

    Args:
        match_id (str): The match ID.
        participant_id (str): The participant ID.
        trial_no (str): The zero-filled trial number.
        dynamodb (DynamoDB): The DynamoDB instance.

    Returns:
        Solution | None: The solution if it exists, otherwise None.
    """
    primary_key: PrimaryKey = {"ID": f"Solutions#{match_id}#{participant_id}", "Trial": trial_no}
    solution = cast(SolutionSchema | None, dynamodb.get_item(primary_key))

    if solution is None:
        msg = "Solution not found"
        raise ValueError(msg)

    # Decimal can not be used for evaluation, so convert it to float.
    return {
        "variable": decimal_to_float(solution["Variable"]),
    }
