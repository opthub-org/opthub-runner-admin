"""This module provides functions to fetch match problems and indicators by GraphQL."""

from typing import TypedDict

from opthub_runner_admin.lib.appsync import fetch_match_response_by_match_uuid


class Match(TypedDict):
    """This class represents the match problem type.

    id (str): MatchId.
    indicator_docker_image (str): The docker image of the indicator.
    indicator_environments (dict[str, str]): The environments of the indicator.
    problem_docker_image (str): The docker image of the problem.
    problem_environments (dict[str, str]): The environments of the problem.
    """

    id: str
    indicator_docker_image: str
    indicator_environments: dict[str, str]
    problem_docker_image: str
    problem_environments: dict[str, str]


def fetch_match_by_id(match_id: str) -> Match:
    """Fetch the match by GraphQL.

    Args:
        match_id (str): The id of the match.

    Returns:
        Match: The fetched match.
    """
    if not match_id.startswith("Match#"):
        msg = "The match_id should start with 'Match#'."
        raise ValueError(msg)

    match_uuid = match_id[6:]
    response = fetch_match_response_by_match_uuid(match_uuid)

    problem_environments: dict[str, str] = {}
    for public_keyvalue in response["problemPublicEnvironments"]:
        problem_environments[public_keyvalue["key"]] = public_keyvalue["value"]

    for private_keyvalue in response["problemPrivateEnvironments"]:
        if private_keyvalue["value"] is None:
            msg = "The private environment is None."
            raise ValueError(msg)
        problem_environments[private_keyvalue["key"]] = private_keyvalue["value"]

    indicator_environments = {}
    for public_keyvalue in response["indicatorPublicEnvironments"]:
        indicator_environments[public_keyvalue["key"]] = public_keyvalue["value"]

    for private_keyvalue in response["indicatorPrivateEnvironments"]:
        if private_keyvalue["value"] is None:
            msg = "The value of the private environment is None."
            raise ValueError(msg)
        indicator_environments[private_keyvalue["key"]] = private_keyvalue["value"]

    return {
        "id": match_id,
        "indicator_docker_image": response["indicator"]["dockerImage"],
        "indicator_environments": indicator_environments,
        "problem_docker_image": response["problem"]["dockerImage"],
        "problem_environments": problem_environments,
    }
