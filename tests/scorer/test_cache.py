import pytest

from opthub_runner.scorer.cache import Cache, Trial


def test_cache() -> None:
    cache = Cache()

    with pytest.raises(ValueError, match="No file loaded."):
        cache.append(
            Trial({"TrialNo": "1", "Objective": 0.1, "Constraint": None, "Info": {}, "Score": 0.1, "Feasible": True}),
        )

    cache.load("Match#1#Team#1")
    values_of_cache1 = [
        Trial({"TrialNo": "1", "Objective": 0.1, "Constraint": None, "Info": {}, "Score": 0.1, "Feasible": True}),
        Trial({"TrialNo": "2", "Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2, "Feasible": False}),
        Trial({"TrialNo": "3", "Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3, "Feasible": None}),
    ]
    values_of_cache2 = [
        Trial({"TrialNo": "1", "Objective": 1.0, "Constraint": None, "Info": {}, "Score": 1.0, "Feasible": None}),
    ]
    cache.append(
        Trial({"TrialNo": "1", "Objective": 0.1, "Constraint": None, "Info": {}, "Score": 0.1, "Feasible": True}),
    )
    cache.append(
        Trial({"TrialNo": "2", "Objective": 0.2, "Constraint": None, "Info": {}, "Score": 0.2, "Feasible": False}),
    )
    cache.append(
        Trial({"TrialNo": "3", "Objective": 0.3, "Constraint": None, "Info": {}, "Score": 0.3, "Feasible": None}),
    )
    cache.load("Match#1#Team#2")
    cache.append(
        Trial({"TrialNo": "1", "Objective": 1.0, "Constraint": None, "Info": {}, "Score": 1.0, "Feasible": None}),
    )
    cache.load("Match#1#Team#1")

    if cache.get_values() != values_of_cache1:
        msg = "cache.get_values() != values_of_cache1"
        raise ValueError(msg)
    cache.load("Match#1#Team#2")
    if cache.get_values() != values_of_cache2:
        msg = "cache.get_values() != values_of_cache2"
        raise ValueError(msg)

    cache.clear()

    with pytest.raises(ValueError, match="No file loaded."):
        cache.get_values()
    with pytest.raises(ValueError, match="No file loaded."):
        cache.append(
            Trial({"TrialNo": "1", "Objective": 0.1, "Constraint": None, "Info": {}, "Score": 0.1, "Feasible": True}),
        )

    cache.load("Match#1#Team#1")
    if cache.get_values() != values_of_cache1:
        msg = "cache.get_values() != values_of_cache1"
        raise ValueError(msg)
