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


def fetch_match_by_id(id: str) -> Match:
    """Fetch the match by GraphQL.

    Args:
        id (str): The id of the match.

    Returns:
        Match: The fetched match.
    """
    return {
        "id": "Match#dcc32372-f02d-19c7-866d-f9742d5372ca",
        "indicator_docker_image": "opthub/best:latest",
        "indicator_environments": {},
        "problem_docker_image": "opthub/sphere:latest",
        "problem_environments": {"SPHERE_OPTIMA": "[[1.5, 1.5, 1.5]]"},
    }
