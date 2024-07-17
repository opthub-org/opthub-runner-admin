"""This module provides the schema of the solution, evaluation, and score."""

from decimal import Decimal
from typing import Literal, TypedDict


class SolutionSchema(TypedDict):
    """The type of the solution."""

    ID: str
    Trial: str
    TrialNo: str
    ResourceType: Literal["Solution"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    UserID: str
    Variable: object


class SuccessEvaluationSchema(TypedDict):
    """The type of the success evaluation."""

    ID: str
    Trial: str
    TrialNo: str
    ResourceType: Literal["Evaluation"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Success"]
    Objective: object
    Constraint: object | None
    Info: object | None
    Feasible: bool | None


class FailedEvaluationSchema(TypedDict):
    """The type of the failed evaluation."""

    ID: str
    Trial: str
    TrialNo: str
    ResourceType: Literal["Evaluation"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Failed"]
    ErrorMessage: str
    AdminErrorMessage: str


class SuccessScoreSchema(TypedDict):
    """The type of the success score."""

    ID: str
    Trial: str
    TrialNo: str
    ResourceType: Literal["Score"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Success"]
    Value: Decimal


class FailedScoreSchema(TypedDict):
    """The type of the failed score."""

    ID: str
    Trial: str
    TrialNo: str
    ResourceType: Literal["Score"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Failed"]
    ErrorMessage: str
    AdminErrorMessage: str


Schema = SolutionSchema | SuccessEvaluationSchema | FailedEvaluationSchema | SuccessScoreSchema | FailedScoreSchema
