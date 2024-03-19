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
    """
    GraphQL経由でMatchを取得し，Evaluationに必要なProblemの情報を取得する関数．

    Parameters
    ----------
    match_id : str
        取得するMatchのid．

    Returns
    -------
    problem_data : dict
        Problemの情報（ProblemDockerImageとProblemEnvironments）を格納したdict．

    """
    return {
        "docker_image": "opthub/sphere:latest",
        "environments": {"SPHERE_OPTIMA": "[[1, 1, 1], [1.5, 1.5, 1.5]]"},
    }


def fetch_match_indicator_by_id(match_id: str) -> MatchIndicator:
    """
    GraphQL経由でMatchを取得し，Scoreに必要なIndicatorの情報を取得する関数．

    Parameters
    ----------
    match_id : str
        取得するMatchのid．

    Returns
    -------
    indicator_data : dict
        Indicatorの情報（IndicatorDockerImageとIndicatorEnvironments）を格納したdict．

    """
    return {
        "docker_image": "opthub/hypervolume:latest",
        "environments": {"HV_REF_POINT": "[1, 1]"},
    }
