"""This module provides functions to fetch match problems and indicators by GraphQL."""

from typing import TypedDict


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


def fetch_match_by_alias(alias: str) -> Match:
    """Fetch the match by GraphQL.

    Args:
        alias (str): The id of the match.

    Returns:
        Match: The fetched match.
    """
    return {
        "id": "1",
        "indicator_docker_image": "opthub/hypervolume:latest",
        "indicator_environments": {"HV_REF_POINT": "[1, 1]"},
        "problem_docker_image": "opthub/sphere:latest",
        "problem_environments": {"SPHERE_OPTIMA": "[[1, 1, 1], [1.5, 1.5, 1.5]]"},
    }
