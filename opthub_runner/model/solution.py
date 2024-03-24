"""
Solutionの取得

"""

from typing import TypedDict, cast

from opthub_runner.lib.converter import decimal_to_float
from opthub_runner.lib.dynamodb import DynamoDB, PrimaryKey


class Solution(TypedDict):
    Variable: object


def fetch_solution_by_primary_key(
    match_id: str,
    participant_id: str,
    trial: str,
    dynamodb: DynamoDB,
) -> Solution | None:
    """
    Primary Keyを使ってDynamo DBからSolutionを取ってくる関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial : str
        Trial．
    dynamodb : DynamoDB
        dynamo DBと通信するためのラッパークラスのオブジェクト．

    Return
    ------
    solution : dict
        取ってきたSolution．
    """
    primary_key: PrimaryKey = {"ID": f"Solutions#{match_id}#{participant_id}", "Trial": trial}
    solution = cast(Solution | None, dynamodb.get_item(primary_key))

    if solution is None:
        return None

    # Decimal can not be used for evaluation, so convert it to float.
    solution["Variable"] = decimal_to_float(solution["Variable"])

    return solution
