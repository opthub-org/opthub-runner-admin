from decimal import Decimal
from typing import Literal, TypedDict


class SuccessEvaluationSchema(TypedDict):
    """The type of the success evaluation."""

    ID: str
    Trial: str
    TrialNo: int
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
    TrialNo: int
    ResourceType: Literal["Evaluation"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Failed"]
    ErrorMessage: str


class SuccessScoreSchema(TypedDict):
    """The type of the success score."""

    ID: str
    Trial: str
    TrialNo: int
    ResourceType: Literal["Score"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Success"]
    Score: Decimal


class FailedScoreSchema(TypedDict):
    """The type of the failed score."""

    ID: str
    Trial: str
    TrialNo: int
    ResourceType: Literal["Score"]
    MatchID: str
    CreatedAt: str
    ParticipantID: str
    StartedAt: str
    FinishedAt: str
    Status: Literal["Failed"]
    ErrorMessage: str


Schema = SuccessEvaluationSchema | FailedEvaluationSchema | SuccessScoreSchema | FailedScoreSchema
