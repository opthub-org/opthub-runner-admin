"""This module provides functions to fetch match problems and indicators by GraphQL."""

from typing import TypedDict


class MatchProblem(TypedDict):
    """This class represents the match problem type."""

    docker_image: str
    environments: dict[str, str]


class MatchIndicator(TypedDict):
    """This class represents the indicator problem type."""

    docker_image: str
    environments: dict[str, str]


def fetch_match_problem_by_id(match_id: str) -> MatchProblem:
    """Fetch the problem of the match by GraphQL.

    Args:
        match_id (str): The id of the match.

    Returns:
        MatchProblem: The problem of the match.
    """
    return {
        "docker_image": "opthub/sphere:latest",
        "environments": {"SPHERE_OPTIMA": "[[1, 1, 1], [1.5, 1.5, 1.5]]"},
    }


def fetch_match_indicator_by_id(match_id: str) -> MatchIndicator:
    """Fetch the indicator of the match by GraphQL.

    Args:
        match_id (str): The id of the match.

    Returns:
        MatchIndicator: The indicator of the match.
    """
    return {
        "docker_image": "opthub/hypervolume:latest",
        "environments": {"HV_REF_POINT": "[1, 1]"},
    }
