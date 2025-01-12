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
    IgnoreStream: Literal[False]


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
    IgnoreStream: Literal[False]


class FlagEvaluationSchema(TypedDict):
    """The type of the flag evaluation."""

    ID: str
    Trial: str
    IgnoreStream: Literal[True]


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
    IgnoreStream: Literal[False]


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
    IgnoreStream: Literal[False]


class FlagScoreSchema(TypedDict):
    """The type of the flag score."""

    ID: str
    Trial: str
    IgnoreStream: Literal[True]


Schema = SolutionSchema | SuccessEvaluationSchema | FailedEvaluationSchema | SuccessScoreSchema | FailedScoreSchema
FlagSchema = FlagEvaluationSchema | FlagScoreSchema
